"""
Scrapes the ISPCH weekly respiratory virus bulletin PDF from
https://www.ispch.gob.cl/virusrespiratorios/ and stores confirmed case counts
in RegistroCasosRespiratorios.

Data extracted:
  - National totals by virus type (from executive summary, page 1)
  - Regional totals (aggregated from hospital table, page with "Tabla 2")
  - SARS-CoV-2 regional sequencing table (last page)

Usage:
    python manage.py fetch_enfermedades           # latest bulletin
    python manage.py fetch_enfermedades --all     # all bulletins on the page
    python manage.py fetch_enfermedades --url URL # direct PDF URL
"""

import io
import re
from datetime import date

import requests
import pdfplumber
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from gestion_ninos.models import RegistroCasosRespiratorios

BASE_URL = "https://www.ispch.gob.cl"
BULLETIN_PAGE = "https://www.ispch.gob.cl/virusrespiratorios/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Maps substrings in hospital/center names → canonical region name
HOSPITAL_REGION = {
    "arica": "Arica y Parinacota",
    "iris véliz": "Arica y Parinacota",
    "iris veliz": "Arica y Parinacota",
    "iquique": "Tarapacá",
    "alto hospicio": "Tarapacá",
    "cirujano aguirre": "Tarapacá",
    "antofagasta": "Antofagasta",
    "cesfam corvallis": "Antofagasta",
    "copiapó": "Atacama",
    "copiapo": "Atacama",
    "mellivobsky": "Atacama",
    "la serena": "Coquimbo",
    "sergio aguilar": "Coquimbo",
    "san felipe": "Valparaíso",
    "valparaíso": "Valparaíso",
    "valparaiso": "Valparaíso",
    "plaza justicia": "Valparaíso",
    "san antonio": "Valparaíso",
    "viña del mar": "Valparaíso",
    "vina del mar": "Valparaíso",
    "gómez carreño": "Valparaíso",
    "gomez carreno": "Valparaíso",
    "viña,": "Valparaíso",
    "r.m.": "Metropolitana",
    " rm ": "Metropolitana",
    "rancagua": "O'Higgins",
    "talca": "Maule",
    "curicó": "Maule",
    "curico": "Maule",
    "linares": "Maule",
    "concepción": "Biobío",
    "concepcion": "Biobío",
    "talcahuano": "Biobío",
    "chillán": "Ñuble",
    "chillan": "Ñuble",
    "temuco": "La Araucanía",
    "valdivia": "Los Ríos",
    "osorno": "Los Lagos",
    "puerto montt": "Los Lagos",
    "castro": "Los Lagos",
    "coyhaique": "Aysén",
    "aysen": "Aysén",
    "punta arenas": "Magallanes",
    "magallanes": "Magallanes",
}

VIRUS_COLUMNS = ["sars-cov-2", "vrs", "adv", "para", "inf a", "inf b", "meta", "rino", "ovr"]


