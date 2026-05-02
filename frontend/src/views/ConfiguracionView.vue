<template>
  <div class="subpage">
    <main class="dashboard-container">
      <section class="section-header">
        <h2>Configuración</h2>
        <p>Ajusta las preferencias del sistema y los datos institucionales.</p>
      </section>

      <!-- Perfil Institucional -->
      <div class="card profile-card">
        <div class="card-header">
          <h3>Perfil Institucional</h3>
          <button class="btn-edit" @click="toggleEditPerfil">
            <svg v-if="!editingPerfil" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
            </svg>
            <svg v-else width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            {{ editingPerfil ? 'Cancelar' : 'Editar' }}
          </button>
        </div>

        <div v-if="!editingPerfil" class="perfil-display">
          <div class="perfil-row">
            <span class="perfil-label">Nombre</span>
            <span class="perfil-value">{{ perfil.nombre }}</span>
          </div>
          <div class="perfil-row">
            <span class="perfil-label">Dirección</span>
            <span class="perfil-value">{{ perfil.direccion }}</span>
          </div>
          <div class="perfil-row">
            <span class="perfil-label">Comuna</span>
            <span class="perfil-value">{{ perfil.comuna }}</span>
          </div>
          <div class="perfil-row">
            <span class="perfil-label">Región</span>
            <span class="perfil-value">{{ perfil.region }}</span>
          </div>
          <div class="perfil-row">
            <span class="perfil-label">Coordenadas</span>
            <span class="perfil-value">{{ perfil.lat }}, {{ perfil.lng }}</span>
          </div>
          <div class="perfil-row" v-if="perfil.telefono">
            <span class="perfil-label">Teléfono</span>
            <span class="perfil-value">{{ perfil.telefono }}</span>
          </div>
          <div class="perfil-row" v-if="perfil.email">
            <span class="perfil-label">Email</span>
            <span class="perfil-value">{{ perfil.email }}</span>
          </div>
        </div>

        <form v-else @submit.prevent="savePerfil" class="perfil-form">
          <div class="form-group">
            <label>Nombre del establecimiento</label>
            <input type="text" v-model="perfilEdit.nombre" required />
          </div>
          <div class="form-group">
            <label>Dirección</label>
            <input type="text" v-model="perfilEdit.direccion" required />
          </div>
          <div class="form-group">
            <label>Comuna</label>
            <input type="text" v-model="perfilEdit.comuna" required />
          </div>
          <div class="form-group">
            <label>Región</label>
            <input type="text" v-model="perfilEdit.region" required />
          </div>
          <div class="form-group">
            <label>Latitud</label>
            <input type="number" step="any" v-model="perfilEdit.lat" />
          </div>
          <div class="form-group">
            <label>Longitud</label>
            <input type="number" step="any" v-model="perfilEdit.lng" />
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input type="text" v-model="perfilEdit.telefono" />
          </div>
          <div class="form-group">
            <label>Email institucional</label>
            <input type="email" v-model="perfilEdit.email" />
          </div>
          <div class="form-actions full-span">
            <button type="submit" class="btn-primary">Guardar cambios</button>
          </div>
        </form>
      </div>

      <!-- Personal Institucional -->
      <div class="card staff-card">
        <div class="card-header">
          <h3>Personal del Establecimiento</h3>
          <button class="btn-primary btn-sm" @click="showStaffForm = !showStaffForm">
            <svg v-if="!showStaffForm" width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <svg v-else width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
            {{ showStaffForm ? 'Cancelar' : 'Agregar miembro' }}
          </button>
        </div>

        <transition name="fade-slide">
          <form v-if="showStaffForm" @submit.prevent="addStaff" class="staff-form">
            <div class="form-group">
              <label>Nombre completo</label>
              <input type="text" v-model="staffForm.nombre" required />
            </div>
            <div class="form-group">
              <label>Cargo</label>
              <input type="text" v-model="staffForm.cargo" required />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="staffForm.email" />
            </div>
            <div class="form-group">
              <label>Teléfono</label>
              <input type="text" v-model="staffForm.telefono" />
            </div>
            <div class="form-group">
              <label>Fecha de ingreso</label>
              <input type="date" v-model="staffForm.fecha_ingreso" />
            </div>
            <div class="form-actions full-span">
              <button type="submit" class="btn-primary">Agregar</button>
            </div>
          </form>
        </transition>

        <div class="table-responsive" v-if="personal.length > 0">
          <table class="data-table">
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Cargo</th>
                <th>Email</th>
                <th>Teléfono</th>
                <th>Ingreso</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="miembro in personal" :key="miembro.id">
                <td>{{ miembro.nombre }}</td>
                <td><span class="cargo-badge">{{ miembro.cargo }}</span></td>
                <td>{{ miembro.email || '—' }}</td>
                <td>{{ miembro.telefono || '—' }}</td>
                <td>{{ miembro.fecha_ingreso || '—' }}</td>
                <td>
                  <button class="btn-delete" @click="deleteStaff(miembro.id)" title="Eliminar">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-else class="empty-state">No hay personal registrado. Agregue el primer miembro del equipo.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api'

