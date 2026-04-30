import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import Nino

NOMBRES_NINOS = ["Agustín", "Mateo", "Tomás", "Lucas", "Benjamín", "Vicente", "Maximiliano", "Joaquín", "Martín", "Facundo", "Diego", "Santiago", "Gaspar", "Emilio", "Julián"]
NOMBRES_NINAS = ["Isabella", "Sofía", "Emilia", "Josefa", "Florencia", "Agustina", "Martina", "Trinidad", "Amanda", "Julieta", "Maite", "Antonella", "Ignacia", "Isidora", "Catalina"]
APELLIDOS = ["González", "Muñoz", "Rojas", "Díaz", "Pérez", "Soto", "Contreras", "Silva", "Martínez", "Sepúlveda", "Morales", "Rodríguez", "López", "Fuentes", "Hernández", "Torres", "Araya", "Flores", "Espinoza", "Valenzuela", "Castillo", "Tapia", "Reyes", "Gutiérrez", "Castro", "Pizarro", "Álvarez", "Vásquez", "Sánchez", "Fernández", "Ramírez", "Carrasco", "Gómez", "Cortés", "Herrera", "Núñez", "Jara", "Vergara", "Rivera", "Figueroa", "Riquelme", "García", "Miranda", "Bravo", "Vera", "Molina", "Vega", "Campos", "Sandoval", "Orellana"]

APODERADOS_NOMBRES = ["Carlos", "María", "José", "Juan", "Luis", "Ana", "Pedro", "Jorge", "Margarita", "Rosa", "Daniel", "Claudia", "Patricia", "Andrea", "Carolina", "Francisco", "Víctor", "Manuel", "Camila", "Paulina"]

CURSOS = {
    "Medio Menor A": {"min_age_days": 2*365, "max_age_days": 3*365},
    "Medio Menor B": {"min_age_days": 2*365, "max_age_days": 3*365},
    "Medio Mayor A": {"min_age_days": 3*365, "max_age_days": 4*365},
    "Medio Mayor B": {"min_age_days": 3*365, "max_age_days": 4*365},
}

def dv(rut):
    s = 1
    m = 0
    for r in reversed(str(rut)):
        s = (s + int(r) * (9 - m % 6)) % 11
        m += 1
    return 'K' if s == 10 else str(s - 1)

def format_rut(rut_num):
    rut_str = str(rut_num)
    rut_str_formatted = ""
    for i, char in enumerate(reversed(rut_str)):
        if i > 0 and i % 3 == 0:
            rut_str_formatted = "." + rut_str_formatted
        rut_str_formatted = char + rut_str_formatted
    return f"{rut_str_formatted}-{dv(rut_num)}"

generated_ruts = set()

def generate_rut():
    while True:
        # Generar un rut razonable para un niño (nacido en ~2022-2024, el rut es aprox 26.xxx.xxx)
        rut_num = random.randint(26000000, 27500000)
        if rut_num not in generated_ruts:
            generated_ruts.add(rut_num)
            return format_rut(rut_num)

def populate():
    # Limpiamos los existentes para evitar mezclar y repetir
    Nino.objects.all().delete()
    print("Base de datos limpiada. Generando registros...")

    today = date(2026, 4, 28)

    for curso, age_range in CURSOS.items():
        num_students = random.randint(20, 25)
        for _ in range(num_students):
            is_boy = random.choice([True, False])
            nombres = random.choice(NOMBRES_NINOS) if is_boy else random.choice(NOMBRES_NINAS)
            apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
            rut = generate_rut()
            
            apoderado = f"{random.choice(APODERADOS_NOMBRES)} {apellidos.split(' ')[0]}"
            
            age_days = random.randint(age_range['min_age_days'], age_range['max_age_days'])
            fecha_nac = today - timedelta(days=age_days)
            
            observaciones = random.choice([
                "", "", "", "Alergia al maní.", "Intolerancia a la lactosa.", 
                "Requiere supervisión al comer.", "Muy participativo.", "En periodo de adaptación."
            ])

            Nino.objects.create(
                nombres=nombres,
                apellidos=apellidos,
                rut=rut,
                apoderado_principal=apoderado,
                fecha_nacimiento=fecha_nac,
                curso=curso,
                observaciones=observaciones
            )
        print(f"Curso {curso} generado con {num_students} niños.")

    print(f"¡Proceso completado! Total de niños registrados: {Nino.objects.count()}")

if __name__ == '__main__':
    populate()
