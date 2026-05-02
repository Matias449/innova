<template>
  <div class="subpage">
    <main class="dashboard-container">
      <section class="section-header">
        <div class="header-titles">
          <h2>Salud Financiera</h2>
          <p>Monitoreo de ingresos, egresos y rentabilidad institucional.</p>
        </div>
        <button class="btn-secondary" @click="fetchData" :disabled="loading">
          {{ loading ? 'Actualizando...' : 'Actualizar Datos' }}
        </button>
      </section>

      <div v-if="loading && !data" class="loading-state">
        <div class="spinner"></div>
        <p>Calculando balances...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>Error al cargar los datos financieros.</p>
      </div>

      <div v-else class="finanzas-grid">
        <!-- Subsidio proyectado -->
        <div v-if="subsidioProyectado" class="card subsidio-card">
          <div class="subsidio-header">
            <div>
              <h3>Proyección de Subsidio — {{ subsidioProyectado.mes }}</h3>
              <p class="subsidio-note">Valor parvulario JUNJI estimado: {{ formatMoney(VALOR_PARVULO) }} · Ajustar según tabla vigente</p>
            </div>
            <span class="subsidio-badge" :class="subsidioProyectado.tasa >= 85 ? 'badge-green' : 'badge-amber'">
              Tasa proyectada: {{ subsidioProyectado.tasa }}%
            </span>
          </div>
          <div class="subsidio-kpis">
            <div class="subsidio-kpi">
              <span class="subsidio-kpi-label">Subsidio Estimado</span>
              <span class="subsidio-kpi-value">{{ formatMoney(subsidioProyectado.estimado) }}</span>
              <span class="subsidio-kpi-sub">{{ subsidioProyectado.matriculados }} matriculados · {{ subsidioProyectado.diasHabiles }} días hábiles</span>
            </div>
            <div class="subsidio-kpi" v-if="subsidioProyectado.mesAnterior">
              <span class="subsidio-kpi-label">Último Mes Real</span>
              <span class="subsidio-kpi-value muted">{{ formatMoney(subsidioProyectado.mesAnterior) }}</span>
              <span class="subsidio-kpi-sub">subsidio registrado</span>
            </div>
            <div class="subsidio-kpi" v-if="subsidioProyectado.mesAnterior">
              <span class="subsidio-kpi-label">Diferencia Proyectada</span>
              <span class="subsidio-kpi-value" :class="subsidioProyectado.diferencia >= 0 ? 'value-pos' : 'value-neg'">
                {{ subsidioProyectado.diferencia >= 0 ? '+' : '' }}{{ formatMoney(subsidioProyectado.diferencia) }}
              </span>
              <span class="subsidio-kpi-sub">vs. mes anterior</span>
            </div>
          </div>
        </div>

        <!-- KPIs -->
        <div class="kpi-container">
          <div class="kpi-card income">
            <h3>Ingresos Totales (YTD)</h3>
            <div class="kpi-value">{{ formatMoney(kpis.totalIngresos) }}</div>
            <p class="kpi-trend positive">↑ En línea con el presupuesto</p>
          </div>
          <div class="kpi-card expense">
            <h3>Egresos Totales (YTD)</h3>
            <div class="kpi-value">{{ formatMoney(kpis.totalEgresos) }}</div>
            <p class="kpi-trend warning">Cuidado con gastos imprevistos</p>
          </div>
          <div class="kpi-card balance" :class="{ negative: kpis.balanceNeto < 0 }">
            <h3>Balance Neto</h3>
            <div class="kpi-value">{{ formatMoney(kpis.balanceNeto) }}</div>
            <p class="kpi-trend">Margen de {{ kpis.margen }}%</p>
          </div>
        </div>

        <!-- Gráfico Mixto -->
        <div class="card chart-card">
          <div class="chart-header">
            <h3>Ingresos vs Egresos (Ene - Ago)</h3>
            <p class="text-muted"><small>La línea azul representa la ganancia neta mensual.</small></p>
          </div>
          <div class="chart-container">
            <Chart type="bar" :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Tabla Desglose -->
        <div class="card table-card">
          <div class="chart-header">
            <h3>Desglose Financiero Mensual</h3>
          </div>
          <div class="table-responsive">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Mes</th>
                  <th>Matrículas (Ingreso)</th>
                  <th>Subsidios (Ingreso)</th>
                  <th>Sueldos (Egreso)</th>
                  <th>Insumos (Egreso)</th>
                  <th>Imprevistos (Egreso)</th>
                  <th>Balance Final</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="mes in data" :key="mes.mes">
                  <td><strong>{{ mes.mes }}</strong></td>
                  <td class="text-success">{{ formatMoney(mes.matriculas) }}</td>
                  <td class="text-success">{{ formatMoney(mes.subsidios) }}</td>
                  <td class="text-danger">{{ formatMoney(mes.sueldos) }}</td>
                  <td class="text-danger">{{ formatMoney(mes.insumos) }}</td>
                  <td class="text-danger" :class="{ 'warning-bg': mes.imprevistos > 0 }">{{ formatMoney(mes.imprevistos) }}</td>
                  <td :class="mes.balance >= 0 ? 'text-success' : 'text-danger'">
                    <strong>{{ formatMoney(mes.balance) }}</strong>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
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
  Title,
  Tooltip,
  Legend,
  LineController,
  BarController
} from 'chart.js'
import { Chart } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  LineController,
  BarController
)

