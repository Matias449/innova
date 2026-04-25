<template>
  <div class="subpage">


    <main class="dashboard-container">
        <section class="section-header">
            <h2>Panel Administrativo e Institucional</h2>
            <p>Gestión de cumplimiento normativo y finanzas.</p>
        </section>

        <div class="admin-grid">
            <div class="docs-section card">
                <h3>Repositorio MINEDUC / JUNJI</h3>
                <ul class="doc-list">
                    <li><span>Certificados de Matrícula 2026</span> <button class="btn-icon">👁️</button></li>
                    <li><span>Protocolos de Convivencia Escolar</span> <button class="btn-icon">👁️</button></li>
                </ul>
                <button class="upload-btn">+ Subir Nuevo Documento</button>
            </div>

            <div class="finance-section card">
                <h3>Estado de Pagos</h3>
                <div class="stat-card"><span class="label">Mensualidades al día</span><span class="value">85%</span></div>
                <button class="view-details">Ver Detalle por Apoderado</button>
            </div>
        </div>
    </main>
  </div>
</template>