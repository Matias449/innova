import json
import requests as http_requests
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Max
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.utils import timezone
import openpyxl
from .models import Nino, AnotacionDesarrollo, RegistroAsistencia, PlanificacionCurso, PerfilInstitucional, PersonalInstitucional, RegistroMeteorologico, RegistroCasosRespiratorios

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
                observaciones=data.get('observaciones', ''),
                quintil_rsh=data.get('quintil_rsh') or None,
                direccion=data.get('direccion', ''),
                numero_hermanos=data.get('numero_hermanos') if data.get('numero_hermanos') is not None else None,
                situacion_laboral_padres=data.get('situacion_laboral_padres', ''),
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
            'telefono_apoderado': nino.telefono_apoderado,
            'fecha_nacimiento': nino.fecha_nacimiento.isoformat() if nino.fecha_nacimiento else None,
            'curso': nino.curso,
            'observaciones': nino.observaciones,
            'enfermedades': nino.enfermedades,
            'alergias': nino.alergias,
            'situacion_familiar': nino.situacion_familiar,
            'quintil_rsh': nino.quintil_rsh,
            'direccion': nino.direccion,
            'numero_hermanos': nino.numero_hermanos,
            'situacion_laboral_padres': nino.situacion_laboral_padres,
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
def aula_asistencia_dia(request):
    if request.method == 'GET':
        curso = request.GET.get('curso')
        fecha_str = request.GET.get('fecha')
        if not curso or not fecha_str:
            return JsonResponse({'error': 'Faltan parámetros curso o fecha'}, status=400)
        try:
            fecha = timezone.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            registros = RegistroAsistencia.objects.filter(
                nino__curso=curso, fecha=fecha
            ).select_related('nino').order_by('nino__apellidos', 'nino__nombres')
            data = [{
                'nino_id': r.nino.id,
                'nombres': r.nino.nombres,
                'apellidos': r.nino.apellidos,
                'estado': r.estado
            } for r in registros]
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def asistencia_por_curso(request):
    if request.method == 'GET':
        cursos = list(Nino.objects.values_list('curso', flat=True).distinct().order_by('curso'))
        result = []
        for curso in cursos:
            qs = RegistroAsistencia.objects.filter(nino__curso=curso)
            total = qs.count()
            if total == 0:
                continue
            presentes = qs.filter(estado='Presente').count()
            ausentes = qs.filter(estado='Ausente').count()
            atrasos = qs.filter(estado='Atraso').count()
            justificados = qs.filter(estado='Justificado').count()
            tasa = round((presentes / total) * 100, 1)
            result.append({
                'curso': curso,
                'total': total,
                'presentes': presentes,
                'ausentes': ausentes,
                'atrasos': atrasos,
                'justificados': justificados,
                'tasa_asistencia': tasa,
            })
        return JsonResponse(result, safe=False)

@csrf_exempt
def finanzas_dashboard(request):
    if request.method == 'GET':
        # Datos simulados Ene–Ago para jardín ~90 niños, 9 funcionarios (CLP)
        # Ene/Feb = verano (operación reducida); Mar = matrículas anuales + mensualidades; Abr–Ago = operación normal
        meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"]

        # Mensualidades + matrícula anual en Marzo ($120.000 x 90 niños)
        matriculas    = [2_100_000, 2_350_000, 15_240_000, 6_030_000, 5_940_000, 5_760_000, 5_620_000, 5_880_000]
        # Subsidio JUNJI: varía con asistencia; menor en verano por días hábiles reducidos
        subsidios     = [4_050_000, 4_620_000, 12_870_000, 13_230_000, 12_960_000, 12_390_000, 11_550_000, 12_780_000]
        # Remuneraciones: 1 directora, 4 educadoras, 2 técnicas, 1 administrativa, 1 auxiliar
        sueldos       = [10_350_000, 10_350_000, 11_100_000, 10_650_000, 10_650_000, 10_650_000, 10_650_000, 10_650_000]
        # Insumos: alimentación (~$2M/mes normal) + materiales + servicios básicos
        insumos       = [1_180_000, 1_090_000, 3_450_000, 2_620_000, 2_480_000, 2_710_000, 2_230_000, 2_590_000]
        # Imprevistos: mantención calefacción en invierno, reparaciones
        imprevistos   = [0, 0, 0, 0, 390_000, 0, 1_980_000, 0]
        
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


# ── Configuración: Perfil Institucional ──────────────────────────────────────

def _perfil_to_dict(p):
    return {
        'id': p.id,
        'nombre': p.nombre,
        'direccion': p.direccion,
        'comuna': p.comuna,
        'region': p.region,
        'lat': p.lat,
        'lng': p.lng,
        'telefono': p.telefono,
        'email': p.email,
    }

