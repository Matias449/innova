<template>
  <div class="subpage">
    <main class="dashboard-container">

      <section class="section-header">
        <h2>Gestión Documental</h2>
        <p>Cumplimiento normativo y rendición de cuentas JUNJI.</p>
      </section>

      <div class="admin-grid-full">

        <!-- Repositorio MINEDUC / JUNJI -->
        <div class="card">
          <div class="card-head">
            <h3>Repositorio MINEDUC / JUNJI</h3>
            <label class="btn-add" title="Subir documento">
              <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
              Subir
              <input type="file" hidden @change="subirRepositorio" />
            </label>
          </div>
          <ul class="doc-list">
            <li v-for="(doc, i) in repositorioDocs" :key="i">
              <div class="doc-info">
                <span class="doc-ext">{{ extIcon(doc.nombre) }}</span>
                <span class="doc-name">{{ doc.nombre }}</span>
              </div>
              <div class="doc-meta">
                <span class="text-muted">{{ doc.fecha }}</span>
                <button class="btn-icon" title="Eliminar" @click="eliminarRepo(i)">
                  <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </li>
            <li v-if="repositorioDocs.length === 0" class="doc-empty">
              No hay documentos cargados.
            </li>
          </ul>
        </div>

        <!-- Rendición D.Nº67 JUNJI — Formulario -->
        <div class="card">
          <div class="card-head">
            <h3>Rendición D.Nº67 JUNJI</h3>
            <span class="mes-badge">{{ mesActualLabel }}</span>
          </div>

          <form class="rendicion-form" @submit.prevent="registrarRendicion">
            <input v-model="nuevo.nombre" type="text" placeholder="Nombre del documento" required />

            <select v-model="nuevo.tipo" required>
              <option value="" disabled>Tipo de documento...</option>
              <optgroup label="Remuneraciones">
                <option value="liquidacion_sueldo">Liquidación de Sueldo</option>
                <option value="libro_remuneraciones">Libro de Remuneraciones</option>
                <option value="contrato_trabajo">Contrato de Trabajo</option>
                <option value="planilla_personal">Planilla de Asistencia de Personal</option>
              </optgroup>
              <optgroup label="Cotizaciones">
                <option value="cotizacion_afp">Cotización AFP</option>
                <option value="cotizacion_salud">Cotización de Salud (FONASA / Isapre)</option>
                <option value="seguro_accidentes">Seguro de Accidentes del Trabajo</option>
              </optgroup>
              <optgroup label="Gastos Operacionales">
                <option value="factura_proveedor">Factura de Proveedor</option>
                <option value="boleta_honorarios">Boleta de Honorarios</option>
                <option value="servicio_basico">Servicios Básicos</option>
                <option value="material_didactico">Material Didáctico</option>
                <option value="gasto_alimentacion">Gastos de Alimentación</option>
                <option value="mantencion">Mantención y Reparaciones</option>
                <option value="arriendo">Arriendo</option>
              </optgroup>
              <optgroup label="Documentos de Cierre">
                <option value="rendicion_consolidada">Planilla Consolidada</option>
                <option value="declaracion_jurada">Declaración Jurada</option>
                <option value="comprobante_transferencia">Comprobante de Transferencia</option>
                <option value="nomina_beneficiarios">Nómina de Beneficiarios</option>
              </optgroup>
            </select>

            <label class="file-drop" :class="{ 'has-file': nuevo.archivoNombre }">
              <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"/></svg>
              <span>{{ nuevo.archivoNombre || 'Adjuntar archivo' }}</span>
              <input ref="fileInput" type="file" hidden accept=".pdf,.jpg,.jpeg,.png,.xlsx,.xls" @change="onFile" />
            </label>

            <button type="submit" class="btn-submit" :disabled="!formValido">
              Registrar documento
            </button>
          </form>
        </div>

        <!-- Rendiciones por mes -->
        <template v-if="rendicionesPorMes.length > 0">
          <div v-for="rendicion in rendicionesPorMes" :key="rendicion.mes" class="card rendicion-mes-card">

            <div class="rendicion-mes-head">
              <div class="rendicion-mes-title">
                <h3>Rendición de {{ rendicion.label }}</h3>
                <span :class="['estado-pill', rendicion.estado === 'rendido' ? 'estado-rendido' : 'estado-proceso']">
                  {{ rendicion.estado === 'rendido' ? 'Rendido' : 'En proceso de rendición' }}
                </span>
              </div>
              <div class="rendicion-mes-actions">
                <button
                  v-if="puedeGestionarEstado"
                  class="btn-estado"
                  @click="toggleEstado(rendicion.mes)"
                >
                  {{ rendicion.estado === 'rendido' ? 'Marcar en proceso' : 'Marcar como rendido' }}
                </button>
                <button class="btn-exportar" @click="exportarJunji(rendicion)">
                  <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                  Importar a formato JUNJI
                </button>
              </div>
            </div>

            <table class="data-table">
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Tipo</th>
                  <th>Archivo</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(doc, i) in rendicion.docs" :key="i">
                  <td>{{ doc.nombre }}</td>
                  <td><span class="tipo-pill">{{ tiposMap[doc.tipo] ?? doc.tipo }}</span></td>
                  <td class="text-muted" style="font-size:0.8rem">{{ doc.archivoNombre }}</td>
                  <td class="text-muted">{{ doc.fecha }}</td>
                </tr>
                <tr v-if="rendicion.docs.length === 0">
                  <td colspan="4" style="text-align:center; color: var(--text-muted); padding: 1rem 0; font-size:0.85rem">
                    Sin documentos registrados.
                  </td>
                </tr>
              </tbody>
            </table>

          </div>
        </template>

      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'