const API_BASE_URL = 'http://localhost:8000/api'
const data = ref(null)
const loading = ref(true)
const error = ref(false)
const mlPrediccion = ref(null)
const ninosCount = ref(0)

const VALOR_PARVULO = 560000

const fetchData = async () => {
  loading.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/finanzas/dashboard/`)
    if (res.ok) {
      data.value = await res.json()
    } else {
      error.value = true
    }
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}

const fetchSubsidioData = async () => {
  try {
    const [mlRes, ninosRes] = await Promise.all([
      fetch(`${API_BASE_URL}/ml/prediccion/`),
      fetch(`${API_BASE_URL}/ninos/`),
    ])
    if (mlRes.ok) mlPrediccion.value = await mlRes.json()
    if (ninosRes.ok) {
      const ninos = await ninosRes.json()
      ninosCount.value = Array.isArray(ninos) ? ninos.length : (ninos.count || 0)
    }
  } catch { /* silent */ }
}

onMounted(() => {
  fetchData()
  fetchSubsidioData()
})

const formatMoney = (amount) => {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(amount)
}

const kpis = computed(() => {
  if (!data.value) return { totalIngresos: 0, totalEgresos: 0, balanceNeto: 0, margen: 0 }

  const totalIngresos = data.value.reduce((acc, curr) => acc + curr.ingreso_total, 0)
  const totalEgresos = data.value.reduce((acc, curr) => acc + curr.egreso_total, 0)
  const balanceNeto = totalIngresos - totalEgresos
  const margen = totalIngresos > 0 ? Math.round((balanceNeto / totalIngresos) * 100) : 0

  return { totalIngresos, totalEgresos, balanceNeto, margen }
})

const subsidioProyectado = computed(() => {
  if (!mlPrediccion.value?.model_a) return null
  const { tasa_predicha, mes_predicho, dias_habiles } = mlPrediccion.value.model_a
  const matriculados = ninosCount.value
  const diasHabiles = dias_habiles || 22
  const estimado = Math.round(VALOR_PARVULO * (tasa_predicha / 100) * matriculados * diasHabiles)

  let mesAnterior = null
  let diferencia = null
  if (data.value && data.value.length > 0) {
    const ultimo = data.value[data.value.length - 1]
    mesAnterior = ultimo.subsidios || 0
    diferencia = estimado - mesAnterior
  }

  return {
    mes: mes_predicho,
    tasa: tasa_predicha,
    estimado,
    matriculados,
    diasHabiles,
    mesAnterior,
    diferencia,
  }
})

const chartData = computed(() => {
  if (!data.value) return { labels: [], datasets: [] }
  
  return {
    labels: data.value.map(d => d.mes),
    datasets: [
      {
        type: 'line',
        label: 'Balance Neto',
        borderColor: '#0EA5E9',
        backgroundColor: '#0EA5E9',
        borderWidth: 3,
        pointBackgroundColor: '#ffffff',
        pointBorderColor: '#0EA5E9',
        pointRadius: 5,
        tension: 0.3,
        data: data.value.map(d => d.balance)
      },
      {
        type: 'bar',
        label: 'Ingresos Totales',
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
        borderRadius: 4,
        data: data.value.map(d => d.ingreso_total)
      },
      {
        type: 'bar',
        label: 'Egresos Totales',
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderRadius: 4,
        data: data.value.map(d => d.egreso_total)
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    tooltip: {
      backgroundColor: '#1E293B',
      padding: 12,
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(context.parsed.y);
          }
          return label;
        }
      }
    },
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 20
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#f1f5f9',
      },
      ticks: {
        callback: function(value) {
          if (value === 0) return '$0'
          return '$' + (value / 1000000) + 'M'
        }
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  }
}

</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.kpi-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.kpi-card {
  background: var(--bg-color);
  padding: 1.5rem;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.kpi-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: var(--text-muted);
}

.kpi-value {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-main);
  margin-bottom: 0.5rem;
  letter-spacing: -0.5px;
}

.kpi-trend {
  font-size: 0.85rem;
  margin: 0;
  font-weight: 600;
}

.kpi-trend.positive { color: #166534; }
.kpi-trend.warning { color: #854D0E; }
.kpi-trend.negative { color: #991B1B; }

.income .kpi-value { color: #15803d; }
.expense .kpi-value { color: #b91c1c; }
.balance .kpi-value { color: #0369a1; }
.balance.negative .kpi-value { color: #b91c1c; }

.chart-card, .table-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-header {
  margin-bottom: 1.5rem;
}

.chart-header h3 {
  margin: 0 0 0.25rem 0;
  color: var(--text-main);
}

.chart-container {
  height: 350px;
  width: 100%;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

.data-table th, .data-table td {
  padding: 1rem;
  text-align: right;
  border-bottom: 1px solid var(--border-color);
}

.data-table th:first-child, .data-table td:first-child {
  text-align: left;
}

.data-table th {
  background-color: var(--bg-color);
  font-weight: 600;
  color: var(--text-muted);
}

.data-table tbody tr:hover {
  background-color: #f1f5f9;
}

.text-success { color: #15803d; }
.text-danger { color: #b91c1c; }
.warning-bg { 
  background-color: #FEF9C3;
  font-weight: 700;
  border-radius: 4px;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: var(--text-muted);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin { 100% { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .kpi-container { grid-template-columns: 1fr; }
}

/* ── Subsidio proyectado card ── */
.subsidio-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 4px solid var(--primary-color, #3B82F6);
}

.subsidio-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.subsidio-header h3 {
  margin: 0 0 0.25rem 0;
  color: var(--text-main);
  font-size: 1rem;
}

.subsidio-note {
  font-size: 0.78rem;
  color: var(--text-muted);
  margin: 0;
}

.subsidio-badge {
  display: inline-block;
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
  flex-shrink: 0;
}
.badge-green { background: #dcfce7; color: #166534; }
.badge-amber { background: #fef9c3; color: #92400e; }

.subsidio-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
}

.subsidio-kpi {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.subsidio-kpi-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  color: var(--text-muted);
}

.subsidio-kpi-value {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--text-main);
  letter-spacing: -0.5px;
}

.subsidio-kpi-value.muted { color: var(--text-muted); }
.subsidio-kpi-value.value-pos { color: #15803d; }
.subsidio-kpi-value.value-neg { color: #b91c1c; }

.subsidio-kpi-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
}
</style>
