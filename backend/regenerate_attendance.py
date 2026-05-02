import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import Nino, RegistroAsistencia
import pandas as pd

def is_holiday(check_date):
    month = check_date.month
    day = check_date.day
    if month == 5 and day == 1: return True
    if month == 5 and day == 21: return True
    if month == 6 and day == 21: return True
    if month == 6 and day == 29: return True
    if month == 7 and day == 16: return True
    if month == 8 and day == 15: return True
    if month == 4 and day in [17, 18]: return True
    if month == 7 and 7 <= day <= 18: return True
    return False

def get_attendance_state(check_date):
    month = check_date.month
    probs = [0.88, 0.05, 0.04, 0.03]
    if month == 6:
        if 15 <= check_date.day <= 25:
            probs = [0.60, 0.25, 0.05, 0.10]
        else:
            probs = [0.75, 0.15, 0.05, 0.05]
    elif month == 7:
        probs = [0.80, 0.10, 0.05, 0.05]
    rand = random.random()
    if rand < probs[0]: return 'Presente'
    elif rand < probs[0] + probs[1]: return 'Ausente'
    elif rand < probs[0] + probs[1] + probs[2]: return 'Atraso'
    else: return 'Justificado'

RegistroAsistencia.objects.all().delete()
print("Registros de asistencia anteriores eliminados.")

ninos = list(Nino.objects.all())
print(f"Generando asistencia de Marzo a Agosto para {len(ninos)} niños...")

start_date = date(2025, 3, 3)
end_date = date(2025, 8, 29)
delta = timedelta(days=1)

current_date = start_date
registros_creados = 0
registros_bulk = []
batch_size = 5000

while current_date <= end_date:
    if current_date.weekday() < 5 and not is_holiday(current_date):
        for nino in ninos:
            estado = get_attendance_state(current_date)
            registros_bulk.append(RegistroAsistencia(
                nino=nino,
                fecha=current_date,
                estado=estado
            ))
            
            if len(registros_bulk) >= batch_size:
                RegistroAsistencia.objects.bulk_create(registros_bulk)
                registros_creados += len(registros_bulk)
                registros_bulk = []
                print(f"Insertados {registros_creados} registros...")
                
    current_date += delta
    
if registros_bulk:
    RegistroAsistencia.objects.bulk_create(registros_bulk)
    registros_creados += len(registros_bulk)
    
print(f"Total de registros de asistencia creados: {registros_creados}")

# Verify
data = RegistroAsistencia.objects.all().values('fecha')
df = pd.DataFrame(list(data))
df['fecha'] = pd.to_datetime(df['fecha'])
print(f"\nVerificación: fechas desde {df['fecha'].min()} a {df['fecha'].max()}")
print(f"Fechas únicas: {df['fecha'].nunique()}")
print(f"Semanas únicas: {df['fecha'].dt.isocalendar().week.nunique()}")
