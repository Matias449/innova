<template>
  <div class="subpage">
    <main class="dashboard-container">

      <section class="section-header">
        <div class="header-titles">
          <h2>Dashboard de Asistencia</h2>
          <p>Análisis histórico de presentismo por curso y período.</p>
        </div>
        <div class="view-tabs">
          <button :class="['tab-btn', { active: mainView === 'datos' }]" @click="setMainView('datos')">Datos Actuales</button>
          <button :class="['tab-btn', { active: mainView === 'proyecciones' }]" @click="setMainView('proyecciones')">Proyecciones</button>
        </div>
      </section>

      <div v-if="mainView === 'datos'" class="sub-view-tabs">
        <button :class="['sub-tab-btn', { active: activeView === 'global' }]" @click="setView('global')">Vista Global</button>
        <button :class="['sub-tab-btn', { active: activeView === 'curso' }]" @click="setView('curso')">Por Curso</button>
      </div>

      <div v-if="mainView === 'datos' && loading" class="empty-state">Cargando datos del dashboard...</div>
      <div v-else-if="mainView === 'datos' && error" class="empty-state error-state">
        No se pudieron cargar los datos. Verifique que el servidor esté activo.
      </div>

      <!-- ───────── CONTEXTO EPIDEMIOLÓGICO ───────── -->
      <div v-if="mainView === 'datos' && !loading && !error" class="contexto-row">

        <!-- Pronóstico 7 días -->
        <div class="card contexto-card">
          <h3 class="contexto-title">Pronóstico — Próximos 7 días</h3>
          <div v-if="pronostico.length" class="forecast-strip">
            <div
              v-for="dia in pronostico"
              :key="dia.fecha"
              class="forecast-day"
              :class="{ 'forecast-today': dia === pronostico[0] }"
            >
              <span class="fc-day-label">{{ dia === pronostico[0] ? 'Hoy' : dia.dia }}</span>
              <span class="fc-icon" v-html="weatherIcon(dia.codigo_clima)"></span>
              <span class="fc-desc">{{ dia.descripcion }}</span>
              <div class="fc-temps">
                <span class="fc-max">{{ dia.temp_max !== null ? Math.round(dia.temp_max) + '°' : '—' }}</span>
                <span class="fc-min">{{ dia.temp_min !== null ? Math.round(dia.temp_min) + '°' : '—' }}</span>
              </div>
              <div class="fc-rain" v-if="dia.prob_lluvia !== null">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z" /></svg>
                <svg width="9" height="12" viewBox="0 0 12 16" fill="#60a5fa"><path d="M6 0 C6 0 0 8 0 11 C0 14.3 2.7 16 6 16 C9.3 16 12 14.3 12 11 C12 8 6 0 6 0Z"/></svg>
                {{ dia.prob_lluvia }}%
              </div>
            </div>
          </div>
          <p v-else class="fc-empty">Pronóstico no disponible.</p>
        </div>

        <!-- Resumen enfermedades -->
        <div class="card contexto-card">
          <h3 class="contexto-title">
            Vigilancia Respiratoria
            <span v-if="enfermedades.semana_epidemiologica" class="se-badge">
              SE {{ enfermedades.semana_epidemiologica }}/{{ enfermedades.anio }}
            </span>
          </h3>
          <div v-if="enfermedades.semana_epidemiologica">
            <div v-if="enfermedades.region_metropolitana" class="rm-highlight">
              <span class="rm-label">Positivos en Región Metropolitana</span>
              <span class="rm-value" :class="riskClass(enfermedades.region_metropolitana.casos)">
                {{ enfermedades.region_metropolitana.casos }}
              </span>
              <span class="rm-sub">casos confirmados (todos los virus)</span>
              <div class="risk-bar-track">
                <div class="risk-bar-fill" :class="riskClass(enfermedades.region_metropolitana.casos)" :style="{ width: Math.min(enfermedades.region_metropolitana.casos / 3, 100) + '%' }"></div>
              </div>
            </div>
            <div class="virus-list">
              <div
                v-for="v in enfermedades.nacionales_por_virus.slice(0, 5)"
                :key="v.virus"
                class="virus-row"
              >
                <span class="virus-name">{{ v.virus }}</span>
                <div class="virus-bar-track">
                  <div class="virus-bar-fill" :style="{ width: virusBarPct(v.casos) + '%' }"></div>
                </div>
                <span class="virus-count">{{ v.casos }}</span>
              </div>
            </div>
            <p class="epid-source">Fuente: ISPCH — Datos nacionales</p>
          </div>
          <p v-else class="fc-empty">Sin datos epidemiológicos. Ejecute <code>fetch_enfermedades</code>.</p>
        </div>
      </div>

      <!-- ───────── VISTA GLOBAL ───────── -->
      <div v-if="mainView === 'datos' && !loading && !error && activeView === 'global'">
        <div class="kpi-grid">
          <div class="card stat-card">
            <span class="stat-label">Tasa de Asistencia Global</span>
            <span class="stat-value" :class="{ 'value-warning': globalData.tasa_global < 85 }">
              {{ globalData.tasa_global }}%
            </span>
            <div class="stat-bar-track">
              <div class="stat-bar-fill" :style="{ width: globalData.tasa_global + '%' }"></div>
            </div>
          </div>
          <div class="card stat-card">
            <span class="stat-label">Inasistencias Totales</span>
            <span class="stat-value value-danger">{{ globalData.total_inasistencias.toLocaleString('es-CL') }}</span>
            <span class="stat-sub">registros en el período</span>
          </div>
          <div class="card stat-card">
            <span class="stat-label">Atrasos Totales</span>
            <span class="stat-value value-amber">{{ globalData.total_atrasos.toLocaleString('es-CL') }}</span>
            <span class="stat-sub">registros en el período</span>
          </div>
          <div class="card stat-card">
            <span class="stat-label">Cursos Monitoreados</span>
            <span class="stat-value value-primary">{{ cursosData.length }}</span>
            <span class="stat-sub">cursos activos</span>
          </div>
        </div>

        <div class="charts-row">
          <div class="card chart-panel">
            <div class="chart-panel-header">
              <div>
                <h3>Comparativa por Curso</h3>
                <span class="chart-subtitle">Tasa de asistencia acumulada del período</span>
              </div>
            </div>
            <div class="chart-container-sm">
              <Bar :data="barChartData" :options="barChartOptions" />
            </div>
          </div>

          <div class="card chart-panel">
            <div class="chart-panel-header">
              <div>
                <h3>Resumen por Curso</h3>
                <span class="chart-subtitle">Indicadores clave</span>
              </div>
            </div>
            <table class="data-table">
              <thead>
                <tr>
                  <th>Curso</th>
                  <th>Tasa</th>
                  <th>Ausentes</th>
                  <th>Atrasos</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in cursosData" :key="c.curso" class="table-row-hover" @click="quickJump(c.curso)">
                  <td class="course-name-cell">{{ c.curso }}</td>
                  <td>
                    <span :class="['tasa-pill', c.tasa_asistencia >= 90 ? 'pill-green' : c.tasa_asistencia >= 85 ? 'pill-amber' : 'pill-red']">
                      {{ c.tasa_asistencia }}%
                    </span>
                  </td>
                  <td class="num-cell danger">{{ c.ausentes.toLocaleString('es-CL') }}</td>
                  <td class="num-cell amber">{{ c.atrasos.toLocaleString('es-CL') }}</td>
                </tr>
              </tbody>
            </table>
            <p class="table-hint">Haz clic en una fila para analizar ese curso</p>
          </div>
        </div>

        <div class="card chart-panel wide-panel">
          <div class="chart-panel-header">
            <div>
              <h3>Evolución Temporal — Todos los Cursos</h3>
              <span class="chart-subtitle">Arrastre para hacer zoom profundo · Use la rueda del mouse para zoom</span>
            </div>
            <div class="interval-filter">
              <button :class="['interval-btn', { active: selectedInterval === 'mensual' }]" @click="setInterval('mensual')">Mensual</button>
              <button :class="['interval-btn', { active: selectedInterval === 'semanal' }]" @click="setInterval('semanal')">Semanal</button>
              <button :class="['interval-btn', { active: selectedInterval === 'diario' }]" @click="setInterval('diario')">Diario</button>
            </div>
          </div>
          <div class="chart-container-lg">
            <Line :data="lineChartData" :options="lineChartOptions" />
          </div>
        </div>
      </div>

      <!-- ───────── VISTA POR CURSO ───────── -->
      <div v-if="mainView === 'datos' && !loading && !error && activeView === 'curso'">
        <div class="course-tabs-row">
          <button
            v-for="c in cursosData"
            :key="c.curso"
            :class="['course-tab-btn', { active: selectedCursoDetalle === c.curso }]"
            @click="selectCursoDetalle(c.curso)"
          >
            {{ c.curso }}
          </button>
        </div>

        <div v-if="loadingCurso" class="empty-state">Cargando datos del curso...</div>

        <div v-else-if="selectedCursoDetalle && cursoDetalleData">
          <div class="kpi-grid kpi-4">
            <div class="card stat-card">
              <span class="stat-label">Tasa de Asistencia</span>
              <span class="stat-value" :class="{ 'value-warning': cursoDetalleData.tasa_global < 85 }">
                {{ cursoDetalleData.tasa_global }}%
              </span>
              <div class="stat-bar-track">
                <div class="stat-bar-fill" :style="{ width: cursoDetalleData.tasa_global + '%' }"></div>
              </div>
            </div>
            <div class="card stat-card">
              <span class="stat-label">Presentes</span>
              <span class="stat-value value-green">{{ cursoPresentes.toLocaleString('es-CL') }}</span>
              <span class="stat-sub">registros en el período</span>
            </div>
            <div class="card stat-card">
              <span class="stat-label">Ausentes</span>
              <span class="stat-value value-danger">{{ cursoDetalleData.total_inasistencias.toLocaleString('es-CL') }}</span>
              <span class="stat-sub">registros en el período</span>
            </div>
            <div class="card stat-card">
              <span class="stat-label">Atrasos</span>
              <span class="stat-value value-amber">{{ cursoDetalleData.total_atrasos.toLocaleString('es-CL') }}</span>
              <span class="stat-sub">registros en el período</span>
            </div>
          </div>

          <div class="charts-row charts-row-detail">
            <div class="card chart-panel chart-flex-2">
              <div class="chart-panel-header">
                <div>
                  <h3>Evolución — {{ selectedCursoDetalle }}</h3>
                  <span class="chart-subtitle">Arrastre para hacer zoom · Use rueda del mouse</span>
                </div>
                <div class="interval-filter">
                  <button :class="['interval-btn', { active: selectedIntervalCurso === 'mensual' }]" @click="setIntervalCurso('mensual')">Mensual</button>
                  <button :class="['interval-btn', { active: selectedIntervalCurso === 'semanal' }]" @click="setIntervalCurso('semanal')">Semanal</button>
                  <button :class="['interval-btn', { active: selectedIntervalCurso === 'diario' }]" @click="setIntervalCurso('diario')">Diario</button>
                </div>
              </div>
              <div class="chart-container-md">
                <Line :data="lineChartDataCurso" :options="lineChartOptions" />
              </div>
            </div>

            <div class="card chart-panel chart-flex-1">
              <div class="chart-panel-header">
                <div>
                  <h3>Distribución</h3>
                  <span class="chart-subtitle">Estados acumulados</span>
                </div>
              </div>
              <div class="donut-wrapper">
                <Doughnut :data="donutChartData" :options="donutOptions" />
              </div>
              <div class="donut-legend">
                <div class="legend-item" v-for="item in donutLegend" :key="item.label">
                  <span class="legend-dot" :style="{ background: item.color }"></span>
                  <span class="legend-text">{{ item.label }}</span>
                  <strong class="legend-value">{{ item.value.toLocaleString('es-CL') }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">Selecciona un curso para ver el análisis detallado.</div>
      </div>

      <!-- ───────── PROYECCIONES ───────── -->
      <div v-if="mainView === 'proyecciones'">
        <div v-if="mlLoading" class="empty-state">Calculando predicciones...</div>

        <div v-else-if="mlError === 503" class="empty-state">
          <p>Modelos no entrenados.</p>
          <code class="code-hint">python manage.py train_models</code>
        </div>

        <div v-else-if="mlError" class="empty-state error-state">
          No se pudieron cargar las predicciones. Verifique que el servidor esté activo.
        </div>

        <div v-else-if="mlData">
          <!-- KPIs de predicción -->
          <div class="kpi-grid kpi-3">
            <div class="card stat-card">
              <span class="stat-label">Tasa Proyectada — {{ mlData.model_a.mes_predicho }}</span>
              <span class="stat-value value-primary">{{ mlData.model_a.tasa_predicha }}%</span>
              <div class="stat-bar-track">
                <div class="stat-bar-fill" :style="{ width: mlData.model_a.tasa_predicha + '%' }"></div>
              </div>
              <span class="stat-sub">Intervalo: {{ mlData.model_a.intervalo[0] }}% — {{ mlData.model_a.intervalo[1] }}%</span>
            </div>
            <div class="card stat-card">
              <span class="stat-label">Riesgo Alto de Ausentismo</span>
              <span class="stat-value value-danger">{{ mlData.model_b.total_riesgo_alto }}</span>
              <span class="stat-sub">estudiantes con probabilidad ≥ 60%</span>
            </div>
            <div class="card stat-card">
              <span class="stat-label">Riesgo Moderado</span>
              <span class="stat-value value-amber">{{ mlData.model_b.total_riesgo_medio }}</span>
              <span class="stat-sub">estudiantes con probabilidad 35–60%</span>
            </div>
          </div>

          <!-- Tabla de riesgo individual -->
          <div class="card chart-panel">
            <div class="chart-panel-header">
              <div>
                <h3>Estudiantes con Riesgo de Ausentismo Crónico</h3>
                <span class="chart-subtitle">Umbral JUNJI: 20% de inasistencias. Ordenados por probabilidad.</span>
              </div>
              <div class="risk-legend">
                <span class="risk-pill risk-alto">Alto</span>
                <span class="risk-pill risk-medio">Moderado</span>
                <span class="risk-pill risk-bajo">Bajo</span>
              </div>
            </div>
            <div class="table-responsive">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>Estudiante</th>
                    <th>Curso</th>
                    <th>Quintil RSH</th>
                    <th>Tasa Actual</th>
                    <th>Probabilidad</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="e in riesgoFiltrado"
                    :key="e.id"
                    :class="{ 'risk-row-alto': e.nivel === 'alto', 'risk-row-medio': e.nivel === 'medio' }"
                  >
                    <td class="course-name-cell">{{ e.nombre }}</td>
                    <td>{{ e.curso }}</td>
                    <td class="num-cell">{{ e.quintil ? 'Q' + e.quintil : '—' }}</td>
                    <td class="num-cell" :class="{ 'danger': e.tasa_actual < 80 }">{{ e.tasa_actual }}%</td>
                    <td>
                      <span :class="['risk-pill', 'risk-' + e.nivel]">
                        {{ Math.round(e.probabilidad * 100) }}%
                        {{ e.nivel === 'alto' ? 'Alto' : e.nivel === 'medio' ? 'Moderado' : 'Bajo' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <p class="proyeccion-note">
            Modelo entrenado con datos históricos del establecimiento. Las predicciones son orientativas y deben complementarse con criterio profesional.
          </p>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'
import zoomPlugin from 'chartjs-plugin-zoom'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler, zoomPlugin
)

const API_BASE_URL = 'http://localhost:8000/api'

const mainView = ref('datos')
const activeView = ref('global')
const loading = ref(true)
const error = ref(false)
const loadingCurso = ref(false)
const mlData = ref(null)
const mlLoading = ref(false)
const mlError = ref(null)

const globalData = ref({ tasa_global: 0, total_inasistencias: 0, total_atrasos: 0, evolucion: { labels: [], data: [] } })
const cursosData = ref([])
const cursoDetalleData = ref(null)
const pronostico = ref([])
const enfermedades = ref({})

const selectedInterval = ref('diario')
const selectedIntervalCurso = ref('mensual')
const selectedCursoDetalle = ref('')

const setView = (view) => { activeView.value = view }

const setMainView = (view) => {
  mainView.value = view
  if (view === 'proyecciones' && !mlData.value && !mlLoading.value) {
    fetchML()
  }
}

const fetchML = async () => {
  mlLoading.value = true
  mlError.value = null
  try {
    const res = await fetch(`${API_BASE_URL}/ml/prediccion/`)
    if (res.status === 503) {
      mlError.value = 503
    } else if (!res.ok) {
      mlError.value = res.status
    } else {
      mlData.value = await res.json()
    }
  } catch {
    mlError.value = -1
  } finally {
    mlLoading.value = false
  }
}

const setInterval = (interval) => {
  selectedInterval.value = interval
  fetchGlobal()
}

const setIntervalCurso = (interval) => {
  selectedIntervalCurso.value = interval
  fetchCursoDetalle(selectedCursoDetalle.value)
}

const fetchContexto = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/dashboard/contexto/`)
    if (res.ok) {
      const data = await res.json()
      pronostico.value = data.pronostico || []
      enfermedades.value = data.enfermedades || {}
    }
  } catch { /* silent fail */ }
}

const WMO_ICONS = {
  clear: `<svg width="28" height="28" viewBox="0 0 24 24" fill="#F59E0B" xmlns="http://www.w3.org/2000/svg"><circle cx="12" cy="12" r="4"/><path stroke="#F59E0B" stroke-width="2" stroke-linecap="round" d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>`,
  cloud: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 10a6 6 0 10-11.93 1A4 4 0 106 19h12a4 4 0 000-8z" fill="#94A3B8"/></svg>`,
  rain: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 10a6 6 0 10-11.93 1A4 4 0 106 19h12a4 4 0 000-8z" fill="#94A3B8"/><path d="M8 19l-1 3M12 19l-1 3M16 19l-1 3" stroke="#60A5FA" stroke-width="1.8" stroke-linecap="round"/></svg>`,
  storm: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 10a6 6 0 10-11.93 1A4 4 0 106 19h12a4 4 0 000-8z" fill="#64748B"/><path d="M13 13l-3 5h4l-3 5" stroke="#FBBF24" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  fog: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 12h18M3 16h12M3 8h14" stroke="#94A3B8" stroke-width="2" stroke-linecap="round"/></svg>`,
  snow: `<svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M18 10a6 6 0 10-11.93 1A4 4 0 106 19h12a4 4 0 000-8z" fill="#BAE6FD"/><path d="M8 19l.5 2M12 19v3M16 19l-.5 2" stroke="#BAE6FD" stroke-width="1.8" stroke-linecap="round"/></svg>`,
}

const weatherIcon = (code) => {
  if (code === null || code === undefined) return WMO_ICONS.cloud
  if (code === 0) return WMO_ICONS.clear
  if (code <= 2) return WMO_ICONS.clear
  if (code === 3) return WMO_ICONS.cloud
  if (code === 45 || code === 48) return WMO_ICONS.fog
  if (code >= 51 && code <= 82) return WMO_ICONS.rain
  if (code >= 71 && code <= 77) return WMO_ICONS.snow
  if (code >= 95) return WMO_ICONS.storm
  return WMO_ICONS.cloud
}

const maxVirusCasos = computed(() => Math.max(...(enfermedades.value.nacionales_por_virus || []).map(v => v.casos), 1))
const virusBarPct = (casos) => Math.round((casos / maxVirusCasos.value) * 100)

const riskClass = (casos) => {
  if (casos > 200) return 'risk-high'
  if (casos > 100) return 'risk-medium'
  return 'risk-low'
}

const fetchGlobal = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/asistencia/dashboard/?curso=Todos&intervalo=${selectedInterval.value}`)
    if (!res.ok) throw new Error()
    globalData.value = await res.json()
  } catch {
    error.value = true
  }
}

const fetchCursosPorCurso = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/asistencia/por-curso/`)
    if (!res.ok) throw new Error()
    cursosData.value = await res.json()
  } catch {
    error.value = true
  }
}

