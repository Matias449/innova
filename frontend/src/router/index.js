import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AsistenciaView from '../views/AsistenciaView.vue'
import AdminView from '../views/AdminView.vue'
import NinosView from '../views/NinosView.vue'
import NinoDetailView from '../views/NinoDetailView.vue'
import AulaView from '../views/AulaView.vue'
import FinanzasView from '../views/FinanzasView.vue'
import PersonalView from '../views/PersonalView.vue'
import ReportesView from '../views/ReportesView.vue'
import AlertasView from '../views/AlertasView.vue'
import ConfiguracionView from '../views/ConfiguracionView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/aula', name: 'aula', component: AulaView },
    { path: '/finanzas', name: 'finanzas', component: FinanzasView },
    { path: '/asistencia', name: 'asistencia', component: AsistenciaView },
    { path: '/administracion', name: 'admin', component: AdminView },
    { path: '/ninos', name: 'ninos', component: NinosView },
    { path: '/ninos/:id', name: 'nino-detail', component: NinoDetailView },
    { path: '/personal', name: 'personal', component: PersonalView },
    { path: '/reportes', name: 'reportes', component: ReportesView },
    { path: '/alertas', name: 'alertas', component: AlertasView },
    { path: '/configuracion', name: 'configuracion', component: ConfiguracionView }
  ]
})

export default router