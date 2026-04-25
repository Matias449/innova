<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
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
        <router-link to="/asistencia" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Asistencia</router-link>
        <router-link to="/ninos" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Niños</router-link>
        <router-link to="/personal" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Personal</router-link>
        <router-link to="/reportes" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Reportes</router-link>
        <router-link to="/alertas" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Alertas</router-link>
        <router-link to="/administracion" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Documentos</router-link>
        <router-link to="/configuracion" class="sidebar-item" active-class="active-link" @click="isSidebarOpen = false">Config.</router-link>
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
          <span>[👤]</span>
        </div>
      </header>

      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>
