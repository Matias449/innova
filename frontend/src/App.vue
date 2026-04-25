<script setup>
import { ref } from 'vue'

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
        <router-link to="/" class="sidebar-item" exact-active-class="active-link">Inicio</router-link>
        <router-link to="/asistencia" class="sidebar-item" active-class="active-link">Asistencia</router-link>
        <router-link to="/ninos" class="sidebar-item" active-class="active-link">Niños</router-link>
        <router-link to="/personal" class="sidebar-item" active-class="active-link">Personal</router-link>
        <router-link to="/reportes" class="sidebar-item" active-class="active-link">Reportes</router-link>
        <router-link to="/alertas" class="sidebar-item" active-class="active-link">Alertas</router-link>
        <router-link to="/administracion" class="sidebar-item" active-class="active-link">Documentos</router-link>
        <router-link to="/configuracion" class="sidebar-item" active-class="active-link">Config.</router-link>
      </nav>
    </aside>

    <div class="main-wrapper">
      <header class="global-navbar">
        <div class="navbar-left">
          <button class="menu-btn" @click="toggleSidebar" aria-label="Alternar Menú" style="gap: 8px; font-weight: 600;">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="24" height="24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            MENÚ
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