const perfil = ref({
  nombre: '', direccion: '', comuna: '', region: '',
  lat: null, lng: null, telefono: '', email: ''
})
const perfilEdit = ref({})
const editingPerfil = ref(false)

const personal = ref([])
const showStaffForm = ref(false)
const staffForm = ref({ nombre: '', cargo: '', email: '', telefono: '', fecha_ingreso: '' })

const fetchPerfil = async () => {
  const res = await fetch(`${API_BASE_URL}/configuracion/perfil/`)
  if (res.ok) perfil.value = await res.json()
}

const savePerfil = async () => {
  const res = await fetch(`${API_BASE_URL}/configuracion/perfil/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(perfilEdit.value)
  })
  if (res.ok) {
    perfil.value = await res.json()
    editingPerfil.value = false
  }
}

const startEditPerfil = () => {
  perfilEdit.value = { ...perfil.value }
}

const toggleEditPerfil = () => {
  if (!editingPerfil.value) startEditPerfil()
  editingPerfil.value = !editingPerfil.value
}

const fetchPersonal = async () => {
  const res = await fetch(`${API_BASE_URL}/configuracion/personal/`)
  if (res.ok) personal.value = await res.json()
}

const addStaff = async () => {
  const res = await fetch(`${API_BASE_URL}/configuracion/personal/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(staffForm.value)
  })
  if (res.ok) {
    const nuevo = await res.json()
    personal.value.push(nuevo)
    staffForm.value = { nombre: '', cargo: '', email: '', telefono: '', fecha_ingreso: '' }
    showStaffForm.value = false
  }
}

const deleteStaff = async (id) => {
  if (!confirm('¿Eliminar este miembro del personal?')) return
  const res = await fetch(`${API_BASE_URL}/configuracion/personal/${id}/`, { method: 'DELETE' })
  if (res.ok) personal.value = personal.value.filter(m => m.id !== id)
}

onMounted(() => {
  fetchPerfil()
  fetchPersonal()
})
</script>

<style scoped>
.section-header {
  margin-bottom: 2rem;
}

.card {
  margin-bottom: 2rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.card-header h3 {
  margin: 0;
}

/* Perfil display */
.perfil-display {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}

.perfil-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.perfil-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.perfil-value {
  font-size: 0.97rem;
  color: var(--text-main);
  font-weight: 500;
}

/* Perfil form */
.perfil-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.25rem;
}

/* Staff form */
.staff-form {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color, #e0e0e0);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
}

.form-group input {
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  color: var(--text-main);
  background: var(--bg-color);
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.full-span {
  grid-column: 1 / -1;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.25rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
}

.btn-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.9rem;
  background: transparent;
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: var(--radius-md);
  font-family: inherit;
  font-weight: 600;
  font-size: 0.85rem;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.btn-delete {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-delete:hover {
  background: #fee2e2;
  border-color: #fca5a5;
  color: #dc2626;
}

/* Table */
.table-responsive {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.85rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color, #f0f0f0);
}

.data-table th {
  font-weight: 600;
  color: var(--text-muted);
  background-color: var(--bg-color);
  text-transform: uppercase;
  font-size: 0.8rem;
  letter-spacing: 0.5px;
}

.cargo-badge {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 2.5rem;
  color: var(--text-muted);
  font-style: italic;
}

/* Transition */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
