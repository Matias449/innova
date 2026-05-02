import pandas as pd
import numpy as np
from datetime import date, timedelta


CURSO_ENCODING = {
    'Medio Menor A': 0,
    'Medio Menor B': 1,
    'Medio Mayor A': 2,
    'Medio Mayor B': 3,
}

LABORAL_ENCODING = {
    'ninguno': 0,
    'uno': 1,
    'ambos': 2,
}

CHILE_HOLIDAYS_2025 = {
    date(2025, 4, 18), date(2025, 4, 19),  # Semana Santa
    date(2025, 5, 1),   # Día del Trabajo
    date(2025, 5, 21),  # Glorias Navales
    date(2025, 6, 20),  # Día del Padre (no feriado legal, but included in some school calendars)
    date(2025, 6, 29),  # San Pedro y San Pablo
    date(2025, 7, 16),  # Virgen del Carmen
    date(2025, 8, 15),  # Asunción de la Virgen
    date(2025, 9, 18), date(2025, 9, 19),  # Independencia
}

VACACIONES_INVIERNO_2025 = set()
for d in range(0, 14):
    day = date(2025, 7, 14) + timedelta(days=d)
    VACACIONES_INVIERNO_2025.add(day)


def _is_school_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    if d in CHILE_HOLIDAYS_2025:
        return False
    if d in VACACIONES_INVIERNO_2025:
        return False
    return True


