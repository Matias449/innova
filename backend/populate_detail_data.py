import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import Nino, AnotacionDesarrollo, RegistroAsistencia

ESTADOS_ASISTENCIA = ['Presente', 'Presente', 'Presente', 'Presente', 'Ausente', 'Atraso', 'Justificado']
NOTAS = [
    "Participa activamente en la ronda.",
    "Logró comer toda su colación sin ayuda.",
    "Hoy estuvo un poco retraído durante el juego libre.",
    "Comparte sus juguetes con los compañeros.",
    "Lloró al momento de separarse del apoderado, pero se calmó pronto.",
    "Reconoce los colores primarios.",
    "Ayudó a ordenar los materiales de arte.",
    "Mostró gran interés en el cuento de la tarde."
]
AUTORES = ["Educadora Pilar", "Tía Daniela", "Tía Constanza", "Educadora Camila"]

def populate_details():
    ninos = Nino.objects.all()
    today = date(2026, 4, 28)
    
    # Limpiamos primero por si acaso se corre varias veces
    AnotacionDesarrollo.objects.all().delete()
    RegistroAsistencia.objects.all().delete()
    
    print(f"Generando datos detallados para {ninos.count()} niños...")
    
    for nino in ninos:
        # Generar asistencia de los últimos 10 días hábiles
        for i in range(14):
            dia = today - timedelta(days=i)
            if dia.weekday() < 5: # Lunes a Viernes
                estado = random.choice(ESTADOS_ASISTENCIA)
                RegistroAsistencia.objects.create(
                    nino=nino,
                    fecha=dia,
                    estado=estado
                )
                
        # Generar 2 a 5 anotaciones aleatorias en el último mes
        num_anotaciones = random.randint(2, 5)
        fechas_usadas = set()
        for _ in range(num_anotaciones):
            dias_atras = random.randint(0, 30)
            fecha_nota = today - timedelta(days=dias_atras)
            if fecha_nota not in fechas_usadas:
                fechas_usadas.add(fecha_nota)
                AnotacionDesarrollo.objects.create(
                    nino=nino,
                    fecha=fecha_nota,
                    descripcion=random.choice(NOTAS),
                    autor=random.choice(AUTORES)
                )
                
        # Agregar datos médicos/familiares aleatorios
        if random.random() < 0.3:
            nino.alergias = random.choice(["Alergia al maní", "Alergia a la proteína de vaca", "Picadura de abejas"])
        if random.random() < 0.2:
            nino.enfermedades = random.choice(["Asma leve", "Soplo al corazón"])
        if random.random() < 0.2:
            nino.situacion_familiar = random.choice(["Padres separados recientemente", "Vive con los abuelos maternos", "Nuevo hermano en camino"])
            
        nino.save()
        
    print("¡Generación de datos de asistencia y anotaciones completada con éxito!")

if __name__ == '__main__':
    populate_details()
