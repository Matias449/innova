import { ref, computed } from 'vue'

const USERS = [
  { id: 'superadmin', name: 'Dev / Superadmin', role: 'SUPERADMIN' },
  { id: 'directora', name: 'Ana (Directora)', role: 'DIRECTORA' },
  { id: 'admin', name: 'Carlos (Administrador)', role: 'ADMINISTRADOR' },
  { id: 'educadora', name: 'Laura (Educadora)', role: 'EDUCADORA' }
]

// Estado global (simulación simple)
const currentUser = ref(USERS[0]) // Por defecto superadmin

const changeUser = (userId) => {
  const user = USERS.find(u => u.id === userId)
  if (user) currentUser.value = user
}

// Permisos computados
const hasAccessTo = computed(() => {
  const role = currentUser.value.role
  
  return {
    ninos: ['SUPERADMIN', 'DIRECTORA', 'EDUCADORA'].includes(role),
    ninos_create: ['SUPERADMIN', 'DIRECTORA'].includes(role),
    aula: ['SUPERADMIN', 'EDUCADORA'].includes(role),
    asistencia_dashboard: ['SUPERADMIN', 'DIRECTORA'].includes(role),
    reportes: ['SUPERADMIN', 'DIRECTORA', 'ADMINISTRADOR'].includes(role),
    documentos: ['SUPERADMIN', 'DIRECTORA', 'ADMINISTRADOR'].includes(role),
    finanzas: ['SUPERADMIN', 'DIRECTORA'].includes(role),
    configuracion: ['SUPERADMIN'].includes(role)
  }
})

export function useAuth() {
  return {
    USERS,
    currentUser,
    hasAccessTo,
    changeUser
  }
}
