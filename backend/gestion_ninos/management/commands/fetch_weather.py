"""
Fetches daily weather data from Open-Meteo for the school's location in
Providencia, Santiago (lat=-33.4372, lon=-70.6506) and stores it in
RegistroMeteorologico. Run manually or via cron.

Usage:
    python manage.py fetch_weather                  # last 7 days
    python manage.py fetch_weather --days 30        # last 30 days
    python manage.py fetch_weather --start 2025-01-01 --end 2025-04-30
"""

import requests
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from gestion_ninos.models import PerfilInstitucional, RegistroMeteorologico

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARS = "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max,weather_code"


class Command(BaseCommand):
    help = "Fetch daily weather data from Open-Meteo and store in RegistroMeteorologico"

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7, help="Number of past days to fetch (default: 7)")
        parser.add_argument("--start", type=str, help="Start date YYYY-MM-DD")
        parser.add_argument("--end", type=str, help="End date YYYY-MM-DD")

    def handle(self, *args, **options):
        perfil, _ = PerfilInstitucional.objects.get_or_create(pk=1)
        lat, lon = perfil.lat, perfil.lng

        today = date.today()

        if options["start"] and options["end"]:
            start = date.fromisoformat(options["start"])
            end = date.fromisoformat(options["end"])
        else:
            end = today - timedelta(days=1)
            start = end - timedelta(days=options["days"] - 1)

        self.stdout.write(f"Fetching weather for {lat},{lon} from {start} to {end}...")

        # Use archive API for historical data, forecast for recent days
        yesterday = today - timedelta(days=1)
        archive_end = min(end, yesterday)

        records_created = 0
        records_skipped = 0

        if start <= archive_end:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start.isoformat(),
                "end_date": archive_end.isoformat(),
                "daily": DAILY_VARS,
                "timezone": "America/Santiago",
            }
            try:
                resp = requests.get(ARCHIVE_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                created, skipped = self._save_daily(data)
                records_created += created
                records_skipped += skipped
            except Exception as e:
                self.stderr.write(f"Archive API error: {e}")

        # If end >= today, also fetch forecast for today
        if end >= today:
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": DAILY_VARS,
                "forecast_days": 1,
                "timezone": "America/Santiago",
            }
            try:
                resp = requests.get(FORECAST_URL, params=params, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                created, skipped = self._save_daily(data)
                records_created += created
                records_skipped += skipped
            except Exception as e:
                self.stderr.write(f"Forecast API error: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created: {records_created}, Already existed: {records_skipped}"
        ))

    def _save_daily(self, data):
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("wind_speed_10m_max", [])
        codes = daily.get("weather_code", [])

        created = 0
        skipped = 0

        for i, fecha_str in enumerate(dates):
            fecha = date.fromisoformat(fecha_str)
            _, was_created = RegistroMeteorologico.objects.update_or_create(
                fecha=fecha,
                defaults={
                    "temp_max": temp_max[i] if i < len(temp_max) else None,
                    "temp_min": temp_min[i] if i < len(temp_min) else None,
                    "precipitacion": precip[i] if i < len(precip) else None,
                    "viento_max": wind[i] if i < len(wind) else None,
                    "codigo_clima": int(codes[i]) if i < len(codes) and codes[i] is not None else None,
                },
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        return created, skipped
