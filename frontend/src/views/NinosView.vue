<template>
  <div class="subpage">
    <main class="dashboard-container">
      <section class="section-header">
        <div class="header-titles">
          <h2>Información de Niños / Párvulos</h2>
          <p>Accede a la ficha y seguimiento de cada estudiante.</p>
        </div>
        <div class="header-actions">
          <button v-if="hasAccessTo.ninos_create" class="btn-primary" @click="showForm = !showForm">
            <svg v-if="!showForm" width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            <svg v-else width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
            {{ showForm ? 'Cerrar Formulario' : 'Nuevo Estudiante' }}
          </button>
          <button class="btn-export" @click="exportToExcel">
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Exportar a Excel
          </button>
        </div>
      </section>

      <!-- Formulario Desplegable -->
      <transition name="fade-slide">
        <div class="card form-card" v-if="showForm">
          <h3>Registrar Nuevo Estudiante</h3>
          <form @submit.prevent="createNino" class="nino-form">
            <div class="form-section-title full-width">Datos Personales</div>
            <div class="form-group">
              <label>Nombres</label>
              <input type="text" v-model="form.nombres" required />
            </div>
            <div class="form-group">
              <label>Apellidos</label>
              <input type="text" v-model="form.apellidos" required />
            </div>
            <div class="form-group">
              <label>RUT</label>
              <input type="text" v-model="form.rut" required placeholder="12.345.678-9" />
            </div>
            <div class="form-group">
              <label>Apoderado Principal</label>
              <input type="text" v-model="form.apoderado_principal" required />
            </div>
            <div class="form-group">
              <label>Fecha de Nacimiento</label>
              <input type="date" v-model="form.fecha_nacimiento" required />
            </div>
            <div class="form-group">
              <label>Curso / Nivel</label>
              <input type="text" v-model="form.curso" required />
            </div>
            <div class="form-group full-width">
              <label>Dirección del estudiante</label>
              <input type="text" v-model="form.direccion" placeholder="Ej: Av. Las Flores 123, Maipú" />
            </div>
            <div class="form-group full-width">
              <label>Observaciones</label>
              <textarea v-model="form.observaciones" rows="2"></textarea>
            </div>

            <div class="form-section-title full-width">Información Socioeconómica</div>
            <div class="form-group">
              <label>Quintil RSH <span class="label-hint">(Registro Social de Hogares)</span></label>
              <select v-model="form.quintil_rsh">
                <option :value="null">No informado</option>
                <option v-for="q in [1,2,3,4,5]" :key="q" :value="q">Quintil {{ q }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>N.° de hermanos</label>
              <input type="number" v-model.number="form.numero_hermanos" min="0" max="20" placeholder="0" />
            </div>
            <div class="form-group">
              <label>Situación laboral de los padres</label>
              <select v-model="form.situacion_laboral_padres">
                <option value="">No informado</option>
                <option value="ninguno">Ninguno con trabajo full time</option>
                <option value="uno">Un apoderado con trabajo full time</option>
                <option value="ambos">Ambos con trabajo full time</option>
              </select>
            </div>

            <div class="form-actions full-width">
              <button type="submit" class="btn-primary" style="width: auto;">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
                </svg>
                Guardar Estudiante
              </button>
            </div>
          </form>
        </div>
      </transition>

      <div class="card list-card">
        <div class="list-header">
          <h3>Lista de Estudiantes ({{ filteredAndSortedNinos.length }})</h3>
          <div class="filters">
            <div class="search-group">
              <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"></path>
              </svg>
              <input type="text" v-model="searchQuery" placeholder="Buscar por nombre..." class="search-input" />
            </div>
            <div class="filter-group">
              <label>Curso:</label>
              <select v-model="filterCurso" class="filter-select">
                <option v-for="curso in availableCursos" :key="curso" :value="curso">
                  {{ curso }}
                </option>
              </select>
            </div>
            <button class="btn-filter" :class="{ 'active': sortByLastName }" @click="sortByLastName = !sortByLastName" title="Ordenar alfabéticamente por apellido">
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"></path>
              </svg>
              {{ sortByLastName ? 'A-Z Activado' : 'Ordenar A-Z' }}
            </button>
          </div>
        </div>

        <div class="table-responsive" v-if="filteredAndSortedNinos.length > 0">
          <table class="data-table">
            <thead>
              <tr>
                <th>Nombres</th>
                <th>Apellidos</th>
                <th>RUT</th>
                <th>Apoderado</th>
                <th>Curso</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="nino in filteredAndSortedNinos" :key="nino.id" @click="$router.push('/ninos/' + nino.id)" class="clickable-row" title="Ver ficha detallada">
                <td>{{ nino.nombres }}</td>
                <td>{{ nino.apellidos }}</td>
                <td>{{ nino.rut }}</td>
                <td>{{ nino.apoderado_principal }}</td>
                <td><span class="curso-badge">{{ nino.curso }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-state">No hay estudiantes que coincidan con los filtros.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { hasAccessTo } = useAuth()
const API_BASE_URL = 'http://localhost:8000/api'
const ninos = ref([])
const showForm = ref(false)

// Filters State
const filterCurso = ref('Todos')
const sortByLastName = ref(false)
const searchQuery = ref('')

const form = ref({
  nombres: '',
  apellidos: '',
  rut: '',
  apoderado_principal: '',
  fecha_nacimiento: '',
  curso: '',
  observaciones: '',
  direccion: '',
  quintil_rsh: null,
  numero_hermanos: null,
  situacion_laboral_padres: ''
})

const availableCursos = computed(() => {
  const cursos = new Set(ninos.value.map(n => n.curso))
  return ['Todos', ...Array.from(cursos).sort()]
})

const filteredAndSortedNinos = computed(() => {
  let result = [...ninos.value]

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    result = result.filter(n =>
      n.nombres.toLowerCase().includes(q) ||
      n.apellidos.toLowerCase().includes(q)
    )
  }

  if (filterCurso.value !== 'Todos') {
    result = result.filter(n => n.curso === filterCurso.value)
  }

  if (sortByLastName.value) {
    result.sort((a, b) => a.apellidos.localeCompare(b.apellidos))
  }

  return result
})

const fetchNinos = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ninos/`)
    if (response.ok) {
      ninos.value = await response.json()
    } else {
      console.error('Error al cargar la lista de niños')
    }
  } catch (error) {
    console.error('Error de red:', error)
  }
}

const createNino = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ninos/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })
    
    if (response.ok) {
      form.value = {
        nombres: '', apellidos: '', rut: '', apoderado_principal: '',
        fecha_nacimiento: '', curso: '', observaciones: '',
        direccion: '', quintil_rsh: null, numero_hermanos: null, situacion_laboral_padres: ''
      }
      showForm.value = false // Ocultar form al guardar
      await fetchNinos()
      alert('Estudiante registrado con éxito')
    } else {
      alert('Error al registrar estudiante')
    }
  } catch (error) {
    console.error('Error al enviar el formulario:', error)
  }
}

const exportToExcel = () => {
  window.open(`${API_BASE_URL}/ninos/export/`, '_blank')
}

onMounted(() => {
  fetchNinos()
})
</script>

<style scoped>
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.form-card {
  margin-bottom: 2rem;
  overflow: hidden;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.4s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.filters {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color, #e0e0e0);
  background-color: var(--bg-color);
  color: var(--text-muted);
  transition: border-color 0.3s;
}

.search-group:focus-within {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 0.95rem;
  color: var(--text-main);
  width: 180px;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}

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
  transition: border-color 0.3s;
}

.filter-select:focus {
  border-color: var(--primary-color);
}

.btn-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color, #e0e0e0);
  background-color: var(--bg-color);
  color: var(--text-muted);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-filter:hover {
  background-color: #f1f5f9;
  color: var(--primary-color);
}

.btn-filter.active {
  background-color: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.curso-badge {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

/* Form Styles */
.nino-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-color);
}

.label-hint {
  font-weight: 400;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.form-section-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color, #e0e0e0);
  margin-top: 0.25rem;
}

.nino-form .form-section-title:first-child {
  border-top: none;
  padding-top: 0;
  margin-top: 0;
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.75rem;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  color: var(--text-main);
  background: var(--bg-color);
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}

.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.data-table th {
  font-weight: 600;
  color: var(--text-muted);
  background-color: var(--bg-color);
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 0.5px;
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.clickable-row:hover {
  background-color: #f1f5f9;
}

.btn-primary, .btn-export {
  padding: 0.75rem 1.5rem;
  border-radius: var(--radius-md);
  border: none;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
  width: auto;
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-export {
  background-color: var(--secondary-color);
  color: white;
  width: auto;
  box-shadow: var(--shadow-sm);
}

.btn-export:hover {
  background-color: var(--secondary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.empty-state {
  text-align: center;
  padding: 3rem 2rem;
  color: var(--text-muted);
  font-style: italic;
}
</style>
