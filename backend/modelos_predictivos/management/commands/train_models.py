import os
import joblib
import numpy as np
import pandas as pd
from datetime import date

from django.core.management.base import BaseCommand

from gestion_ninos.models import (
    Nino, RegistroAsistencia, RegistroMeteorologico, RegistroCasosRespiratorios
)
from modelos_predictivos.features import (
    build_weekly_features, build_student_features, CURSO_ENCODING
)

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'trained_models')
MODEL_A_PATH = os.path.join(MODELS_DIR, 'xgb_tasa.pkl')
MODEL_B_PATH = os.path.join(MODELS_DIR, 'xgb_riesgo.pkl')

CHRONIC_THRESHOLD = 0.80  # 20% absence = chronically absent


class Command(BaseCommand):
    help = 'Entrena los modelos predictivos XGBoost de asistencia y riesgo individual.'

    def handle(self, *args, **options):
        try:
            from xgboost import XGBRegressor, XGBClassifier
            from sklearn.model_selection import cross_val_score, LeaveOneOut
            from sklearn.metrics import mean_absolute_error, roc_auc_score
        except ImportError:
            self.stderr.write('Faltan paquetes: pip install xgboost scikit-learn pandas numpy joblib')
            return

        os.makedirs(MODELS_DIR, exist_ok=True)

        self.stdout.write('Cargando datos...')
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

        self._train_model_a(df_weather, df_disease, XGBRegressor, cross_val_score, mean_absolute_error)
        self._train_model_b(df_weather, df_disease, XGBClassifier, LeaveOneOut, roc_auc_score)

    def _train_model_a(self, df_weather, df_disease, XGBRegressor, cross_val_score, mean_absolute_error):
        self.stdout.write('\n--- Modelo A: Tasa Global de Asistencia ---')

        all_attendance = RegistroAsistencia.objects.all().values('fecha', 'estado', 'nino_id')
        df_all = pd.DataFrame(list(all_attendance))
        if df_all.empty:
            self.stderr.write('Sin datos de asistencia para Model A.')
            return

        df_all['fecha'] = pd.to_datetime(df_all['fecha'])
        daily = df_all.groupby('fecha').apply(
            lambda g: (g['estado'] == 'Presente').sum() / len(g) * 100
        ).reset_index()
        daily.columns = ['fecha', 'tasa_diaria']

        features_df = build_weekly_features(daily, df_weather, df_disease)
        if features_df.empty or len(features_df) < 5:
            self.stderr.write(f'Datos insuficientes para Model A ({len(features_df)} semanas).')
            return

        feature_cols = [
            'week_of_year', 'month', 'rolling_4w_rate',
            'avg_temp_max', 'total_precip', 'disease_cases_rm', 'has_holiday',
        ]
        X = features_df[feature_cols].values
        y = features_df['tasa_semanal'].values

        model_a = XGBRegressor(
            max_depth=2,
            n_estimators=50,
            learning_rate=0.1,
            subsample=0.8,
            random_state=42,
            verbosity=0,
        )

        n_folds = min(4, len(X))
        if len(X) >= n_folds:
            scores = cross_val_score(model_a, X, y, cv=n_folds, scoring='neg_mean_absolute_error')
            mae_cv = -scores.mean()
            self.stdout.write(f'Model A — CV MAE: {mae_cv:.2f}% (n={len(X)} semanas, {n_folds} folds)')

        model_a.fit(X, y)
        y_pred = model_a.predict(X)
        mae_train = mean_absolute_error(y, y_pred)
        self.stdout.write(f'Model A — Train MAE: {mae_train:.2f}%')

        importances = dict(zip(feature_cols, model_a.feature_importances_))
        top = sorted(importances.items(), key=lambda x: -x[1])[:3]
        self.stdout.write('Top features: ' + ', '.join(f'{k}={v:.3f}' for k, v in top))

        joblib.dump(model_a, MODEL_A_PATH)
        self.stdout.write(f'Model A guardado en {MODEL_A_PATH}')

    def _train_model_b(self, df_weather, df_disease, XGBClassifier, LeaveOneOut, roc_auc_score):
        self.stdout.write('\n--- Modelo B: Riesgo de Ausentismo Crónico ---')

        ninos = list(Nino.objects.all())
        if not ninos:
            self.stderr.write('Sin estudiantes para Model B.')
            return

        all_attendance = RegistroAsistencia.objects.all().values('nino_id', 'fecha', 'estado')
        df_all = pd.DataFrame(list(all_attendance))

        as_of = date(2025, 8, 29)  # end of the training attendance period

        rows = []
        labels = []

        for nino in ninos:
            if df_all.empty:
                df_nino = pd.DataFrame(columns=['fecha', 'estado'])
            else:
                df_nino = df_all[df_all['nino_id'] == nino.id][['fecha', 'estado']].copy()

            feats = build_student_features(nino, df_nino, df_weather, df_disease, as_of)
            rows.append(feats)

            # Label: is this student chronically absent? (attendance rate < 80% = >20% absent)
            label = 1 if feats['overall_attendance_rate'] < (CHRONIC_THRESHOLD * 100) else 0
            labels.append(label)

        feature_cols = list(rows[0].keys())
        X = np.array([[r[c] for c in feature_cols] for r in rows], dtype=float)
        y = np.array(labels)

        n_chronic = int(y.sum())
        n_non_chronic = len(y) - n_chronic
        self.stdout.write(f'Estudiantes crónicos: {n_chronic}, no crónicos: {n_non_chronic}')

        if n_chronic == 0 or n_non_chronic == 0:
            self.stderr.write('Solo hay una clase — no se puede entrenar Model B.')
            return

        scale_pos_weight = n_non_chronic / max(n_chronic, 1)

        model_b = XGBClassifier(
            max_depth=3,
            n_estimators=100,
            learning_rate=0.1,
            subsample=0.8,
            scale_pos_weight=scale_pos_weight,
            eval_metric='auc',
            random_state=42,
            verbosity=0,
        )

        # LOOCV for AUC
        loo = LeaveOneOut()
        y_proba = np.zeros(len(y))
        for train_idx, test_idx in loo.split(X):
            X_tr, X_te = X[train_idx], X[test_idx]
            y_tr = y[train_idx]
            if len(np.unique(y_tr)) < 2:
                y_proba[test_idx] = 0.5
                continue
            m = XGBClassifier(
                max_depth=3, n_estimators=100, learning_rate=0.1,
                subsample=0.8, scale_pos_weight=scale_pos_weight,
                eval_metric='auc', random_state=42, verbosity=0,
            )
            m.fit(X_tr, y_tr)
            y_proba[test_idx] = m.predict_proba(X_te)[0, 1]

        try:
            auc = roc_auc_score(y, y_proba)
            self.stdout.write(f'Model B — LOOCV ROC-AUC: {auc:.3f}')
        except Exception:
            self.stdout.write('Model B — AUC no calculable (distribución de clases extrema)')

        # Final fit on all data
        model_b.fit(X, y)
        importances = dict(zip(feature_cols, model_b.feature_importances_))
        top = sorted(importances.items(), key=lambda x: -x[1])[:4]
        self.stdout.write('Top features: ' + ', '.join(f'{k}={v:.3f}' for k, v in top))

        high_risk = int((y_proba >= 0.60).sum())
        medium_risk = int(((y_proba >= 0.35) & (y_proba < 0.60)).sum())
        self.stdout.write(f'Riesgo alto (≥0.60): {high_risk}, medio (0.35-0.59): {medium_risk}')

        joblib.dump(model_b, MODEL_B_PATH)
        self.stdout.write(f'Model B guardado en {MODEL_B_PATH}')