import { useAuth } from '../composables/useAuth'

const { currentUser } = useAuth()
const fileInput = ref(null)

// ── Auth ─────────────────────────────────────────────────────────────────────
const puedeGestionarEstado = computed(() =>
  ['ADMINISTRADOR', 'SUPERADMIN'].includes(currentUser.value.role)
)

// ── Helpers ───────────────────────────────────────────────────────────────────
const MESES = [
  'enero','febrero','marzo','abril','mayo','junio',
  'julio','agosto','septiembre','octubre','noviembre','diciembre',
]

function mesKey(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
}

function mesLabel(key) {
  const [year, month] = key.split('-')
  return `${MESES[parseInt(month) - 1]} ${year}`
}

const mesActualKey   = mesKey()
const mesActualLabel = mesLabel(mesActualKey)

function extIcon(nombre) {
  const ext = nombre.split('.').pop().toLowerCase()
  return { pdf: 'PDF', jpg: 'IMG', jpeg: 'IMG', png: 'IMG', xlsx: 'XLS', xls: 'XLS' }[ext] ?? 'DOC'
}

// ── Estado persistido ─────────────────────────────────────────────────────────
const rendicionDocs   = ref(JSON.parse(localStorage.getItem('rendicion_docs')    || '[]'))
const repositorioDocs = ref(JSON.parse(localStorage.getItem('repositorio_docs')  || '[]'))
const rendicionEstados = ref(JSON.parse(localStorage.getItem('rendicion_estados') || '{}'))

function persist() {
  localStorage.setItem('rendicion_docs',    JSON.stringify(rendicionDocs.value))
  localStorage.setItem('rendicion_estados', JSON.stringify(rendicionEstados.value))
}

// ── Agrupación por mes ────────────────────────────────────────────────────────
const rendicionesPorMes = computed(() => {
  const mapa = {}

  // Asegurar que el mes actual siempre aparece
  if (!mapa[mesActualKey]) mapa[mesActualKey] = []

  for (const doc of rendicionDocs.value) {
    const key = doc.mes ?? mesActualKey
    if (!mapa[key]) mapa[key] = []
    mapa[key].push(doc)
  }

  return Object.keys(mapa)
    .sort((a, b) => b.localeCompare(a))
    .map(key => ({
      mes:    key,
      label:  mesLabel(key),
      docs:   mapa[key],
      estado: rendicionEstados.value[key] ?? 'en_proceso',
    }))
})

