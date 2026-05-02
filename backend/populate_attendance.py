import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import Nino, RegistroAsistencia

def is_holiday(check_date):
    # Feriados aproximados y vacaciones de invierno (Julio) en 2025/2026
    month = check_date.month
    day = check_date.day
    
    # Feriados fijos aprox
    if month == 5 and day == 1: return True # Día del trabajo
    if month == 5 and day == 21: return True # Glorias Navales
    if month == 6 and day == 21: return True # Pueblos originarios
    if month == 6 and day == 29: return True # San Pedro y San Pablo
    if month == 7 and day == 16: return True # Virgen del Carmen
    if month == 8 and day == 15: return True # Asunción de la Virgen
    if month == 4 and day in [17, 18]: return True # Semana Santa (aprox)
    
    # Vacaciones de invierno (Aprox 2 semanas de Julio, ej. 7 al 18 de Julio)
    if month == 7 and 7 <= day <= 18:
        return True

    return False

def get_attendance_state(check_date, is_chronic=False):
    month = check_date.month
    
    # Probabilidades base (Presente, Ausente, Atraso, Justificado)
    if is_chronic:
        # Estudiantes crónicos: solo 60-65% presencia
        probs = [0.62, 0.20, 0.10, 0.08]
    else:
        probs = [0.88, 0.05, 0.04, 0.03]
    
    # Oleada de baja asistencia en Junio (virus respiratorios)
    if month == 6:
        # Tercera semana de junio: brote de virus
        if 15 <= check_date.day <= 25:
            if is_chronic:
                probs = [0.45, 0.35, 0.10, 0.10]
            else:
                probs = [0.60, 0.25, 0.05, 0.10]
        else:
            if is_chronic:
                probs = [0.55, 0.25, 0.10, 0.10]
            else:
                probs = [0.75, 0.15, 0.05, 0.05]
            
    # Julio (antes/despues de vacaciones) también baja
    elif month == 7:
        if is_chronic:
            probs = [0.60, 0.20, 0.10, 0.10]
        else:
            probs = [0.80, 0.10, 0.05, 0.05]
        
    rand = random.random()
    if rand < probs[0]: return 'Presente'
    elif rand < probs[0] + probs[1]: return 'Ausente'
    elif rand < probs[0] + probs[1] + probs[2]: return 'Atraso'
    else: return 'Justificado'

def populate_attendance():
    RegistroAsistencia.objects.all().delete()
    print("Registros de asistencia anteriores eliminados.")
    
    ninos = list(Nino.objects.all())
    print(f"Generando asistencia de Marzo a Agosto para {len(ninos)} niños...")
    
    # Usaremos 2025 para tener un año completo y realista de marzo a agosto
    start_date = date(2025, 3, 3) # Lunes 3 de Marzo
    end_date = date(2025, 8, 29) # Viernes 29 de Agosto
    
    delta = timedelta(days=1)
    
    # Marcar primeros 10-15% de estudiantes como crónicos
    chronic_indices = set(range(len(ninos) // 8))  # ~12% serán crónicos
    
    current_date = start_date
    registros_creados = 0
    
    # Para optimizar, recolectaremos los objetos y haremos bulk_create
    registros_bulk = []
    batch_size = 5000
    
    while current_date <= end_date:
        if current_date.weekday() < 5 and not is_holiday(current_date): # Lunes a Viernes y no feriado
            for idx, nino in enumerate(ninos):
                is_chronic = idx in chronic_indices
                estado = get_attendance_state(current_date, is_chronic=is_chronic)
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
        
    print(f"¡Proceso completado! Total de registros de asistencia creados: {registros_creados}")
    print(f"Estudiantes crónicos: ~{len(chronic_indices)}")

if __name__ == '__main__':
    populate_attendance()
