"""
Populates synthetic 2025 weather and disease data for the training period 2025-03-03 to 2025-08-29.
Weather follows realistic Santiago seasonal patterns.
Disease data mimics ISPCH RM Rinovirus/VRS surge pattern used in populate_attendance.py.
"""
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import RegistroMeteorologico, RegistroCasosRespiratorios

random.seed(42)

START = date(2025, 3, 3)
END = date(2025, 8, 29)


# ─── Santiago seasonal weather parameters by month ─────────────────────────
# (temp_max_mean, temp_min_mean, precip_monthly_mm, wind_max_mean)
WEATHER_BY_MONTH = {
    3:  (26.0, 13.0, 5.0,   25),   # March: late summer, hot/dry
    4:  (22.0, 10.0, 15.0,  22),   # April: autumn begins
    5:  (17.0,  7.0, 50.0,  20),   # May: cooler, some rain
    6:  (13.0,  4.5, 70.0,  22),   # June: cold, rainy
    7:  (11.5,  3.5, 80.0,  24),   # July: coldest, wettest
    8:  (14.0,  5.0, 45.0,  22),   # August: still cold, less rain
}

# WMO codes by month: clear/partly cloudy in summer; overcast/rain in winter
WMO_WEIGHTS = {
    3:  {0: 0.60, 1: 0.30, 2: 0.10},   # 0=clear, 1=partly, 2=overcast
    4:  {0: 0.40, 1: 0.35, 2: 0.25},
    5:  {0: 0.25, 1: 0.30, 2: 0.45},
    6:  {0: 0.15, 1: 0.25, 2: 0.60},
    7:  {0: 0.10, 1: 0.20, 2: 0.70},
    8:  {0: 0.20, 1: 0.30, 2: 0.50},
}

WMO_CODE_MAP = {0: 0, 1: 2, 2: 3}  # clear=0, partly=2, overcast=3


def days_in_month(year: int, month: int) -> int:
    from calendar import monthrange
    return monthrange(year, month)[1]


def populate_weather():
    RegistroMeteorologico.objects.filter(fecha__gte=START, fecha__lte=END).delete()

    current = START
    created = 0
    while current <= END:
        m = current.month
        params = WEATHER_BY_MONTH[m]
        dim = days_in_month(current.year, m)

        temp_max = round(params[0] + random.gauss(0, 1.5), 1)
        temp_min = round(params[1] + random.gauss(0, 1.0), 1)

        # Distribute monthly precip across days with realistic clustering
        daily_prob = params[2] / (dim * 3.0)  # rough daily probability of rain
        if random.random() < daily_prob * 3:
            precip = round(max(0, random.expovariate(1.0 / max(params[2] / 8, 1))), 1)
        else:
            precip = 0.0

        wmo_type = random.choices(
            list(WMO_WEIGHTS[m].keys()),
            weights=list(WMO_WEIGHTS[m].values())
        )[0]
        # If raining, override code
        if precip > 2:
            codigo = 61  # moderate rain
        elif precip > 0:
            codigo = 51  # drizzle
        else:
            codigo = WMO_CODE_MAP[wmo_type]

        viento = round(params[3] + random.gauss(0, 5), 1)
        viento = max(5, viento)

        RegistroMeteorologico.objects.create(
            fecha=current,
            temp_max=temp_max,
            temp_min=temp_min,
            precipitacion=precip,
            codigo_clima=codigo,
            viento_max=viento,
        )
        created += 1
        current += timedelta(days=1)

    print(f'Clima: {created} registros creados ({START} a {END})')


# ─── Disease data: RM weekly respiratory virus cases ────────────────────────
# SE09 (Mar 3) through SE35 (Aug 29)
# Baseline: ~30-60 cases. Surge in SE24-SE28 (mid-June to mid-July) peaking ~250

VIRUS_TYPES = [
    'Rinovirus',
    'VRS (Virus Respiratorio Sincicial)',
    'Influenza A',
    'Influenza B',
    'Metapneumovirus',
    'Parainfluenza',
]


def get_se_and_year(d: date):
    iso = d.isocalendar()
    return int(iso[1]), int(iso[0])


def disease_baseline(se: int, virus: str) -> int:
    """Baseline weekly RM cases by SE and virus type."""
    # Peak SE24-28 (roughly June 16 - July 19)
    if 24 <= se <= 28:
        surge_factor = 4.0 + 2.0 * (1 - abs(se - 26) / 2.0)  # peaks at SE26
    elif 22 <= se <= 30:
        surge_factor = 2.0
    else:
        surge_factor = 1.0

    bases = {
        'Rinovirus': 45,
        'VRS (Virus Respiratorio Sincicial)': 35,
        'Influenza A': 20,
        'Influenza B': 8,
        'Metapneumovirus': 12,
        'Parainfluenza': 10,
    }
    base = bases.get(virus, 15)
    cases = int(base * surge_factor * random.uniform(0.85, 1.15))
    return max(0, cases)


def populate_disease():
    RegistroCasosRespiratorios.objects.filter(anio=2025, semana_epidemiologica__gte=9).delete()

    current = START
    processed_weeks = set()
    created = 0

    while current <= END:
        se, year = get_se_and_year(current)
        if (se, year) not in processed_weeks:
            processed_weeks.add((se, year))
            for virus in VIRUS_TYPES:
                casos = disease_baseline(se, virus)
                RegistroCasosRespiratorios.objects.get_or_create(
                    semana_epidemiologica=se,
                    anio=year,
                    region='Región Metropolitana',
                    tipo_virus=virus,
                    defaults={
                        'casos_confirmados': casos,
                        'fecha_publicacion': current,
                    }
                )
                created += 1
        current += timedelta(days=1)

    print(f'Enfermedades: {created} registros creados ({len(processed_weeks)} semanas epidemiológicas)')


if __name__ == '__main__':
    print('Generando datos de contexto 2025...')
    populate_weather()
    populate_disease()
    print('Completado.')
