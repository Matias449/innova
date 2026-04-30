<template>
  <div class="subpage">
    <main class="dashboard-container">
      <section class="section-header">
        <div class="header-titles">
          <h2>📊 Dashboard de Asistencia Global</h2>
          <p>Monitoreo histórico y modelos predictivos de presentismo.</p>
        </div>
        <div class="filters">
          <div class="button-group">
            <button :class="['toggle-btn', { active: selectedInterval === 'mensual' }]" @click="setInterval('mensual')">Mensual</button>
            <button :class="['toggle-btn', { active: selectedInterval === 'semanal' }]" @click="setInterval('semanal')">Semanal</button>
            <button :class="['toggle-btn', { active: selectedInterval === 'diario' }]" @click="setInterval('diario')">Diario</button>
          </div>
          <select v-model="selectedCurso" @change="fetchDashboardData" class="filter-select ml-2">
            <option value="Todos">Todos los Cursos</option>
            <option v-for="curso in cursosDisponibles" :key="curso" :value="curso">{{ curso }}</option>
          </select>
        </div>
      </section>

      <div v-if="loading" class="empty-state">Cargando datos del dashboard...</div>
      <div v-else-if="error" class="empty-state">Error cargando el dashboard.</div>

      <div v-else>
        <!-- KPIs -->
        <div class="kpi-grid">
          <div class="card stat-card">
            <span class="label">Tasa de Asistencia Global</span>
            <span class="value" :class="{'text-danger': data.tasa_global < 85}">{{ data.tasa_global }}%</span>
          </div>
          <div class="card stat-card">
            <span class="label">Total Inasistencias</span>
            <span class="value text-warning">{{ data.total_inasistencias }}</span>
          </div>
          <div class="card stat-card">
            <span class="label">Total Atrasos</span>
            <span class="value text-info">{{ data.total_atrasos }}</span>
          </div>
        </div>

        <div class="dashboard-grid">
          <!-- Gráfico -->
          <div class="card chart-card">
            <div class="chart-header">
              <h3>Evolución de Asistencia</h3>
              <p class="text-muted"><small>💡 Haz clic y arrastra sobre una zona para hacer zoom profundo (Drag-to-Zoom). Usa los botones superiores para cambiar la resolución.</small></p>
            </div>
            <div class="chart-container">
              <Line :data="chartData" :options="chartOptions" />
            </div>
          </div>

          <!-- Alertas Predictivas -->
          <div class="card alert-card">
            <div class="alert-header">
              <svg width="24" height="24" fill="none" stroke="var(--primary-color)" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              <h3>Modelo Predictivo (IA)</h3>
            </div>
            <div class="alert-content">
              <p class="text-muted">El modelo de Machine Learning está analizando los datos históricos de asistencia...</p>
              
              <div class="predictive-insight warning">
                <strong>Alerta Temprana Simulada:</strong>
                <p>Se proyecta una baja de 15% en la asistencia para la tercera semana de Junio debido a un aumento esperado de enfermedades respiratorias. Se recomienda iniciar campaña preventiva.</p>
              </div>
              
              <div class="predictive-insight info mt-2">
                <strong>Insight de Curso:</strong>
                <p>El curso <em>Medio Menor A</em> tiene la mayor variabilidad de asistencia los días Viernes.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import zoomPlugin from 'chartjs-plugin-zoom'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  zoomPlugin
)

const API_BASE_URL = 'http://localhost:8000/api'
const loading = ref(true)
const error = ref(false)
const data = ref(null)
const selectedCurso = ref('Todos')
const selectedInterval = ref('diario')
const cursosDisponibles = ref([])

const setInterval = (interval) => {
  selectedInterval.value = interval
  fetchDashboardData()
}

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/asistencia/dashboard/?curso=${selectedCurso.value}&intervalo=${selectedInterval.value}`)
    if (res.ok) {
      data.value = await res.json()
      if (selectedCurso.value === 'Todos') {
        cursosDisponibles.value = data.value.cursos_disponibles
      }
    } else {
      error.value = true
    }
  } catch (e) {
    console.error(e)
    error.value = true
  } finally {
    loading.value = false
  }
}

const chartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  
  const isDiario = selectedInterval.value === 'diario'
  const isSemanal = selectedInterval.value === 'semanal'
  
  return {
    labels: data.value.evolucion.labels,
    datasets: [
      {
        label: 'Tasa de Asistencia (%)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3B82F6',
        pointBackgroundColor: '#ffffff',
        pointBorderColor: '#3B82F6',
        pointBorderWidth: isDiario ? 0 : 2,
        pointRadius: isDiario ? 0 : (isSemanal ? 2 : 4),
        pointHoverRadius: isDiario ? 4 : 6,
        borderWidth: isDiario ? 1.5 : 2,
        fill: true,
        tension: isDiario ? 0.1 : 0.4,
        data: data.value.evolucion.data
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: '#1E293B',
      padding: 10,
      titleFont: { size: 14 },
      bodyFont: { size: 13 }
    },
    zoom: {
      pan: {
        enabled: true,
        mode: 'x',
      },
      zoom: {
        drag: {
          enabled: true,
          backgroundColor: 'rgba(59, 130, 246, 0.3)'
        },
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'x',
      }
    }
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: {
        callback: function(value) {
          return value + '%'
        }
      },
      grid: {
        color: '#E2E8F0',
        borderDash: [5, 5]
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

onMounted(() => {
  fetchDashboardData()
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

.filters {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  flex-wrap: wrap;
}

.button-group {
  display: flex;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 600;
  color: var(--text-muted);
  transition: all 0.2s;
  border-right: 1px solid var(--border-color, #e0e0e0);
}

.toggle-btn:last-child {
  border-right: none;
}

.toggle-btn:hover {
  background-color: #f1f5f9;
}

.toggle-btn.active {
  background-color: var(--primary-color);
  color: white;
}

.ml-2 { margin-left: 0.5rem; }

.filter-select {
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color, #e0e0e0);
  background-color: var(--bg-color);
  font-family: inherit;
  font-weight: 500;
  color: var(--text-main);
  outline: none;
  cursor: pointer;
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  text-align: center;
  padding: 1.5rem;
}

.stat-card .label {
  display: block;
  font-size: 0.9rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.stat-card .value {
  display: block;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
}

.text-danger { color: #EF4444 !important; }
.text-warning { color: #F59E0B !important; }
.text-info { color: #0EA5E9 !important; }

.dashboard-grid {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.chart-header h3 {
  margin: 0;
  color: var(--text-main);
}

.chart-container {
  position: relative;
  height: 400px;
  width: 100%;
}

.alert-card {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border: 1px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.alert-header h3 {
  color: var(--primary-color);
  margin: 0;
}

.predictive-insight {
  padding: 1rem;
  border-radius: var(--radius-md);
  margin-top: 1rem;
  font-size: 0.9rem;
}

.predictive-insight.warning {
  background-color: #FEF2F2;
  border-left: 4px solid #EF4444;
}

.predictive-insight.warning strong {
  color: #B91C1C;
  display: block;
  margin-bottom: 0.25rem;
}

.predictive-insight.info {
  background-color: #EFF6FF;
  border-left: 4px solid #3B82F6;
}

.predictive-insight.info strong {
  color: #1D4ED8;
  display: block;
  margin-bottom: 0.25rem;
}

.mt-2 { margin-top: 1rem; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-style: italic;
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>