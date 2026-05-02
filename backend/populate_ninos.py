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

# Addresses by quintil — lower quintiles tend to be peripheral communes
ADDRESSES_BY_QUINTIL = {
    1: [
        "Av. La Pintana 2340, La Pintana",
        "Pasaje Los Cóndores 145, Lo Espejo",
        "Calle El Manzano 88, Cerro Navia",
        "Av. Américo Vespucio 3210, El Bosque",
        "Pasaje Los Pinos 321, Pudahuel",
        "Calle Frontera 678, La Pintana",
        "Av. Pedro Aguirre Cerda 1102, Lo Espejo",
    ],
    2: [
        "Av. Vicuña Mackenna 4560, La Granja",
        "Calle Las Rosas 234, Renca",
        "Pasaje El Arrayán 77, Quilicura",
        "Av. Américo Vespucio 1890, Pudahuel",
        "Calle Los Aromos 456, San Bernardo",
        "Av. General Velásquez 3300, San Bernardo",
        "Calle Tarapacá 892, Renca",
    ],
    3: [
        "Av. Pajaritos 2100, Maipú",
        "Calle Los Quillayes 340, La Florida",
        "Av. Américo Vespucio 780, Maipú",
        "Calle Magnolias 123, Ñuñoa",
        "Av. Departamental 2760, La Florida",
        "Calle Los Cerezos 445, Peñalolén",
        "Av. José Arrieta 8800, Peñalolén",
    ],
    4: [
        "Av. Irarrázaval 2300, Ñuñoa",
        "Calle Santa Isabel 1234, Santiago Centro",
        "Av. Matta 890, San Miguel",
        "Calle Los Leones 560, Providencia",
        "Av. Macul 3100, Macul",
        "Calle Bilbao 1450, Providencia",
        "Av. Francisco Bilbao 2100, San Miguel",
    ],
    5: [
        "Av. El Bosque Norte 500, Las Condes",
        "Calle Isidora Goyenechea 3400, Las Condes",
        "Av. Vitacura 5200, Vitacura",
        "Calle El Golf 99, Las Condes",
        "Av. Alonso de Córdova 2800, Vitacura",
        "Calle Colón 5432, Las Condes",
    ],
}

# RSH quintil distribution for a JUNJI public preschool (low-income skewed)
QUINTIL_WEIGHTS = [0.30, 0.28, 0.22, 0.13, 0.07]  # Q1 most likely

# Situacion laboral weights: none/one/both full-time
LABORAL_OPTIONS = ['ninguno', 'uno', 'ambos']
# Lower quintiles less likely to have both parents employed full-time
LABORAL_WEIGHTS_BY_QUINTIL = {
    1: [0.35, 0.45, 0.20],
    2: [0.25, 0.48, 0.27],
    3: [0.18, 0.47, 0.35],
    4: [0.10, 0.42, 0.48],
    5: [0.05, 0.32, 0.63],
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
        rut_num = random.randint(26000000, 27500000)
        if rut_num not in generated_ruts:
            generated_ruts.add(rut_num)
            return format_rut(rut_num)

def pick_quintil():
    return random.choices([1, 2, 3, 4, 5], weights=QUINTIL_WEIGHTS)[0]

def pick_hermanos():
    # 0-4 siblings, weighted towards 0-2
    return random.choices([0, 1, 2, 3, 4], weights=[0.20, 0.35, 0.28, 0.12, 0.05])[0]

def populate():
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

            quintil = pick_quintil()
            direccion = random.choice(ADDRESSES_BY_QUINTIL[quintil])
            numero_hermanos = pick_hermanos()
            laboral_weights = LABORAL_WEIGHTS_BY_QUINTIL[quintil]
            situacion_laboral = random.choices(LABORAL_OPTIONS, weights=laboral_weights)[0]

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
                observaciones=observaciones,
                quintil_rsh=quintil,
                direccion=direccion,
                numero_hermanos=numero_hermanos,
                situacion_laboral_padres=situacion_laboral,
            )
        print(f"Curso {curso} generado con {num_students} niños.")

    print(f"Proceso completado. Total: {Nino.objects.count()} niños registrados.")

if __name__ == '__main__':
    populate()
