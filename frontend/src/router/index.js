import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import AsistenciaView from '../views/AsistenciaView.vue'
import AdminView from '../views/AdminView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/asistencia', name: 'asistencia', component: AsistenciaView },
    { path: '/administracion', name: 'admin', component: AdminView }
  ]
})

export default router