@csrf_exempt
def configuracion_perfil(request):
    perfil, _ = PerfilInstitucional.objects.get_or_create(pk=1)

    if request.method == 'GET':
        return JsonResponse(_perfil_to_dict(perfil))

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            for field in ('nombre', 'direccion', 'comuna', 'region', 'telefono', 'email'):
                if field in data:
                    setattr(perfil, field, data[field])
            if 'lat' in data:
                perfil.lat = float(data['lat'])
            if 'lng' in data:
                perfil.lng = float(data['lng'])
            perfil.save()
            return JsonResponse(_perfil_to_dict(perfil))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# ── Configuración: Personal Institucional ────────────────────────────────────

def _personal_to_dict(p):
    return {
        'id': p.id,
        'nombre': p.nombre,
        'cargo': p.cargo,
        'email': p.email,
        'telefono': p.telefono,
        'fecha_ingreso': p.fecha_ingreso.isoformat() if p.fecha_ingreso else None,
    }

@csrf_exempt
def configuracion_personal(request):
    if request.method == 'GET':
        personal = PersonalInstitucional.objects.all()
        return JsonResponse([_personal_to_dict(p) for p in personal], safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            miembro = PersonalInstitucional.objects.create(
                nombre=data.get('nombre', ''),
                cargo=data.get('cargo', ''),
                email=data.get('email') or None,
                telefono=data.get('telefono') or None,
                fecha_ingreso=data.get('fecha_ingreso') or None,
            )
            return JsonResponse(_personal_to_dict(miembro), status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def configuracion_personal_detail(request, personal_id):
    try:
        miembro = PersonalInstitucional.objects.get(pk=personal_id)
    except PersonalInstitucional.DoesNotExist:
        return JsonResponse({'error': 'No encontrado'}, status=404)

    if request.method == 'DELETE':
        miembro.delete()
        return JsonResponse({'mensaje': 'Eliminado correctamente'})

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            for field in ('nombre', 'cargo', 'email', 'telefono', 'fecha_ingreso'):
                if field in data:
                    setattr(miembro, field, data[field] or None)
            miembro.save()
            return JsonResponse(_personal_to_dict(miembro))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# ── Dashboard: Contexto Epidemiológico y Climático ───────────────────────────

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

def _wmo_label(code):
    if code is None:
        return "Sin datos"
    if code == 0:
        return "Despejado"
    if code in (1, 2):
        return "Parcial"
    if code == 3:
        return "Nublado"
    if code in (45, 48):
        return "Niebla"
    if 51 <= code <= 67:
        return "Lluvia"
    if 71 <= code <= 77:
        return "Nieve"
    if 80 <= code <= 82:
        return "Chubascos"
    if 95 <= code <= 99:
        return "Tormenta"
    return "Variable"

@csrf_exempt
def dashboard_contexto(request):
    """Returns 7-day weather forecast + latest epidemiological week disease summary."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    perfil, _ = PerfilInstitucional.objects.get_or_create(pk=1)
    pronostico = []

    try:
        resp = http_requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": perfil.lat,
                "longitude": perfil.lng,
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,weather_code",
                "forecast_days": 7,
                "timezone": "America/Santiago",
            },
            timeout=8,
        )
        if resp.ok:
            d = resp.json().get("daily", {})
            dates = d.get("time", [])
            for i, fecha_str in enumerate(dates):
                from datetime import date as dt_date
                fecha = dt_date.fromisoformat(fecha_str)
                code = d["weather_code"][i] if i < len(d.get("weather_code", [])) else None
                pronostico.append({
                    "fecha": fecha_str,
                    "dia": DIAS_ES[fecha.weekday()],
                    "temp_max": d["temperature_2m_max"][i] if i < len(d.get("temperature_2m_max", [])) else None,
                    "temp_min": d["temperature_2m_min"][i] if i < len(d.get("temperature_2m_min", [])) else None,
                    "precipitacion": d["precipitation_sum"][i] if i < len(d.get("precipitation_sum", [])) else None,
                    "prob_lluvia": d["precipitation_probability_max"][i] if i < len(d.get("precipitation_probability_max", [])) else None,
                    "codigo_clima": code,
                    "descripcion": _wmo_label(code),
                })
    except Exception:
        pass

    last_se = RegistroCasosRespiratorios.objects.aggregate(
        max_se=Max("semana_epidemiologica"),
        max_anio=Max("anio"),
    )
    se_data = {}
    region_rm = None
    virus_nacional = []

    if last_se["max_se"]:
        registros = RegistroCasosRespiratorios.objects.filter(
            semana_epidemiologica=last_se["max_se"],
            anio=last_se["max_anio"],
        )
        total_rm = 0
        for r in registros:
            if r.region == "Región Metropolitana":
                total_rm += r.casos_confirmados
                virus_nacional.append({"virus": r.tipo_virus, "casos": r.casos_confirmados})

        if total_rm > 0:
            region_rm = {"region": "Región Metropolitana", "casos": total_rm}

        se_data = {
            "semana_epidemiologica": last_se["max_se"],
            "anio": last_se["max_anio"],
            "region_metropolitana": region_rm,
            "nacionales_por_virus": sorted(virus_nacional, key=lambda x: x["casos"], reverse=True),
        }

    return JsonResponse({"pronostico": pronostico, "enfermedades": se_data})
