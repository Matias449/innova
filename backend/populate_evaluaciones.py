import os
import django
import random
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from gestion_ninos.models import Nino, EvaluacionActividad

def populate_evaluaciones():
    # Obtener el curso actual o usar uno por defecto para poblar
    cursos = Nino.objects.values_list('curso', flat=True).distinct()
    
    if not cursos:
        print("No hay niños registrados en ningún curso. Por favor, poblar la base de datos de niños primero.")
        return

    fecha_hoy = date.today()
    estados = ['Logrado', 'En proceso', 'Necesita apoyo']
    
    # Probabilidades para que sea realista
    weights = [0.5, 0.3, 0.2] 

    total_creados = 0
    
    for curso in cursos:
        ninos_curso = Nino.objects.filter(curso=curso)
        for nino in ninos_curso:
            evaluacion_estado = random.choices(estados, weights=weights)[0]
            
            # Crear o actualizar evaluación para hoy
            obj, created = EvaluacionActividad.objects.update_or_create(
                nino=nino,
                fecha=fecha_hoy,
                defaults={'evaluacion': evaluacion_estado}
            )
            if created:
                total_creados += 1

    print(f"Población exitosa: Se crearon/actualizaron {total_creados} evaluaciones para la fecha {fecha_hoy}.")

if __name__ == '__main__':
    populate_evaluaciones()
