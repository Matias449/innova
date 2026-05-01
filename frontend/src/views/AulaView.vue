<template>
  <div class="subpage">
    <main class="dashboard-container">
      <section class="section-header">
        <div class="header-titles">
          <h2>Aula Diaria</h2>
          <p>Herramientas de gestión diaria para educadoras.</p>
        </div>
        <div class="custom-selector">
          <label>Curso actual: </label>
          <div class="dropdown-wrapper">
            <button class="selector-btn" @click="courseDropdownOpen = !courseDropdownOpen">
              <span class="selector-text">{{ selectedCurso || 'Seleccionar curso...' }}</span>
              <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            
            <div v-if="courseDropdownOpen" class="dropdown-overlay" @click="courseDropdownOpen = false"></div>
            
            <div v-if="courseDropdownOpen" class="dropdown-menu">
              <div class="search-box">
                <input type="text" v-model="courseSearch" placeholder="Escribe para buscar..." class="dropdown-search" autofocus />
              </div>
              <ul class="dropdown-list">
                <li v-for="curso in filteredCursos" :key="curso" @click="selectCurso(curso)" :class="{ active: selectedCurso === curso }">
                  {{ curso }}
                </li>
                <li v-if="filteredCursos.length === 0" class="empty-list">No se encontraron cursos.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <div v-if="!selectedCurso" class="empty-state">
        Por favor, selecciona un curso para comenzar tu jornada.
      </div>

      <div v-else class="aula-grid">
        <!-- SECCIÓN 1: PLANIFICACIÓN -->
        <div class="card panel-card">
          <div class="panel-header">
            <h3>Planificación del Día</h3>
            <input type="date" v-model="selectedPlanDate" @change="fetchPlanificacion" class="date-picker-input" />
          </div>
          <textarea 
            v-model="planificacion" 
            placeholder="Ej: A las 09:00 hrs círculo de bienvenida. Luego, actividad de motricidad fina con plasticina..."
            class="plan-textarea"
          ></textarea>
          <button class="btn-primary mt-2" @click="guardarPlanificacion" :disabled="savingPlan">
            {{ savingPlan ? 'Guardando...' : 'Guardar Planificación' }}
          </button>
        </div>

        <!-- SECCIÓN 2: ASISTENCIA (Flujo Interactivo 1 a 1) -->
        <div class="card panel-card">
          <div class="panel-header">
            <h3>Registro de Asistencia</h3>
          </div>
          
          <div class="asistencia-intro">
            <p class="text-muted mb-3">Toma asistencia preguntando a viva voz. Al iniciar se abrirá un modo enfocado para evitar distracciones.</p>
            <button class="btn-action w-100" @click="iniciarAsistencia">Iniciar Registro de Asistencia</button>
          </div>
        </div>

        <!-- SECCIÓN 3: LISTA DE ESTUDIANTES DEL DÍA -->
        <div class="card panel-card full-width">
          <div class="panel-header">
            <h3>Estudiantes del Día</h3>
            <span class="fecha-hoy">{{ fechaHoyStr }}</span>
          </div>
          <div v-if="asistenciaHoy.length === 0" class="lista-estado-vacio">
            <p>No hay asistencia registrada para hoy. Inicia el registro con el botón de arriba.</p>
          </div>
          <div v-else class="lista-estudiantes-grid">
            <div
              v-for="reg in asistenciaHoy"
              :key="reg.nino_id"
              :class="['estudiante-chip', reg.estado.toLowerCase()]"
            >
              <div class="chip-avatar">{{ reg.nombres.charAt(0) }}{{ reg.apellidos.charAt(0) }}</div>
              <div class="chip-info">
                <span class="chip-nombre">{{ reg.apellidos }}, {{ reg.nombres }}</span>
                <span :class="['chip-badge', reg.estado.toLowerCase()]">
                  {{ reg.estado }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- SECCIÓN 4: BITÁCORAS / ANOTACIONES -->
        <div class="card panel-card full-width">
          <div class="panel-header">
            <h3>Anotación de Desarrollo</h3>
          </div>
          <p class="text-muted mb-2">Registra un hito o incidente para la ficha de un niño.</p>
          
          <div class="form-group custom-selector w-100">
            <label>Seleccionar Niño:</label>
            <div class="dropdown-wrapper w-100 mt-2">
              <button class="selector-btn w-100" @click="ninoDropdownOpen = !ninoDropdownOpen">
                <span class="selector-text">{{ selectedNinoName }}</span>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              
              <div v-if="ninoDropdownOpen" class="dropdown-overlay" @click="ninoDropdownOpen = false"></div>
              
              <div v-if="ninoDropdownOpen" class="dropdown-menu w-100">
                <div class="search-box">
                  <input type="text" v-model="ninoSearch" placeholder="Buscar por nombre o apellido..." class="dropdown-search" autofocus />
                </div>
                <ul class="dropdown-list">
                  <li v-for="nino in filteredEstudiantes" :key="nino.id" @click="selectNino(nino)" :class="{ active: anotacion.nino_id === nino.id }">
                    <div class="nino-list-item">
                      <div class="mini-avatar">{{ iniciales(nino) }}</div>
                      <span>{{ nino.apellidos }}, {{ nino.nombres }}</span>
                    </div>
                  </li>
                  <li v-if="filteredEstudiantes.length === 0" class="empty-list">No se encontraron estudiantes.</li>
                </ul>
              </div>
            </div>
          </div>
          
          <div class="form-group mt-2">
            <label>Observación:</label>
            <textarea 
              v-model="anotacion.descripcion" 
              placeholder="Ej: Hoy logró compartir sus juguetes con sus compañeros de forma autónoma..."
              class="plan-textarea short"
            ></textarea>
          </div>
          
          <button class="btn-primary mt-2" @click="guardarAnotacion" :disabled="!anotacion.nino_id || !anotacion.descripcion || savingAnotacion">
            {{ savingAnotacion ? 'Guardando...' : 'Guardar Anotación' }}
          </button>
        </div>

      </div>
    </main>

    <!-- Modal de Asistencia Enfocada -->
    <div v-if="asistenciaModalOpen" class="attendance-modal">
      <div class="modal-content">
        <button class="close-modal-btn" @click="cancelarAsistencia">&times;</button>
        
        <!-- Flujo 1 a 1 -->
        <div v-if="!asistenciaFinalizada" class="asistencia-flow">
          <div class="modal-header">
            <h3>Registro de Asistencia</h3>
            <p>{{ selectedCurso }} - {{ fechaHoyStr }}</p>
          </div>
          
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progresoAsistencia + '%' }"></div>
          </div>
          <p class="progress-text">Niño {{ currentIndex + 1 }} de {{ estudiantes.length }}</p>
          
          <div class="estudiante-card">
            <div class="avatar-placeholder big">{{ iniciales(estudianteActual) }}</div>
            <h2 class="estudiante-nombre">{{ estudianteActual.nombres }}</h2>
            <h3 class="estudiante-apellido">{{ estudianteActual.apellidos }}</h3>
          </div>

          <div class="action-buttons">
            <button class="btn-ausente" @click="registrar('Ausente')">Ausente</button>
            <button class="btn-atraso" @click="registrar('Atraso')">Atraso</button>
            <button class="btn-presente" @click="registrar('Presente')">Presente</button>
          </div>
          
          <button v-if="currentIndex > 0" class="btn-back mt-4" @click="volverAtras">
            ← Deshacer y volver al alumno anterior
          </button>
        </div>

        <!-- Resumen Final -->
        <div v-else class="asistencia-summary-modal">
          <div class="modal-header">
            <h3>Registro Completado</h3>
            <p>Revisa el resumen antes de enviarlo oficialmente.</p>
          </div>
          
          <div class="summary-grid">
            <div class="summary-box presente">
              <span class="num">{{ countAsistencia('Presente') }}</span>
              <span>Presentes</span>
            </div>
            <div class="summary-box ausente">
              <span class="num">{{ countAsistencia('Ausente') }}</span>
              <span>Ausentes</span>
            </div>
            <div class="summary-box atraso">
              <span class="num">{{ countAsistencia('Atraso') }}</span>
              <span>Atrasos</span>
            </div>
          </div>

          <div class="summary-detail-table">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Estudiante</th>
                  <th>Estado Marcado</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reg in registrosTemporales" :key="reg.nino_id">
                  <td>{{ reg.nombre }}</td>
                  <td>
                    <span :class="['badge', reg.estado.toLowerCase()]">
                      {{ reg.estado }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="modal-actions mt-4">
            <button class="btn-back" @click="volverAtrasDesdeResumen">← Corregir al último alumno</button>
            <button class="btn-primary" @click="guardarAsistenciaEnBD" :disabled="savingAsistencia">
              {{ savingAsistencia ? 'Guardando...' : 'Confirmar y Guardar Asistencia' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api'

const cursosDisponibles = ref(['Medio Menor A', 'Medio Menor B', 'Medio Mayor A', 'Medio Mayor B'])
const selectedCurso = ref('')
const courseSearch = ref('')
const courseDropdownOpen = ref(false)

const filteredCursos = computed(() => {
  if (!courseSearch.value) return cursosDisponibles.value
  return cursosDisponibles.value.filter(c => c.toLowerCase().includes(courseSearch.value.toLowerCase()))
})

const selectCurso = (curso) => {
  selectedCurso.value = curso
  courseDropdownOpen.value = false
  courseSearch.value = ''
  fetchData()
}

const estudiantes = ref([])
const planificacion = ref('')
const savingPlan = ref(false)

// Estado de Asistencia
const asistenciaModalOpen = ref(false)
const asistenciaFinalizada = ref(false)
const currentIndex = ref(0)
const registrosTemporales = ref([])
const savingAsistencia = ref(false)

// Lista asistencia del día
const asistenciaHoy = ref([])

const fetchAsistenciaHoy = async () => {
  if (!selectedCurso.value) return
  try {
    const res = await fetch(`${API_BASE_URL}/aula/asistencia/dia/?curso=${encodeURIComponent(selectedCurso.value)}&fecha=${fechaHoyISO}`)
    if (res.ok) asistenciaHoy.value = await res.json()
  } catch (e) {
    console.error('Error fetching asistencia del día:', e)
  }
}

// Estado de Anotación
const anotacion = ref({ nino_id: '', descripcion: '' })
const savingAnotacion = ref(false)
const ninoSearch = ref('')
const ninoDropdownOpen = ref(false)

const filteredEstudiantes = computed(() => {
  if (!ninoSearch.value) return estudiantes.value
  const query = ninoSearch.value.toLowerCase()
  return estudiantes.value.filter(n => 
    n.nombres.toLowerCase().includes(query) || 
    n.apellidos.toLowerCase().includes(query)
  )
})

const selectedNinoName = computed(() => {
  if (!anotacion.value.nino_id) return 'Seleccionar estudiante...'
  const n = estudiantes.value.find(e => e.id === anotacion.value.nino_id)
  return n ? `${n.nombres} ${n.apellidos}` : 'Seleccionar estudiante...'
})

const selectNino = (nino) => {
  anotacion.value.nino_id = nino.id
  ninoDropdownOpen.value = false
  ninoSearch.value = ''
}

const fechaHoy = new Date()
const fechaHoyStr = fechaHoy.toLocaleDateString('es-CL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
const fechaHoyISO = fechaHoy.toISOString().split('T')[0] // YYYY-MM-DD
const selectedPlanDate = ref(fechaHoyISO)

const fetchPlanificacion = async () => {
  if (!selectedCurso.value) return
  planificacion.value = ''
  try {
    const resPlan = await fetch(`${API_BASE_URL}/aula/planificaciones/?curso=${selectedCurso.value}&fecha=${selectedPlanDate.value}`)
    if (resPlan.ok) {
      const dataPlan = await resPlan.json()
      planificacion.value = dataPlan.actividades
    }
  } catch (error) {
    console.error("Error fetching plan:", error)
  }
}

const fetchData = async () => {
  if (!selectedCurso.value) return

  asistenciaModalOpen.value = false
  asistenciaFinalizada.value = false
  registrosTemporales.value = []

  try {
    const resEst = await fetch(`${API_BASE_URL}/aula/estudiantes/?curso=${encodeURIComponent(selectedCurso.value)}`)
    if (resEst.ok) estudiantes.value = await resEst.json()

    fetchPlanificacion()
    fetchAsistenciaHoy()
  } catch (error) {
    console.error("Error fetching data:", error)
  }
}

const guardarPlanificacion = async () => {
  savingPlan.value = true
  try {
    await fetch(`${API_BASE_URL}/aula/planificaciones/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        curso: selectedCurso.value,
        fecha: selectedPlanDate.value,
        actividades: planificacion.value
      })
    })
    alert('Planificación guardada con éxito.')
  } catch (e) {
    alert('Error al guardar planificación.')
  } finally {
    savingPlan.value = false
  }
}

// Lógica de Asistencia 1 a 1
const estudianteActual = computed(() => estudiantes.value[currentIndex.value])
const progresoAsistencia = computed(() => (currentIndex.value / estudiantes.value.length) * 100)

const iniciales = (nino) => {
  if (!nino) return ''
  return nino.nombres.charAt(0) + nino.apellidos.charAt(0)
}

const iniciarAsistencia = () => {
  if (estudiantes.value.length === 0) {
    alert("No hay estudiantes en este curso.")
    return
  }
  currentIndex.value = 0
  registrosTemporales.value = []
  asistenciaModalOpen.value = true
  asistenciaFinalizada.value = false
}

const cancelarAsistencia = () => {
  if (confirm("¿Seguro que deseas cancelar? Se perderá todo el progreso de la toma de asistencia actual.")) {
    asistenciaModalOpen.value = false
  }
}

const volverAtras = () => {
  if (currentIndex.value > 0) {
    registrosTemporales.value.pop()
    currentIndex.value--
  }
}

const volverAtrasDesdeResumen = () => {
  asistenciaFinalizada.value = false
  registrosTemporales.value.pop()
  currentIndex.value = estudiantes.value.length - 1
}

const registrar = (estado) => {
  registrosTemporales.value.push({
    nino_id: estudianteActual.value.id,
    nombre: `${estudianteActual.value.apellidos}, ${estudianteActual.value.nombres}`,
    estado: estado
  })
  
  if (currentIndex.value < estudiantes.value.length - 1) {
    currentIndex.value++
  } else {
    asistenciaFinalizada.value = true
  }
}

const countAsistencia = (estado) => registrosTemporales.value.filter(r => r.estado === estado).length

const guardarAsistenciaEnBD = async () => {
  savingAsistencia.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/aula/asistencia/bulk/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fecha: fechaHoyISO,
        registros: registrosTemporales.value
      })
    })
    if (res.ok) {
      alert("¡Asistencia registrada oficialmente!")
      asistenciaModalOpen.value = false
      fetchAsistenciaHoy()
    }
  } catch (e) {
    alert("Error al guardar asistencia.")
  } finally {
    savingAsistencia.value = false
  }
}

const guardarAnotacion = async () => {
  savingAnotacion.value = true
  try {
    const res = await fetch(`${API_BASE_URL}/aula/anotaciones/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        nino_id: anotacion.value.nino_id,
        fecha: fechaHoyISO,
        descripcion: anotacion.value.descripcion,
        autor: 'Educadora Principal' // MVP
      })
    })
    if (res.ok) {
      alert("Anotación registrada en la ficha del alumno.")
      anotacion.value.descripcion = '' // Limpiar form
      anotacion.value.nino_id = ''
    }
  } catch (e) {
    alert("Error al guardar anotación.")
  } finally {
    savingAnotacion.value = false
  }
}

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

/* Custom Selectors */
.custom-selector {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
  position: relative;
}

.dropdown-wrapper {
  position: relative;
}

.selector-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-main);
  cursor: pointer;
  min-width: 280px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  transition: all 0.2s;
}

