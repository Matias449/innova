<template>
  <div>
    <header class="navbar">
        <div class="logo">
            <h1>EduSync</h1>
        </div>
        <div class="user-profile">
            <img src="https://ui-avatars.com/api/?name=Jardin+Los+Pinitos&background=0D8ABC&color=fff" alt="Avatar">
            <span>Jardín Los Pinitos</span>
        </div>
    </header>

    <main class="dashboard-container">
        <section class="welcome-section">
            <h2>Bienvenido al Sistema de Gestión</h2>
            <p>Selecciona el módulo al que deseas ingresar para comenzar tu jornada.</p>
        </section>

        <section class="modules-grid">
            <router-link to="/asistencia" class="module-card primary">
                <div class="card-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>
                </div>
                <h3>Gestión de Aula</h3>
                <p>Asistencia, bitácoras diarias, planificaciones y seguimiento de los niños.</p>
                <span class="btn-text">Ingresar al Aula &rarr;</span>
            </router-link>

            <router-link to="/administracion" class="module-card secondary">
                <div class="card-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                <h3>Administración Institucional</h3>
                <p>Documentos MINEDUC, gestión de pagos y certificados oficiales.</p>
                <span class="btn-text">Ingresar a Administración &rarr;</span>
            </router-link>
        </section>
    </main>
  </div>
</template>