<template>
  <div class="subpage">
    <header class="navbar">
        <div class="logo">
            <router-link to="/" style="text-decoration: none; color: inherit;"><h1>EduSync</h1></router-link>
        </div>
        <nav class="breadcrumb">
            <router-link to="/">Inicio</router-link> / <span>Gestión de Aula</span>
        </nav>
    </header>

    <main class="dashboard-container">
        <section class="section-header">
            <h2>Pase de Asistencia - Kínder B</h2>
            <p>Fecha: <span>12 de Abril, 2026</span></p>
        </section>

        <div class="attendance-grid">
            <div class="student-list card">
                <h3>Lista de Párvulos</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Alumno</th>
                            <th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>Benjamín Arancibia</td><td><button class="status-pill present">Presente</button></td></tr>
                        <tr><td>Sofía Henríquez</td><td><button class="status-pill present">Presente</button></td></tr>
                        <tr><td>Martina Osses</td><td><button class="status-pill absent">Ausente</button></td></tr>
                        <tr><td>Lucas Villavicencio</td><td><button class="status-pill present">Presente</button></td></tr>
                    </tbody>
                </table>
                <button class="save-btn primary">Finalizar Registro</button>
            </div>

            <div class="log-section card">
                <h3>Bitácora Diaria</h3>
                <textarea placeholder="Observaciones pedagógicas del día..."></textarea>
                <button class="save-btn secondary">Guardar Bitácora</button>
            </div>
        </div>
    </main>
  </div>
</template>