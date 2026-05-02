import os
import joblib
import numpy as np
import pandas as pd
from datetime import date, timedelta
from calendar import monthrange

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from gestion_ninos.models import (
    Nino, RegistroAsistencia, RegistroMeteorologico, RegistroCasosRespiratorios
)
from modelos_predictivos.features import (
    build_weekly_features, build_student_features
)

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'trained_models')
MODEL_A_PATH = os.path.join(MODELS_DIR, 'xgb_tasa.pkl')
MODEL_B_PATH = os.path.join(MODELS_DIR, 'xgb_riesgo.pkl')

FEATURE_COLS_A = [
    'week_of_year', 'month', 'rolling_4w_rate',
    'avg_temp_max', 'total_precip', 'disease_cases_rm', 'has_holiday',
]

FEATURE_COLS_B = [
    'quintil_rsh', 'situacion_laboral', 'numero_hermanos', 'age_months', 'curso',
    'attendance_rate_30d', 'attendance_rate_60d', 'overall_attendance_rate',
    'max_consecutive_absences', 'num_absences_30d', 'total_days_recorded',
    'avg_temp_last_7d', 'total_precip_last_7d', 'disease_cases_rm_last_week',
]


def _next_month_info():
    today = date.today()
    if today.month == 12:
        year, month = today.year + 1, 1
    else:
        year, month = today.year, today.month + 1

    mes_nombres = [
        '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
    ]
    _, days_in_month = monthrange(year, month)
    school_days = sum(
        1 for d in range(1, days_in_month + 1)
        if date(year, month, d).weekday() < 5
    )
    return mes_nombres[month], year, school_days


@csrf_exempt
def prediccion(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    if not os.path.exists(MODEL_A_PATH) or not os.path.exists(MODEL_B_PATH):
        return JsonResponse({'error': 'Modelos no entrenados'}, status=503)

    try:
        model_a = joblib.load(MODEL_A_PATH)
        model_b = joblib.load(MODEL_B_PATH)
    except Exception as e:
        return JsonResponse({'error': f'Error cargando modelos: {str(e)}'}, status=500)

    # --- Model A prediction ---
    all_att = RegistroAsistencia.objects.all().values('fecha', 'estado', 'nino_id')
    df_all = pd.DataFrame(list(all_att))

    weather_qs = RegistroMeteorologico.objects.all().values('fecha', 'temp_max', 'temp_min', 'precipitacion')
    df_weather = pd.DataFrame(list(weather_qs))

    disease_qs = RegistroCasosRespiratorios.objects.filter(
        region='Región Metropolitana'
    ).values('semana_epidemiologica', 'anio', 'casos_confirmados')
    df_disease_raw = pd.DataFrame(list(disease_qs))
    if not df_disease_raw.empty:
        df_disease = df_disease_raw.groupby(['semana_epidemiologica', 'anio']).agg(
            casos_rm=('casos_confirmados', 'sum')
        ).reset_index()
    else:
        df_disease = pd.DataFrame(columns=['semana_epidemiologica', 'anio', 'casos_rm'])

    if not df_all.empty:
        df_all_copy = df_all.copy()
        df_all_copy['fecha'] = pd.to_datetime(df_all_copy['fecha'])
        daily = df_all_copy.groupby('fecha').apply(
            lambda g: (g['estado'] == 'Presente').sum() / len(g) * 100
        ).reset_index()
        daily.columns = ['fecha', 'tasa_diaria']
        features_df = build_weekly_features(daily, df_weather, df_disease)
    else:
        features_df = pd.DataFrame()

    if not features_df.empty:
        last_row = features_df.iloc[-1]
        mes_nombre, next_year, school_days = _next_month_info()

        next_week = int(last_row['week_of_year']) + 4
        next_month = date.today().month + 1 if date.today().month < 12 else 1
        X_pred = np.array([[
            next_week % 52,
            next_month,
            float(last_row['rolling_4w_rate']),
            float(last_row['avg_temp_max']),
            float(last_row['total_precip']) * 0.8,
            float(last_row['disease_cases_rm']) * 0.7,
            0,
        ]])
        tasa_predicha = float(np.clip(model_a.predict(X_pred)[0], 0, 100))
        intervalo = [
            round(max(0, tasa_predicha - 5.0), 1),
            round(min(100, tasa_predicha + 5.0), 1),
        ]
        model_a_result = {
            'tasa_predicha': round(tasa_predicha, 1),
            'mes_predicho': f'{mes_nombre} {next_year}',
            'intervalo': intervalo,
            'dias_habiles': school_days,
        }
    else:
        model_a_result = {'error': 'Sin datos de asistencia suficientes'}

    # --- Model B prediction ---
    ninos = list(Nino.objects.all())
    as_of = date.today()
    estudiantes_riesgo = []

    for nino in ninos:
        if df_all.empty:
            df_nino = pd.DataFrame(columns=['fecha', 'estado'])
        else:
            df_nino = df_all[df_all['nino_id'] == nino.id][['fecha', 'estado']].copy()

        feats = build_student_features(nino, df_nino, df_weather, df_disease, as_of)
        X_b = np.array([[feats[c] for c in FEATURE_COLS_B]], dtype=float)

        try:
            probabilidad = float(model_b.predict_proba(X_b)[0, 1])
        except Exception:
            probabilidad = float(model_b.predict(X_b)[0])

        if probabilidad >= 0.60:
            nivel = 'alto'
        elif probabilidad >= 0.35:
            nivel = 'medio'
        else:
            nivel = 'bajo'

        tasa_actual = round(feats['overall_attendance_rate'], 1)

        estudiantes_riesgo.append({
            'id': nino.id,
            'nombre': f'{nino.nombres} {nino.apellidos}',
            'curso': nino.curso,
            'quintil': nino.quintil_rsh,
            'tasa_actual': tasa_actual,
            'probabilidad': round(probabilidad, 3),
            'nivel': nivel,
        })

    estudiantes_riesgo.sort(key=lambda x: -x['probabilidad'])
    total_alto = sum(1 for e in estudiantes_riesgo if e['nivel'] == 'alto')
    total_medio = sum(1 for e in estudiantes_riesgo if e['nivel'] == 'medio')

    return JsonResponse({
        'model_a': model_a_result,
        'model_b': {
            'estudiantes_riesgo': estudiantes_riesgo,
            'total_riesgo_alto': total_alto,
            'total_riesgo_medio': total_medio,
        },
    })