.selector-btn:hover {
  border-color: var(--primary-color);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.dropdown-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 99;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  min-width: 100%;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  z-index: 100;
  overflow: hidden;
  animation: slideDown 0.2s ease-out forwards;
}

@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.search-box {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border-color);
  background-color: #f8fafc;
}

.dropdown-search {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  outline: none;
  font-family: inherit;
}

.dropdown-search:focus {
  border-color: var(--primary-color);
}

.dropdown-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 250px;
  overflow-y: auto;
}

.dropdown-list li {
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.1s;
}

.dropdown-list li:last-child { border-bottom: none; }

.dropdown-list li:hover { background-color: #f1f5f9; }

.dropdown-list li.active {
  background-color: #e0e7ff;
  color: var(--primary-color);
  font-weight: 600;
}

.empty-list {
  color: var(--text-muted);
  text-align: center;
  padding: 1.5rem !important;
  font-style: italic;
}

.nino-list-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.mini-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 700;
}

.w-100 { width: 100%; }

.aula-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.full-width {
  grid-column: 1 / -1;
}

.panel-card {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.panel-header h3 { margin: 0; color: var(--primary-color); }

.fecha-hoy {
  font-size: 0.85rem;
  color: var(--text-muted);
  text-transform: capitalize;
}

.date-picker-input {
  padding: 0.4rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: var(--bg-color);
  font-family: inherit;
  color: var(--text-main);
  font-weight: 500;
  outline: none;
}

.plan-textarea {
  width: 100%;
  min-height: 150px;
  padding: 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background-color: #f8fafc;
  resize: vertical;
  font-family: inherit;
  font-size: 0.95rem;
}

.plan-textarea.short { min-height: 80px; }

.btn-primary, .btn-action {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover, .btn-action:hover { background-color: #4f46e5; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background-color: transparent;
  color: var(--text-main);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
}

.asistencia-intro { text-align: center; padding: 2rem 0; }

.asistencia-flow {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background-color: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1.5rem; }

.estudiante-card {
  margin-bottom: 2rem;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #818cf8 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  margin: 0 auto 1rem;
}

.estudiante-nombre { margin: 0; font-size: 1.5rem; }
.estudiante-apellido { margin: 0; color: var(--text-muted); font-weight: 400; }

.action-buttons {
  display: flex;
  gap: 1rem;
  width: 100%;
  justify-content: center;
}

.btn-ausente, .btn-atraso, .btn-presente {
  padding: 1rem;
  border: none;
  border-radius: var(--radius-md);
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  flex: 1;
  transition: transform 0.1s, opacity 0.2s;
}

.btn-ausente:active, .btn-atraso:active, .btn-presente:active { transform: scale(0.95); }

.btn-ausente { background-color: #FEE2E2; color: #991B1B; }
.btn-atraso { background-color: #FEF9C3; color: #854D0E; }
.btn-presente { background-color: #DCFCE7; color: #166534; }

.btn-ausente:hover { background-color: #FCA5A5; }
.btn-atraso:hover { background-color: #FDE047; }
.btn-presente:hover { background-color: #86EFAC; }

.asistencia-summary {
  text-align: center;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: var(--radius-md);
}

.summary-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
  display: flex;
  justify-content: space-around;
}

.empty-state { text-align: center; padding: 4rem; color: var(--text-muted); font-size: 1.1rem; }

/* MODAL ASISTENCIA */
.attendance-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(15, 23, 42, 0.85);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-content {
  background: var(--bg-color);
  width: 100%;
  max-width: 650px;
  border-radius: var(--radius-lg);
  padding: 3rem;
  position: relative;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.close-modal-btn {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
}

.close-modal-btn:hover { color: #ef4444; }

.modal-header {
  text-align: center;
  margin-bottom: 2rem;
}

.modal-header h3 { margin: 0 0 0.5rem 0; font-size: 1.8rem; color: var(--text-main); }
.modal-header p { margin: 0; color: var(--primary-color); font-weight: 500; }

.avatar-placeholder.big {
  width: 120px;
  height: 120px;
  font-size: 3.5rem;
}

.btn-back {
  background: none;
  border: none;
  color: var(--text-muted);
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 1rem;
  transition: color 0.2s;
}

.btn-back:hover {
  color: var(--text-main);
  text-decoration: underline;
}

.summary-grid {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
  margin: 2.5rem 0;
}

.summary-box {
  flex: 1;
  padding: 2rem 1rem;
  border-radius: var(--radius-md);
  text-align: center;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.summary-box.presente { background: #DCFCE7; color: #166534; border: 1px solid #BBF7D0; }
.summary-box.ausente { background: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
.summary-box.atraso { background: #FEF9C3; color: #854D0E; border: 1px solid #FEF08A; }

.summary-box .num {
  font-size: 3rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.summary-detail-table {
  max-height: 250px;
  overflow-y: auto;
  margin-bottom: 1.5rem;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: var(--radius-md);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th, .data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.data-table th {
  background-color: #f8fafc;
  position: sticky;
  top: 0;
  z-index: 1;
  font-weight: 600;
  color: var(--text-main);
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge.presente { background: #DCFCE7; color: #166534; }
.badge.ausente { background: #FEE2E2; color: #991B1B; }
.badge.atraso { background: #FEF9C3; color: #854D0E; }

.modal-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.lista-estado-vacio {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-style: italic;
  background: #f8fafc;
  border-radius: var(--radius-md);
}

.lista-estudiantes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.75rem;
}

.estudiante-chip {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  background: #f8fafc;
  transition: box-shadow 0.15s;
}

.estudiante-chip:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.07); }

.estudiante-chip.presente { border-left: 4px solid #22c55e; background: #f0fdf4; }
.estudiante-chip.ausente { border-left: 4px solid #ef4444; background: #fef2f2; }
.estudiante-chip.atraso { border-left: 4px solid #f59e0b; background: #fffbeb; }
.estudiante-chip.justificado { border-left: 4px solid #6366f1; background: #eef2ff; }

.chip-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.chip-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}

.chip-nombre {
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-main);
}

.chip-badge {
  font-size: 0.75rem;
  font-weight: 600;
}

.chip-badge.presente { color: #166534; }
.chip-badge.ausente { color: #991b1b; }
.chip-badge.atraso { color: #92400e; }
.chip-badge.justificado { color: #3730a3; }

@media (max-width: 768px) {
  .aula-grid { grid-template-columns: 1fr; }
  .action-buttons { flex-direction: column; }
  .modal-content { padding: 1.5rem; }
  .summary-grid { flex-direction: column; }
  .modal-actions { flex-direction: column; }
  .lista-estudiantes-grid { grid-template-columns: 1fr; }
}
</style>