def build_weekly_features(
    df_attendance: pd.DataFrame,
    df_weather: pd.DataFrame,
    df_disease: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build weekly feature matrix for Model A (school-level attendance rate regression).

    df_attendance: columns [fecha, tasa_diaria] where tasa_diaria is 0-100
    df_weather: columns [fecha, temp_max, temp_min, precipitacion]
    df_disease: columns [semana_epidemiologica, anio, casos_rm]
    Returns DataFrame with one row per week.
    """
    if df_attendance.empty:
        return pd.DataFrame()

    df_attendance = df_attendance.copy()
    df_attendance['fecha'] = pd.to_datetime(df_attendance['fecha'])
    df_attendance = df_attendance.sort_values('fecha')
    df_attendance['week'] = df_attendance['fecha'].dt.isocalendar().week.astype(int)
    df_attendance['year'] = df_attendance['fecha'].dt.year
    df_attendance['month'] = df_attendance['fecha'].dt.month

    weekly = df_attendance.groupby(['year', 'week']).agg(
        tasa_semanal=('tasa_diaria', 'mean'),
        month=('month', 'first'),
    ).reset_index()

    weekly = weekly.sort_values(['year', 'week']).reset_index(drop=True)
    weekly['week_of_year'] = weekly['week']
    weekly['rolling_4w_rate'] = weekly['tasa_semanal'].rolling(4, min_periods=1).mean().shift(1)
    weekly['rolling_4w_rate'] = weekly['rolling_4w_rate'].fillna(weekly['tasa_semanal'].mean())

    # Weather join
    if not df_weather.empty:
        df_weather = df_weather.copy()
        df_weather['fecha'] = pd.to_datetime(df_weather['fecha'])
        df_weather['week'] = df_weather['fecha'].dt.isocalendar().week.astype(int)
        df_weather['year'] = df_weather['fecha'].dt.year
        weather_weekly = df_weather.groupby(['year', 'week']).agg(
            avg_temp_max=('temp_max', 'mean'),
            total_precip=('precipitacion', 'sum'),
        ).reset_index()
        weekly = weekly.merge(weather_weekly, on=['year', 'week'], how='left')
    else:
        weekly['avg_temp_max'] = np.nan
        weekly['total_precip'] = np.nan

    # Disease join
    if not df_disease.empty:
        df_disease = df_disease.copy()
        disease_weekly = df_disease.groupby(['anio', 'semana_epidemiologica']).agg(
            disease_cases_rm=('casos_rm', 'sum')
        ).reset_index().rename(columns={'anio': 'year', 'semana_epidemiologica': 'week'})
        weekly = weekly.merge(disease_weekly, on=['year', 'week'], how='left')
    else:
        weekly['disease_cases_rm'] = np.nan

    weekly['disease_cases_rm'] = weekly['disease_cases_rm'].fillna(0)
    weekly['avg_temp_max'] = weekly['avg_temp_max'].fillna(weekly['avg_temp_max'].median())
    weekly['total_precip'] = weekly['total_precip'].fillna(0)

    weekly['has_holiday'] = weekly['week_of_year'].apply(
        lambda w: 1 if w in {16, 21, 25, 26, 27, 28, 29, 30} else 0
    )

    feature_cols = [
        'week_of_year', 'month', 'rolling_4w_rate',
        'avg_temp_max', 'total_precip', 'disease_cases_rm', 'has_holiday',
    ]
    return weekly[feature_cols + ['tasa_semanal', 'year', 'week']].copy()


def build_student_features(
    student,
    df_attendance: pd.DataFrame,
    df_weather: pd.DataFrame,
    df_disease: pd.DataFrame,
    as_of_date: date,
) -> dict:
    """
    Build feature dict for a single student for Model B (chronic absence risk classifier).

    student: Nino ORM instance
    df_attendance: all attendance rows for this student [fecha, estado]
    df_weather: weather records [fecha, temp_max, precipitacion]
    df_disease: disease records [semana_epidemiologica, anio, casos_rm]
    as_of_date: reference date for rolling window calculations
    """
    today = as_of_date
    d30 = today - timedelta(days=30)
    d60 = today - timedelta(days=60)
    d7 = today - timedelta(days=7)

    if not df_attendance.empty:
        df_att = df_attendance.copy()
        df_att['fecha'] = pd.to_datetime(df_att['fecha']).dt.date
        df_att = df_att.sort_values('fecha')

        att_30 = df_att[df_att['fecha'] >= d30]
        att_60 = df_att[df_att['fecha'] >= d60]
        total_all = len(df_att)
        absent_all = (df_att['estado'] == 'Ausente').sum()

        rate_30 = (1 - (att_30['estado'] == 'Ausente').sum() / max(len(att_30), 1)) * 100
        rate_60 = (1 - (att_60['estado'] == 'Ausente').sum() / max(len(att_60), 1)) * 100
        overall_rate = (1 - absent_all / max(total_all, 1)) * 100

        # Max consecutive absences
        estados = df_att['estado'].tolist()
        max_consec = 0
        cur = 0
        for e in estados:
            if e == 'Ausente':
                cur += 1
                max_consec = max(max_consec, cur)
            else:
                cur = 0

        num_absences_30d = int((att_30['estado'] == 'Ausente').sum())
    else:
        rate_30 = rate_60 = overall_rate = 100.0
        max_consec = 0
        num_absences_30d = 0
        total_all = 0

    # Weather last 7 days
    if not df_weather.empty:
        df_w = df_weather.copy()
        df_w['fecha'] = pd.to_datetime(df_w['fecha']).dt.date
        w7 = df_w[df_w['fecha'] >= d7]
        avg_temp_last_7d = w7['temp_max'].mean() if not w7.empty else np.nan
        total_precip_last_7d = w7['precipitacion'].sum() if not w7.empty else 0.0
    else:
        avg_temp_last_7d = np.nan
        total_precip_last_7d = 0.0

    # Disease last week
    if not df_disease.empty:
        today_isoweek = today.isocalendar()[1]
        today_year = today.year
        prev_week = today_isoweek - 1 if today_isoweek > 1 else 52
        prev_year = today_year if today_isoweek > 1 else today_year - 1
        disease_last_week = df_disease[
            (df_disease['semana_epidemiologica'] == prev_week) &
            (df_disease['anio'] == prev_year)
        ]['casos_rm'].sum()
    else:
        disease_last_week = 0

    age_months = (
        (today.year - student.fecha_nacimiento.year) * 12
        + (today.month - student.fecha_nacimiento.month)
    )

    return {
        'quintil_rsh': student.quintil_rsh or 3,
        'situacion_laboral': LABORAL_ENCODING.get(student.situacion_laboral_padres or 'uno', 1),
        'numero_hermanos': student.numero_hermanos or 0,
        'age_months': age_months,
        'curso': CURSO_ENCODING.get(student.curso, 0),
        'attendance_rate_30d': rate_30,
        'attendance_rate_60d': rate_60,
        'overall_attendance_rate': overall_rate,
        'max_consecutive_absences': max_consec,
        'num_absences_30d': num_absences_30d,
        'total_days_recorded': total_all,
        'avg_temp_last_7d': avg_temp_last_7d if not np.isnan(avg_temp_last_7d) else 15.0,
        'total_precip_last_7d': total_precip_last_7d,
        'disease_cases_rm_last_week': int(disease_last_week),
    }
