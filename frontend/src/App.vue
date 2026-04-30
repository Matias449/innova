<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from './composables/useAuth'

const route = useRoute()
const router = useRouter()
const { currentUser, USERS, hasAccessTo, changeUser } = useAuth()

const isSidebarOpen = ref(true)
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}
</script>

<template>
  <div class="app-layout">
    <aside class="global-sidebar" :class="{ 'sidebar-closed': !isSidebarOpen }">
      <div class="sidebar-header">
        <h1 class="logo-text">LOGO</h1>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/" class="sidebar-item" exact-active-class="active-link" @click="isSidebarOpen = false">Inicio</router-link>
        <router-link v-if="hasAccessTo.aula" to="/aula" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Aula Diaria</router-link>
        <router-link v-if="hasAccessTo.asistencia_dashboard" to="/asistencia" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Global Asistencia</router-link>
        <router-link v-if="hasAccessTo.ninos" to="/ninos" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Niños</router-link>
        <router-link v-if="hasAccessTo.reportes" to="/reportes" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Reportes</router-link>
        <router-link v-if="hasAccessTo.documentos" to="/administracion" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Documentos</router-link>
        <router-link v-if="hasAccessTo.finanzas" to="/finanzas" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Finanzas</router-link>
        <router-link v-if="hasAccessTo.configuracion" to="/configuracion" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Configuración</router-link>
      </nav>
    </aside>

    <div class="main-wrapper">
      <header class="global-navbar">
        <div class="navbar-left">
          <button class="menu-btn" @click="toggleSidebar" aria-label="Alternar Menú" style="gap: 8px; font-weight: 600;">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            MENÚ
          </button>
          
          <button v-if="route.path !== '/'" class="menu-btn" @click="router.push('/')" aria-label="Volver al Inicio" style="gap: 8px; font-weight: 600;">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
            INICIO
          </button>
          <span class="system-title">SISTEMA INTEGRADO EDUCATIVO</span>
        </div>
        <div class="user-profile">
          <span style="font-size: 14px; color: var(--text-muted); margin-right: 8px;">Viendo como:</span>
          <select 
            :value="currentUser.id" 
            @change="e => { changeUser(e.target.value); router.push('/'); isSidebarOpen = false }"
            style="padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-color); font-weight: 600; color: var(--primary-color);"
          >
            <option v-for="user in USERS" :key="user.id" :value="user.id">
              {{ user.name }}
            </option>
          </select>
        </div>
      </header>

      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>
