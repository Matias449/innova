import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
import openpyxl
from .models import Nino, AnotacionDesarrollo, RegistroAsistencia, PlanificacionCurso

@csrf_exempt
def ninos_list_create(request):
    if request.method == 'GET':
        ninos = Nino.objects.all().order_by('-fecha_registro')
        data = []
        for n in ninos:
            data.append({
                'id': n.id,
                'nombres': n.nombres,
                'apellidos': n.apellidos,
                'rut': n.rut,
                'apoderado_principal': n.apoderado_principal,
                'fecha_nacimiento': n.fecha_nacimiento.isoformat() if n.fecha_nacimiento else None,
                'curso': n.curso,
                'observaciones': n.observaciones,
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            nuevo_nino = Nino.objects.create(
                nombres=data.get('nombres'),
                apellidos=data.get('apellidos'),
                rut=data.get('rut'),
                apoderado_principal=data.get('apoderado_principal'),
                fecha_nacimiento=data.get('fecha_nacimiento'),
                curso=data.get('curso'),
                observaciones=data.get('observaciones', '')
            )
            return JsonResponse({'id': nuevo_nino.id, 'mensaje': 'Niño creado exitosamente'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def nino_detail(request, nino_id):
    if request.method == 'GET':
        nino = get_object_or_404(Nino, id=nino_id)
        
        anotaciones = list(nino.anotaciones.all().values('id', 'fecha', 'descripcion', 'autor'))
        asistencias = list(nino.asistencias.all().values('id', 'fecha', 'estado'))
        
        data = {
            'id': nino.id,
            'nombres': nino.nombres,
            'apellidos': nino.apellidos,
            'rut': nino.rut,
            'apoderado_principal': nino.apoderado_principal,
            'fecha_nacimiento': nino.fecha_nacimiento.isoformat() if nino.fecha_nacimiento else None,
            'curso': nino.curso,
            'observaciones': nino.observaciones,
            'enfermedades': nino.enfermedades,
            'alergias': nino.alergias,
            'situacion_familiar': nino.situacion_familiar,
            'anotaciones': anotaciones,
            'asistencias': asistencias
        }
        return JsonResponse(data)

@csrf_exempt
def ninos_export_excel(request):
    if request.method == 'GET':
        ninos = Nino.objects.all().order_by('apellidos', 'nombres')
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Niños Registrados"
        
        # Header
        headers = ["Nombres", "Apellidos", "RUT", "Apoderado Principal", "Fecha Nacimiento", "Curso", "Observaciones"]
        ws.append(headers)
        
        # Data
        for n in ninos:
            ws.append([
                n.nombres,
                n.apellidos,
                n.rut,
                n.apoderado_principal,
                n.fecha_nacimiento.isoformat() if n.fecha_nacimiento else "",
                n.curso,
                n.observaciones
            ])
            
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="ninos.xlsx"'
        wb.save(response)
        return response

@csrf_exempt
def dashboard_asistencia(request):
    if request.method == 'GET':
        curso = request.GET.get('curso', 'Todos')
        intervalo = request.GET.get('intervalo', 'mensual')
        qs = RegistroAsistencia.objects.all()
        
        if curso != 'Todos':
            qs = qs.filter(nino__curso=curso)
            
        total_registros = qs.count()
        if total_registros == 0:
            return JsonResponse({'error': 'No hay registros'}, status=404)
            
        total_presentes = qs.filter(estado='Presente').count()
        total_ausentes = qs.filter(estado='Ausente').count()
        total_atrasos = qs.filter(estado='Atraso').count()
        
        tasa_global = round((total_presentes / total_registros) * 100, 1) if total_registros > 0 else 0
        
        # Agregación según intervalo
        if intervalo == 'semanal':
            stats = qs.annotate(period=TruncWeek('fecha')).values('period').annotate(
                total=Count('id'),
                presentes=Count('id', filter=Q(estado='Presente')),
                ausentes=Count('id', filter=Q(estado='Ausente'))
            ).order_by('period')
        elif intervalo == 'diario':
            stats = qs.annotate(period=TruncDay('fecha')).values('period').annotate(
                total=Count('id'),
                presentes=Count('id', filter=Q(estado='Presente')),
                ausentes=Count('id', filter=Q(estado='Ausente'))
            ).order_by('period')
        else: # mensual
            stats = qs.annotate(period=TruncMonth('fecha')).values('period').annotate(
                total=Count('id'),
                presentes=Count('id', filter=Q(estado='Presente')),
                ausentes=Count('id', filter=Q(estado='Ausente'))
            ).order_by('period')
        
        evolucion_labels = []
        evolucion_data = []
        evolucion_ausencias = []
        
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        for stat in stats:
            if stat['period']:
                if intervalo == 'semanal':
                    label = f"Sem {stat['period'].isocalendar()[1]} ({meses[stat['period'].month-1]})"
                elif intervalo == 'diario':
                    label = f"{stat['period'].day} {meses[stat['period'].month-1]}"
                else:
                    label = meses[stat['period'].month - 1]
                    
                tasa_periodo = round((stat['presentes'] / stat['total']) * 100, 1) if stat['total'] > 0 else 0
                
                evolucion_labels.append(label)
                evolucion_data.append(tasa_periodo)
                evolucion_ausencias.append(stat['ausentes'])
                
        cursos_disponibles = list(Nino.objects.values_list('curso', flat=True).distinct())
        
        data = {
            'tasa_global': tasa_global,
            'total_inasistencias': total_ausentes,
            'total_atrasos': total_atrasos,
            'evolucion': {
                'labels': evolucion_labels,
                'data': evolucion_data,
                'ausencias': evolucion_ausencias
            },
            'cursos_disponibles': cursos_disponibles
        }
        
        return JsonResponse(data)

@csrf_exempt
def aula_estudiantes(request):
    if request.method == 'GET':
        curso = request.GET.get('curso')
        if not curso:
            return JsonResponse({'error': 'Debe especificar un curso'}, status=400)
            
        ninos = Nino.objects.filter(curso=curso).order_by('apellidos', 'nombres')
        data = [{'id': n.id, 'nombres': n.nombres, 'apellidos': n.apellidos, 'rut': n.rut} for n in ninos]
        return JsonResponse(data, safe=False)

@csrf_exempt
def aula_asistencia_bulk(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fecha_str = data.get('fecha')
            registros = data.get('registros', [])
            
            if not fecha_str or not registros:
                return JsonResponse({'error': 'Faltan datos (fecha o registros)'}, status=400)
                
            fecha = timezone.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            nino_ids = [r['nino_id'] for r in registros]
            RegistroAsistencia.objects.filter(fecha=fecha, nino_id__in=nino_ids).delete()
            
            nuevos_registros = [
                RegistroAsistencia(nino_id=r['nino_id'], fecha=fecha, estado=r['estado'])
                for r in registros
            ]
            RegistroAsistencia.objects.bulk_create(nuevos_registros)
            
            return JsonResponse({'mensaje': 'Asistencia guardada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def aula_anotaciones(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            AnotacionDesarrollo.objects.create(
                nino_id=data.get('nino_id'),
                fecha=data.get('fecha'),
                descripcion=data.get('descripcion'),
                autor=data.get('autor', 'Educadora')
            )
            return JsonResponse({'mensaje': 'Anotación guardada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def aula_planificaciones(request):
    if request.method == 'GET':
        curso = request.GET.get('curso')
        fecha_str = request.GET.get('fecha')
        
        if not curso or not fecha_str:
            return JsonResponse({'error': 'Faltan parámetros curso o fecha'}, status=400)
            
        try:
            fecha = timezone.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            plan = PlanificacionCurso.objects.filter(curso=curso, fecha=fecha).first()
            if plan:
                return JsonResponse({'actividades': plan.actividades})
            return JsonResponse({'actividades': ''})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
            
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            curso = data.get('curso')
            fecha = data.get('fecha')
            actividades = data.get('actividades', '')
            
            plan, created = PlanificacionCurso.objects.update_or_create(
                curso=curso,
                fecha=fecha,
                defaults={'actividades': actividades}
            )
            return JsonResponse({'mensaje': 'Planificación guardada correctamente'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def finanzas_dashboard(request):
    if request.method == 'GET':
        # Datos simulados de Enero a Agosto (CLP)
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"]
        
        matriculas = [500000, 1500000, 12000000, 1500000, 500000, 200000, 100000, 250000]
        subsidios = [8000000, 8000000, 8500000, 8500000, 8500000, 8500000, 8500000, 8500000]
        
        sueldos = [6500000, 6500000, 7000000, 7000000, 7000000, 7000000, 7000000, 7000000]
        insumos = [500000, 800000, 2500000, 1200000, 1000000, 1500000, 1100000, 900000]
        imprevistos = [0, 0, 150000, 0, 800000, 0, 4500000, 0] # Ej: Julio hubo rotura de cañería
        
        datos = []
        for i in range(len(meses)):
            ingreso_total = matriculas[i] + subsidios[i]
            egreso_total = sueldos[i] + insumos[i] + imprevistos[i]
            balance = ingreso_total - egreso_total
            
            datos.append({
                'mes': meses[i],
                'matriculas': matriculas[i],
                'subsidios': subsidios[i],
                'ingreso_total': ingreso_total,
                'sueldos': sueldos[i],
                'insumos': insumos[i],
                'imprevistos': imprevistos[i],
                'egreso_total': egreso_total,
                'balance': balance
            })
            
        return JsonResponse(datos, safe=False)
