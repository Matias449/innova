<template>
  <div class="subpage">
    <main class="dashboard-container">
      <div v-if="loading" class="empty-state">Cargando ficha detallada...</div>
      
      <div v-else-if="nino" class="detail-wrapper">
        <section class="section-header">
          <div class="header-titles">
            <h2>Ficha de {{ nino.nombres }} {{ nino.apellidos }}</h2>
            <p>Curso: <span class="curso-badge">{{ nino.curso }}</span></p>
          </div>
          <button class="btn-secondary" @click="$router.push('/ninos')">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 5px;">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            Volver a la lista
          </button>
        </section>

        <div class="detail-grid">
          <!-- Información Personal -->
          <div class="card info-card">
            <h3>Información Personal</h3>
            <ul class="info-list">
              <li><strong>RUT:</strong> {{ nino.rut }}</li>
              <li><strong>Fecha Nacimiento:</strong> {{ nino.fecha_nacimiento }}</li>
              <li><strong>Apoderado Principal:</strong> {{ nino.apoderado_principal }}</li>
            </ul>
          </div>

          <!-- Antecedentes Médicos y Familiares -->
          <div class="card medical-card">
            <h3>Antecedentes Especiales</h3>
            <div class="bg-gray p-3 rounded mt-2">
              <p><strong>Enfermedades:</strong> {{ nino.enfermedades || 'Ninguna registrada' }}</p>
              <p><strong>Alergias:</strong> {{ nino.alergias || 'Ninguna registrada' }}</p>
              <p><strong>Situación Familiar:</strong> {{ nino.situacion_familiar || 'Sin observaciones' }}</p>
            </div>
          </div>

          <!-- Historial de Asistencia -->
          <div class="card attendance-card">
            <h3>Historial de Asistencia (Últimos días)</h3>
            <div v-if="nino.asistencias && nino.asistencias.length > 0">
              <ul class="doc-list">
                <li v-for="asist in nino.asistencias.slice(0,5)" :key="asist.id">
                  <span>📅 {{ asist.fecha }}</span>
                  <span :class="['status-pill', getStatusClass(asist.estado)]">{{ asist.estado }}</span>
                </li>
              </ul>
            </div>
            <p v-else class="text-muted">No hay registros de asistencia.</p>
          </div>

          <!-- Bitácora de Desarrollo -->
          <div class="card annotations-card">
            <h3>Bitácora de Desarrollo</h3>
            <div v-if="nino.anotaciones && nino.anotaciones.length > 0" class="timeline">
              <div v-for="nota in nino.anotaciones" :key="nota.id" class="timeline-item">
                <div class="timeline-date">{{ nota.fecha }}</div>
                <div class="timeline-content">
                  <p>{{ nota.descripcion }}</p>
                  <small>Por: {{ nota.autor }}</small>
                </div>
              </div>
            </div>
            <p v-else class="text-muted">No hay anotaciones de desarrollo registradas.</p>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <p>No se pudo cargar la información del estudiante.</p>
        <button class="btn-primary mt-2" @click="$router.push('/ninos')">Volver al listado</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const nino = ref(null)
const loading = ref(true)

const API_BASE_URL = 'http://localhost:8000/api'

const fetchNinoDetail = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/ninos/${route.params.id}/`)
    if (res.ok) {
      nino.value = await res.json()
    }
  } catch (error) {
    console.error("Error fetching nino detail:", error)
  } finally {
    loading.value = false
  }
}

const getStatusClass = (estado) => {
  if (estado === 'Presente') return 'present'
  if (estado === 'Ausente') return 'absent'
  return 'late'
}

onMounted(() => {
  fetchNinoDetail()
})
</script>

<style scoped>
.detail-wrapper {
  animation: fadeIn 0.3s ease;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.curso-badge {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: var(--border-color);
  color: var(--text-main);
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
}

.btn-secondary:hover {
  background-color: #cbd5e1;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.info-card, .medical-card, .attendance-card, .annotations-card {
  display: flex;
  flex-direction: column;
}

.annotations-card {
  grid-column: 1 / -1;
}

.info-list {
  list-style: none;
  padding: 0;
  margin-top: 1rem;
}

.info-list li {
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border-color);
}

.bg-gray {
  background-color: var(--bg-color);
}
.p-3 { padding: 1.25rem; }
.mt-2 { margin-top: 1rem; }
.rounded { border-radius: var(--radius-md); }
.text-muted { color: var(--text-muted); font-style: italic; }

/* Timeline for annotations */
.timeline {
  margin-top: 1.5rem;
  border-left: 2px solid var(--primary-color);
  padding-left: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.timeline-item {
  position: relative;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -1.95rem;
  top: 0.25rem;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background-color: var(--primary-color);
  border: 2px solid white;
}

.timeline-date {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 0.25rem;
}

.timeline-content {
  background-color: var(--bg-color);
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.timeline-content p {
  margin-bottom: 0.5rem;
}

.timeline-content small {
  color: var(--text-muted);
  font-weight: 500;
}

.status-pill.late { background: #FEF08A; color: #854D0E; }
.status-pill.justified { background: #E0F2FE; color: #0369A1; }

.empty-state {
  text-align: center;
  padding: 3rem;
  color: var(--text-muted);
  font-style: italic;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
