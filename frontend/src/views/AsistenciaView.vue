<template>
  <div class="subpage">
    <main class="dashboard-container">

      <section class="section-header">
        <div class="header-titles">
          <h2>Dashboard de Asistencia</h2>
          <p>Análisis histórico de presentismo por curso y período.</p>
        </div>
        <div class="view-tabs">
          <button :class="['tab-btn', { active: activeView === 'global' }]" @click="setView('global')">Vista Global</button>
          <button :class="['tab-btn', { active: activeView === 'curso' }]" @click="setView('curso')">Por Curso</button>
        </div>
      </section>

      <div v-if="loading" class="empty-state">Cargando datos del dashboard...</div>
      <div v-else-if="error" class="empty-state error-state">
        No se pudieron cargar los datos. Verifique que el servidor esté activo.
      </div>

      <!-- ───────── VISTA GLOBAL ───────── -->
      <div v-else-if="activeView === 'global'">
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
      <div v-else-if="activeView === 'curso'">
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

const activeView = ref('global')
const loading = ref(true)
const error = ref(false)
const loadingCurso = ref(false)

const globalData = ref({ tasa_global: 0, total_inasistencias: 0, total_atrasos: 0, evolucion: { labels: [], data: [] } })
const cursosData = ref([])
const cursoDetalleData = ref(null)

const selectedInterval = ref('diario')
const selectedIntervalCurso = ref('mensual')
const selectedCursoDetalle = ref('')

const setView = (view) => { activeView.value = view }

const setInterval = (interval) => {
  selectedInterval.value = interval
  fetchGlobal()
}

const setIntervalCurso = (interval) => {
  selectedIntervalCurso.value = interval
  fetchCursoDetalle(selectedCursoDetalle.value)
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

onMounted(async () => {
  loading.value = true
  await Promise.all([fetchGlobal(), fetchCursosPorCurso()])
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
</style>