const fetchCursoDetalle = async (curso) => {
  if (!curso) return
  loadingCurso.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/asistencia/dashboard/?curso=${encodeURIComponent(curso)}&intervalo=${selectedIntervalCurso.value}`)
    if (!res.ok) throw new Error()
    cursoDetalleData.value = await res.json()
  } catch {
    cursoDetalleData.value = null
  } finally {
    loadingCurso.value = false
  }
}

const selectCursoDetalle = (curso) => {
  selectedCursoDetalle.value = curso
  fetchCursoDetalle(curso)
}

const quickJump = (curso) => {
  activeView.value = 'curso'
  selectCursoDetalle(curso)
}

const cursoPresentes = computed(() => {
  if (!cursoDetalleData.value || !selectedCursoDetalle.value) return 0
  const found = cursosData.value.find(c => c.curso === selectedCursoDetalle.value)
  return found ? found.presentes : 0
})

// Bar chart — course comparison
const BLUE = '#3B82F6'
const GREEN = '#22c55e'
const COURSE_COLORS = ['#3B82F6', '#22c55e', '#6366f1', '#0ea5e9']

const barChartData = computed(() => ({
  labels: cursosData.value.map(c => c.curso),
  datasets: [
    {
      label: 'Tasa de asistencia (%)',
      data: cursosData.value.map(c => c.tasa_asistencia),
      backgroundColor: COURSE_COLORS.map(c => c + 'CC'),
      borderColor: COURSE_COLORS,
      borderWidth: 1.5,
      borderRadius: 6,
    }
  ]
}))

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1E293B',
      padding: 10,
      callbacks: { label: (ctx) => ` ${ctx.raw}%` }
    }
  },
  scales: {
    y: {
      min: 75,
      max: 100,
      ticks: { callback: (v) => v + '%' },
      grid: { color: '#E2E8F0', borderDash: [4, 4] }
    },
    x: { grid: { display: false } }
  }
}

// Line chart — global evolution
const lineChartData = computed(() => {
  if (!globalData.value?.evolucion) return { labels: [], datasets: [] }
  const isDiario = selectedInterval.value === 'diario'
  return {
    labels: globalData.value.evolucion.labels,
    datasets: [{
      label: 'Tasa de Asistencia (%)',
      data: globalData.value.evolucion.data,
      backgroundColor: BLUE + '22',
      borderColor: BLUE,
      pointBackgroundColor: '#fff',
      pointBorderColor: BLUE,
      pointBorderWidth: isDiario ? 0 : 2,
      pointRadius: isDiario ? 0 : 3,
      pointHoverRadius: 5,
      borderWidth: isDiario ? 1.5 : 2,
      fill: true,
      tension: isDiario ? 0.1 : 0.4,
    }]
  }
})

// Line chart — course evolution
const lineChartDataCurso = computed(() => {
  if (!cursoDetalleData.value?.evolucion) return { labels: [], datasets: [] }
  const isDiario = selectedIntervalCurso.value === 'diario'
  return {
    labels: cursoDetalleData.value.evolucion.labels,
    datasets: [{
      label: 'Tasa de Asistencia (%)',
      data: cursoDetalleData.value.evolucion.data,
      backgroundColor: GREEN + '22',
      borderColor: GREEN,
      pointBackgroundColor: '#fff',
      pointBorderColor: GREEN,
      pointBorderWidth: isDiario ? 0 : 2,
      pointRadius: isDiario ? 0 : 3,
      pointHoverRadius: 5,
      borderWidth: isDiario ? 1.5 : 2,
      fill: true,
      tension: isDiario ? 0.1 : 0.4,
    }]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1E293B',
      padding: 10,
      callbacks: { label: (ctx) => ` ${ctx.raw}%` }
    },
    zoom: {
      pan: { enabled: true, mode: 'x' },
      zoom: {
        drag: { enabled: true, backgroundColor: 'rgba(59,130,246,0.15)' },
        wheel: { enabled: true },
        pinch: { enabled: true },
        mode: 'x'
      }
    }
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: { callback: (v) => v + '%' },
      grid: { color: '#E2E8F0', borderDash: [4, 4] }
    },
    x: { grid: { display: false } }
  }
}

// Donut chart
const donutLegend = computed(() => {
  if (!cursoDetalleData.value || !selectedCursoDetalle.value) return []
  const found = cursosData.value.find(c => c.curso === selectedCursoDetalle.value)
  if (!found) return []
  return [
    { label: 'Presentes', value: found.presentes, color: GREEN },
    { label: 'Ausentes', value: found.ausentes, color: '#EF4444' },
    { label: 'Atrasos', value: found.atrasos, color: '#F59E0B' },
    { label: 'Justificados', value: found.justificados, color: '#6366f1' },
  ]
})

const donutChartData = computed(() => ({
  labels: donutLegend.value.map(d => d.label),
  datasets: [{
    data: donutLegend.value.map(d => d.value),
    backgroundColor: donutLegend.value.map(d => d.color + 'CC'),
    borderColor: donutLegend.value.map(d => d.color),
    borderWidth: 1.5,
    hoverOffset: 6,
  }]
}))

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#1E293B',
      padding: 10,
    }
  }
}

const riesgoFiltrado = computed(() => {
  if (!mlData.value) return []
  return [...mlData.value.model_b.estudiantes_riesgo]
    .sort((a, b) => b.probabilidad - a.probabilidad)
})

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchGlobal(), fetchCursosPorCurso(), fetchContexto()])
  loading.value = false
})
</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.view-tabs {
  display: flex;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-color, #fff);
}

.tab-btn {
  padding: 0.6rem 1.25rem;
  border: none;
  background: none;
  font-family: inherit;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--border-color, #e2e8f0);
}
.tab-btn:last-child { border-right: none; }
.tab-btn:hover { background: #f1f5f9; }
.tab-btn.active { background: var(--primary-color, #3B82F6); color: #fff; }

/* KPI */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.stat-label {
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted, #64748b);
}

.stat-value {
  font-size: 2.4rem;
  font-weight: 800;
  line-height: 1;
  color: var(--primary-color, #3B82F6);
}

.stat-sub {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
}

.stat-bar-track {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.4rem;
}

.stat-bar-fill {
  height: 100%;
  background: var(--primary-color, #3B82F6);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.value-warning { color: #F59E0B !important; }
.value-danger  { color: #EF4444 !important; }
.value-amber   { color: #D97706 !important; }
.value-primary { color: var(--primary-color, #3B82F6) !important; }
.value-green   { color: #22c55e !important; }

/* Charts layout */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.wide-panel { margin-bottom: 1.5rem; }

.chart-panel {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.charts-row-detail { grid-template-columns: 2fr 1fr; }
.chart-flex-2 {}
.chart-flex-1 {}

.chart-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.chart-panel-header h3 { margin: 0; font-size: 1rem; color: var(--text-main, #0f172a); }
.chart-subtitle { font-size: 0.78rem; color: var(--text-muted, #64748b); display: block; margin-top: 0.2rem; }

.chart-container-sm { position: relative; height: 220px; }
.chart-container-md { position: relative; height: 300px; }
.chart-container-lg { position: relative; height: 380px; }

/* Interval filter */
.interval-filter {
  display: flex;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.interval-btn {
  padding: 0.4rem 0.85rem;
  border: none;
  background: none;
  font-family: inherit;
  font-weight: 600;
  font-size: 0.8rem;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--border-color, #e2e8f0);
}
.interval-btn:last-child { border-right: none; }
.interval-btn:hover { background: #f1f5f9; }
.interval-btn.active { background: var(--primary-color, #3B82F6); color: #fff; }

/* Table */
.data-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.data-table th {
  padding: 0.65rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted, #64748b);
  background: #f8fafc;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}
.data-table td { padding: 0.75rem 1rem; border-bottom: 1px solid #f1f5f9; }

.table-row-hover { cursor: pointer; transition: background 0.1s; }
.table-row-hover:hover { background: #f8fafc; }

.course-name-cell { font-weight: 600; color: var(--text-main, #0f172a); }

.tasa-pill {
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.82rem;
}
.pill-green  { background: #dcfce7; color: #166534; }
.pill-amber  { background: #fef9c3; color: #92400e; }
.pill-red    { background: #fee2e2; color: #991b1b; }

.num-cell { font-variant-numeric: tabular-nums; }
.num-cell.danger { color: #EF4444; font-weight: 600; }
.num-cell.amber  { color: #D97706; font-weight: 600; }

.table-hint { font-size: 0.75rem; color: var(--text-muted, #64748b); margin: 0.5rem 1rem 0; font-style: italic; }

/* Course tabs */
.course-tabs-row {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.course-tab-btn {
  padding: 0.6rem 1.25rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  background: var(--bg-color, #fff);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.2s;
}
.course-tab-btn:hover { border-color: var(--primary-color, #3B82F6); color: var(--primary-color, #3B82F6); }
.course-tab-btn.active {
  background: var(--primary-color, #3B82F6);
  border-color: var(--primary-color, #3B82F6);
  color: #fff;
}

/* Donut */
.donut-wrapper { position: relative; height: 180px; }

.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.85rem;
  color: var(--text-main, #0f172a);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-text { flex: 1; color: var(--text-muted, #64748b); }
.legend-value { font-size: 0.85rem; }

/* States */
.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted, #64748b);
  font-style: italic;
}
.error-state { color: #EF4444; }

@media (max-width: 900px) {
  .charts-row { grid-template-columns: 1fr; }
  .chart-flex-2, .chart-flex-1 { flex: unset; }
}

@media (max-width: 600px) {
  .kpi-grid { grid-template-columns: 1fr 1fr; }
  .section-header { flex-direction: column; align-items: flex-start; }
}

/* ── Contexto epidemiológico ── */
.contexto-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.contexto-card {
  padding: 1.5rem;
}

.contexto-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0 0 1.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.se-badge {
  font-size: 0.72rem;
  font-weight: 600;
  background: #e0f2fe;
  color: #0369a1;
  padding: 2px 8px;
  border-radius: 999px;
}

/* Forecast strip */
.forecast-strip {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 0.5rem;
}

.forecast-day {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  padding: 0.65rem 0.25rem;
  border-radius: 10px;
  border: 1px solid var(--border-color, #e2e8f0);
  background: var(--bg-color, #fff);
  transition: background 0.15s;
}

.forecast-today {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.fc-day-label {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted, #64748b);
}

.fc-icon {
  line-height: 1;
  display: flex;
}

.fc-desc {
  font-size: 0.65rem;
  color: var(--text-muted, #64748b);
  text-align: center;
  line-height: 1.2;
}

.fc-temps {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
}

.fc-max {
  font-size: 0.9rem;
  font-weight: 700;
  color: #D97706;
  line-height: 1.2;
}

.fc-min {
  font-size: 0.75rem;
  font-weight: 500;
  color: #60A5FA;
  line-height: 1.2;
}

.fc-rain {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 0.65rem;
  color: #60A5FA;
  font-weight: 600;
}

.fc-empty {
  font-size: 0.85rem;
  color: var(--text-muted, #64748b);
  font-style: italic;
}

/* Disease panel */
.rm-highlight {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  margin-bottom: 1.25rem;
  padding: 1rem;
  border-radius: 10px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.rm-label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted, #64748b);
}

.rm-value {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1.1;
}

.rm-value.risk-low    { color: #22c55e; }
.rm-value.risk-medium { color: #F59E0B; }
.rm-value.risk-high   { color: #EF4444; }

.rm-sub {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
}

.risk-bar-track {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.4rem;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s;
}

.risk-bar-fill.risk-low    { background: #22c55e; }
.risk-bar-fill.risk-medium { background: #F59E0B; }
.risk-bar-fill.risk-high   { background: #EF4444; }

.virus-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.virus-row {
  display: grid;
  grid-template-columns: 110px 1fr 44px;
  align-items: center;
  gap: 0.6rem;
}

.virus-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main, #0f172a);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.virus-bar-track {
  height: 7px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.virus-bar-fill {
  height: 100%;
  background: var(--primary-color, #3B82F6);
  border-radius: 4px;
  transition: width 0.4s;
}

.virus-count {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted, #64748b);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.epid-source {
  font-size: 0.68rem;
  color: var(--text-muted, #64748b);
  margin: 0.75rem 0 0;
  font-style: italic;
}

@media (max-width: 900px) {
  .contexto-row { grid-template-columns: 1fr; }
  .forecast-strip { grid-template-columns: repeat(4, 1fr); }
  .forecast-strip .forecast-day:nth-child(n+5) { display: none; }
  .virus-row { grid-template-columns: 90px 1fr 36px; }
}

/* ── Sub-view tabs (global / por curso) ── */
.sub-view-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.75rem;
}

.sub-tab-btn {
  padding: 0.5rem 1.1rem;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  background: var(--bg-color, #fff);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text-muted, #64748b);
  cursor: pointer;
  transition: all 0.2s;
}
.sub-tab-btn:hover { border-color: var(--primary-color, #3B82F6); color: var(--primary-color, #3B82F6); }
.sub-tab-btn.active {
  background: var(--primary-color, #3B82F6);
  border-color: var(--primary-color, #3B82F6);
  color: #fff;
}

.kpi-3 { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }

/* ── Risk pills ── */
.risk-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.22rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}
.risk-alto   { background: #fee2e2; color: #991b1b; }
.risk-medio  { background: #fef9c3; color: #92400e; }
.risk-bajo   { background: #dcfce7; color: #166534; }

.risk-legend {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-shrink: 0;
}

/* Row highlights in risk table */
.risk-row-alto { background: #fff5f5; }
.risk-row-medio { background: #fffbeb; }

.table-responsive {
  overflow-x: auto;
}

.code-hint {
  font-family: monospace;
  font-size: 0.85rem;
  background: #f1f5f9;
  padding: 0.3rem 0.65rem;
  border-radius: 5px;
  color: #334155;
  margin-top: 0.75rem;
  display: inline-block;
}

.proyeccion-note {
  font-size: 0.78rem;
  color: var(--text-muted, #64748b);
  font-style: italic;
  margin-top: 1rem;
  text-align: center;
}
</style>
