<template>
  <div class="home-view">
    <section class="welcome-section">
      <h2>Bienvenida, {{ currentUser.name.split(' ')[0] }}</h2>
      <p>Selecciona un módulo para comenzar.</p>
    </section>

    <section class="modules-grid">
      <router-link v-if="hasAccessTo.aula" to="/aula" class="module-card primary">
        <div class="card-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
        </div>
        <h3>Gestión de Aula</h3>
        <p>Asistencia, bitácoras diarias, planificaciones y seguimiento de los niños.</p>
        <span class="btn-text">Ingresar al Aula &rarr;</span>
      </router-link>

      <router-link v-if="hasAccessTo.documentos" to="/administracion" class="module-card secondary">
        <div class="card-icon">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
        </div>
        <h3>Gestión Documental</h3>
        <p>Documentos MINEDUC, gestión de pagos y certificados oficiales.</p>
        <span class="btn-text">Ingresar a Gestión Documental &rarr;</span>
      </router-link>

      <router-link v-if="hasAccessTo.finanzas" to="/finanzas" class="module-card" style="background: linear-gradient(135deg, #047857, #065F46); color: white;">
        <div class="card-icon" style="background: rgba(255,255,255,0.15); color: white;">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <h3>Finanzas</h3>
        <p>Control de ingresos, egresos, matrículas y rentabilidad.</p>
        <span class="btn-text" style="color: #d1fae5;">Ver Balance &rarr;</span>
      </router-link>
      
      <router-link v-if="hasAccessTo.asistencia_dashboard" to="/asistencia" class="module-card" style="background: linear-gradient(135deg, #1e293b, #334155); color: white;">
        <div class="card-icon" style="background: rgba(255,255,255,0.1); color: white;">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path></svg>
        </div>
        <h3>Dashboard Global</h3>
        <p>Analíticas predictivas de ausentismo.</p>
        <span class="btn-text" style="color: #cbd5e1;">Ver Analíticas &rarr;</span>
      </router-link>
    </section>
  </div>
</template>

<script setup>
import { useAuth } from '../composables/useAuth'

const { currentUser, hasAccessTo } = useAuth()
</script>