// ── Formulario de rendición ───────────────────────────────────────────────────
const nuevo = ref({ nombre: '', tipo: '', archivoNombre: '', archivo: null })

const tiposMap = {
  liquidacion_sueldo:       'Liquidación de Sueldo',
  libro_remuneraciones:     'Libro de Remuneraciones',
  contrato_trabajo:         'Contrato de Trabajo',
  planilla_personal:        'Planilla de Asistencia de Personal',
  cotizacion_afp:           'Cotización AFP',
  cotizacion_salud:         'Cotización de Salud',
  seguro_accidentes:        'Seguro de Accidentes del Trabajo',
  factura_proveedor:        'Factura de Proveedor',
  boleta_honorarios:        'Boleta de Honorarios',
  servicio_basico:          'Servicios Básicos',
  material_didactico:       'Material Didáctico',
  gasto_alimentacion:       'Gastos de Alimentación',
  mantencion:               'Mantención y Reparaciones',
  arriendo:                 'Arriendo',
  rendicion_consolidada:    'Planilla Consolidada',
  declaracion_jurada:       'Declaración Jurada',
  comprobante_transferencia:'Comprobante de Transferencia',
  nomina_beneficiarios:     'Nómina de Beneficiarios',
}

const formValido = computed(
  () => nuevo.value.nombre.trim() && nuevo.value.tipo && nuevo.value.archivoNombre
)

function onFile(e) {
  const file = e.target.files[0]
  if (file) { nuevo.value.archivo = file; nuevo.value.archivoNombre = file.name }
}

function registrarRendicion() {
  if (!formValido.value) return
  rendicionDocs.value.unshift({
    nombre:        nuevo.value.nombre.trim(),
    tipo:          nuevo.value.tipo,
    archivoNombre: nuevo.value.archivoNombre,
    fecha:         new Date().toLocaleDateString('es-CL'),
    mes:           mesActualKey,
  })
  persist()
  nuevo.value = { nombre: '', tipo: '', archivoNombre: '', archivo: null }
  if (fileInput.value) fileInput.value.value = ''
}

// ── Estado de rendición ───────────────────────────────────────────────────────
function toggleEstado(mes) {
  const actual = rendicionEstados.value[mes] ?? 'en_proceso'
  rendicionEstados.value = {
    ...rendicionEstados.value,
    [mes]: actual === 'rendido' ? 'en_proceso' : 'rendido',
  }
  persist()
}

// ── Repositorio ───────────────────────────────────────────────────────────────
function subirRepositorio(e) {
  const file = e.target.files[0]
  if (!file) return
  repositorioDocs.value.unshift({
    nombre: file.name,
    fecha:  new Date().toLocaleDateString('es-CL'),
  })
  localStorage.setItem('repositorio_docs', JSON.stringify(repositorioDocs.value))
  e.target.value = ''
}

function eliminarRepo(i) {
  repositorioDocs.value.splice(i, 1)
  localStorage.setItem('repositorio_docs', JSON.stringify(repositorioDocs.value))
}

// ── Exportar a JUNJI (Excel vacío con headers) ────────────────────────────────
function exportarJunji(rendicion) {
  const wb = XLSX.utils.book_new()
  const headers = [
    ['N°', 'Tipo de Documento', 'Nombre', 'Archivo Adjunto', 'Fecha de Registro', 'Observaciones'],
  ]
  const ws = XLSX.utils.aoa_to_sheet(headers)

  // Anchos de columna
  ws['!cols'] = [
    { wch: 5 }, { wch: 32 }, { wch: 36 }, { wch: 30 }, { wch: 18 }, { wch: 24 },
  ]

  XLSX.utils.book_append_sheet(wb, ws, `Rendición ${rendicion.label}`)
  XLSX.writeFile(wb, `Rendicion_JUNJI_${rendicion.mes}.xlsx`)
}
</script>