class Command(BaseCommand):
    help = "Scrape ISPCH respiratory virus bulletin PDF and save case counts by region"

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true", help="Process all bulletin PDFs on the page")
        parser.add_argument("--url", type=str, help="Direct PDF URL to process")

    def handle(self, *args, **options):
        if options.get("url"):
            pdf_links = [options["url"]]
        else:
            pdf_links = self._find_bulletin_links()
            if not pdf_links:
                self.stderr.write("No bulletin PDFs found on the ISPCH page.")
                return
            if not options["all"]:
                pdf_links = pdf_links[:1]

        total_saved = 0
        for url in pdf_links:
            self.stdout.write(f"Processing: {url}")
            saved = self._process_pdf(url)
            total_saved += saved
            self.stdout.write(f"  Saved {saved} records")

        self.stdout.write(self.style.SUCCESS(f"Total: {total_saved} records saved"))

    def _find_bulletin_links(self):
        try:
            resp = requests.get(BULLETIN_PAGE, timeout=30, headers=HEADERS)
            resp.raise_for_status()
        except Exception as e:
            self.stderr.write(f"Could not fetch bulletin index: {e}")
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True).lower()
            # Weekly bulletins follow the pattern "Informe-circulacion-virus-respiratorios-SEXX-..."
            if ("informe-circulacion" in href.lower() or "descargar informe semana" in text) and href.lower().endswith(".pdf"):
                full = href if href.startswith("http") else BASE_URL + href
                if full not in links:
                    links.append(full)

        self.stdout.write(f"Found {len(links)} weekly bulletin(s)")
        return links

    def _process_pdf(self, url):
        # Support local file paths for testing
        if url.startswith("/") or url.startswith("file://"):
            path = url.replace("file://", "")
            try:
                with open(path, "rb") as f:
                    pdf_bytes = f.read()
            except Exception as e:
                self.stderr.write(f"  Could not read local file: {e}")
                return 0
        else:
            try:
                resp = requests.get(url, timeout=90, headers=HEADERS)
                resp.raise_for_status()
                pdf_bytes = resp.content
            except Exception as e:
                self.stderr.write(f"  Download failed: {e}")
                return 0

        # Extract SE and year from filename
        se, anio = self._parse_se_from_url(url)

        saved = 0
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                # Detect SE/year from page 1 text if not in URL
                page1_text = pdf.pages[0].extract_text() or ""
                if not se:
                    se, anio = self._parse_se_from_text(page1_text)

                if not se or not anio:
                    self.stderr.write(f"  Could not detect SE/year, skipping")
                    return 0

                self.stdout.write(f"  SE {se}/{anio}")

                # 1. National totals from executive summary text
                saved += self._save_national_totals(page1_text, se, anio)

                # 2. Regional aggregation from hospital tables
                saved += self._save_regional_from_tables(pdf, se, anio)

        except Exception as e:
            self.stderr.write(f"  PDF parse error: {e}")

        return saved

    def _parse_se_from_url(self, url):
        m = re.search(r"SE(\d{1,2})[-_](\d{2})-(\d{2})-(\d{4})", url, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(4))
        m = re.search(r"se[\-_]?(\d{1,2})[\-_].*?(\d{4})", url, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    def _parse_se_from_text(self, text):
        m = re.search(r"SE\s+(\d{1,2})\s+del\s+(\d{4})", text)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.search(r"Semana\s+Epidemiol[oó]gica\s+\(SE\)\s+(\d{1,2})\s+del\s+(\d{4})", text)
        if m:
            return int(m.group(1)), int(m.group(2))
        return None, None

    def _save_national_totals(self, text, se, anio):
        """Parse the bullet list of virus totals on page 1 and store as 'Nacional'."""
        # Pattern: "- Rinovirus: 698 (60,0%)"  or "Rinovirus: 698"
        virus_patterns = [
            ("Rinovirus", "Rinovirus"),
            ("Influenza A", "Influenza A"),
            ("Influenza B", "Influenza B"),
            ("Adenovirus", "Adenovirus"),
            ("Parainfluenza", "Parainfluenza"),
            (r"(?:VRS|Virus Respiratorio Sincicial)", "VRS"),
            ("SARS-CoV-2", "SARS-CoV-2"),
            ("Metapneumovirus", "Metapneumovirus"),
            (r"(?:OVR|otros virus respiratorios)", "OVR"),
        ]
        today = date.today()
        saved = 0
        for pattern, label in virus_patterns:
            m = re.search(rf"{pattern}[^:]*:\s*(\d+)", text, re.IGNORECASE)
            if m:
                casos = int(m.group(1))
                try:
                    RegistroCasosRespiratorios.objects.update_or_create(
                        semana_epidemiologica=se,
                        anio=anio,
                        region="Nacional",
                        tipo_virus=label,
                        defaults={"fecha_publicacion": today, "casos_confirmados": casos},
                    )
                    saved += 1
                except Exception:
                    pass
        return saved

    def _save_regional_from_tables(self, pdf, se, anio):
        """
        Find the main all-cases table (Tabla 2) that lists every hospital
        center with columns: total_casos, positivos, virus_positivos, …
        Only process that page to avoid double-counting from Tabla 3/4.
        Aggregate positives per region using HOSPITAL_REGION lookup.
        """
        today = date.today()
        region_totals = {}

        for page in pdf.pages:
            text = page.extract_text() or ""
            # Only Tabla 2 page (all cases). Skip Tabla 3 (hospitalized) and Tabla 4 (ambulatory).
            if "Tabla 2" not in text:
                continue
            if "Tabla 3" in text or "Tabla 4" in text:
                continue

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                region = self._line_to_region(line)
                if not region:
                    continue
                # Second numeric value = Nº casos positivos
                nums = re.findall(r"\d+", line)
                if len(nums) >= 2:
                    positivos = int(nums[1])
                    region_totals[region] = region_totals.get(region, 0) + positivos

        saved = 0
        for region, total in region_totals.items():
            try:
                RegistroCasosRespiratorios.objects.update_or_create(
                    semana_epidemiologica=se,
                    anio=anio,
                    region=region,
                    tipo_virus="Total positivos (todos los virus)",
                    defaults={"fecha_publicacion": today, "casos_confirmados": total},
                )
                saved += 1
            except Exception:
                pass
        return saved

    def _line_to_region(self, line):
        """Return canonical region name if the line contains a known hospital identifier."""
        lower = line.lower()
        for keyword, region in HOSPITAL_REGION.items():
            if keyword in lower:
                return region
        return None
