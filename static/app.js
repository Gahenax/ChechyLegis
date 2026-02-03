const API_BASE = '/api';
let currentRole = 'admin';

// DOM Elements
const content = document.getElementById('content');
const roleSelector = document.getElementById('role-selector');
const navList = document.getElementById('nav-list');
const navCreate = document.getElementById('nav-create');
const navSettings = document.getElementById('nav-settings');

// State Management
// Load filters from storage or default
let filters = JSON.parse(localStorage.getItem('chechy_filters')) || {
    fecha_desde: '',
    fecha_hasta: '',
    estado: '',
    numero_proceso: ''
};

// Initialization
roleSelector.addEventListener('change', (e) => {
    currentRole = e.target.value;
    document.getElementById('current-user-display').innerText = `Usuario: ${currentRole.charAt(0).toUpperCase() + currentRole.slice(1)}`;
    loadList(); // Refresh list to respect roles (especially delete button visibility)
});

navList.addEventListener('click', () => {
    setActiveNav(navList);
    loadList();
});

navCreate.addEventListener('click', () => {
    setActiveNav(navCreate);
    renderCreateForm();
});

navSettings.addEventListener('click', () => {
    setActiveNav(navSettings);
    renderSettings();
});

function setActiveNav(el) {
    document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
    el.classList.add('active');
}

// --- ANTIGRAVITY_HELPER: safe stringify for UI rendering ---
function safeStringify(x) {
    try {
        if (x === null || x === undefined) return '';
        if (typeof x === 'string') return x;
        // Pretty-print objects/arrays for readability; replace later with proper renderer/table.
        return JSON.stringify(x, null, 2);
    } catch (e) {
        return String(x);
    }
}
// --- END ANTIGRAVITY_HELPER ---

// API Helpers
async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-User-Role': currentRole,
        'X-User-Name': `Usuario_${currentRole}`
    };

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Error en la petición');
    }
    return response.json();
}

// Views
async function loadList() {
    const query = new URLSearchParams(filters).toString();
    try {
        const procesos = await apiCall(`/procesos?${query}`);
        renderListPage(procesos);
    } catch (err) {
        content.innerHTML = `<div class="card error">${err.message}</div>`;
    }
}

function renderListPage(procesos) {
    content.innerHTML = `
        <div class="view-header">
            <h2>Gestión de Procesos</h2>
            ${currentRole !== 'viewer' ? `<button class="btn btn-primary" onclick="renderCreateForm()">+ Nuevo Proceso</button>` : ''}
        </div>

        <div class="filters">
            <div>
                <label>Buscador</label>
                <input type="text" placeholder="Núm. Proceso..." value="${filters.numero_proceso}" oninput="updateFilter('numero_proceso', this.value)">
            </div>
            <div>
                <label>Estado</label>
                <select onchange="updateFilter('estado', this.value)">
                    <option value="">Todos</option>
                    <option value="ACTIVO" ${filters.estado === 'ACTIVO' ? 'selected' : ''}>Activo</option>
                    <option value="TERMINADO" ${filters.estado === 'TERMINADO' ? 'selected' : ''}>Terminado</option>
                    <option value="SUSPENDIDO" ${filters.estado === 'SUSPENDIDO' ? 'selected' : ''}>Suspendido</option>
                    <option value="RECHAZADO" ${filters.estado === 'RECHAZADO' ? 'selected' : ''}>Rechazado</option>
                </select>
            </div>
            <div>
                <label>Desde</label>
                <input type="date" value="${filters.fecha_desde}" onchange="updateFilter('fecha_desde', this.value)">
            </div>
            <div>
                <label>Hasta</label>
                <input type="date" value="${filters.fecha_hasta}" onchange="updateFilter('fecha_hasta', this.value)">
            </div>
        </div>

        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th>Radicación</th>
                        <th>Número de Proceso</th>
                        <th>Partes</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${procesos.map(p => `
                        <tr>
                            <td>${p.fecha_radicacion}</td>
                            <td><strong>${p.numero_proceso}</strong></td>
                            <td>${p.partes}</td>
                            <td><span class="badge badge-${p.estado.toLowerCase()}">${p.estado}</span></td>
                            <td>
                                <button class="btn-text" onclick="loadDetail(${p.id})">Ver</button>
                                ${currentRole !== 'viewer' ? `<button class="btn-text" onclick="renderEditForm(${p.id})">Editar</button>` : ''}
                                ${currentRole === 'admin' ? `<button class="btn-text" style="color:red" onclick="deleteProceso(${p.id})">Eliminar</button>` : ''}
                            </td>
                        </tr>
                    `).join('')}
                    ${procesos.length === 0 ? '<tr><td colspan="5" style="text-align:center">No se encontraron registros</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

function updateFilter(key, val) {
    filters[key] = val;
    localStorage.setItem('chechy_filters', JSON.stringify(filters));
    loadList();
}

async function loadDetail(id) {
    const p = await apiCall(`/procesos/${id}`);
    content.innerHTML = `
        <div class="view-header">
            <h2>Detalle de Proceso: ${p.numero_proceso}</h2>
            <button class="btn" onclick="loadList()">Volver</button>
        </div>
        <div class="card">
            <div class="form-grid">
                <div><label>Fecha Radicación</label><p>${p.fecha_radicacion}</p></div>
                <div><label>Estado</label><p><span class="badge badge-${p.estado.toLowerCase()}">${p.estado}</span></p></div>
                <div><label>Clase</label><p>${p.clase_proceso || 'N/A'}</p></div>
                <div><label>Cuantía</label><p>${p.cuantia_tipo || 'N/A'}</p></div>
                <div class="full-width"><label>Partes</label><p>${p.partes}</p></div>
                <div class="full-width"><label>Observaciones</label><p>${p.observaciones || 'Sin observaciones'}</p></div>
            </div>
        </div>

        <div class="audit-list">
            <h3>Historial de Auditoría</h3>
            ${p.audit_trail.map(log => `
                <div class="audit-item">
                    <strong>${log.accion}</strong> - ${new Date(log.timestamp).toLocaleString()}<br>
                    <small>Usuario: ${log.usuario}</small>
                    ${log.campo_modificado ? `<div>Cambio en <i>${log.campo_modificado}</i>: <s>${log.valor_anterior}</s> → <b>${log.valor_nuevo}</b></div>` : ''}
                    ${log.accion === 'CREATE' ? `<div style="font-size:0.75rem; color:var(--text-light)">Datos iniciales: ${log.valor_nuevo}</div>` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

function renderCreateForm() {
    renderForm('Nuevo Proceso', null);
}

async function renderEditForm(id) {
    const p = await apiCall(`/procesos/${id}`);
    renderForm('Editar Proceso', p);
}

function renderForm(title, data) {
    content.innerHTML = `
        <div class="view-header">
            <h2>${title}</h2>
            <button class="btn" onclick="loadList()">Cancelar</button>
        </div>
        <div class="card">
            <form id="proceso-form">
                <div class="form-grid">
                    <div>
                        <label>Número de Proceso *</label>
                        <input type="text" name="numero_proceso" value="${data ? data.numero_proceso : ''}" required>
                    </div>
                    <div>
                        <label>Fecha Radicación *</label>
                        <input type="date" name="fecha_radicacion" value="${data ? data.fecha_radicacion : ''}" required>
                    </div>
                    <div>
                        <label>Estado *</label>
                        <select name="estado" required>
                            <option value="ACTIVO" ${data?.estado === 'ACTIVO' ? 'selected' : ''}>Activo</option>
                            <option value="TERMINADO" ${data?.estado === 'TERMINADO' ? 'selected' : ''}>Terminado</option>
                            <option value="SUSPENDIDO" ${data?.estado === 'SUSPENDIDO' ? 'selected' : ''}>Suspendido</option>
                            <option value="RECHAZADO" ${data?.estado === 'RECHAZADO' ? 'selected' : ''}>Rechazado</option>
                        </select>
                    </div>
                    <div>
                        <label>Clase de Proceso</label>
                        <input type="text" name="clase_proceso" value="${data ? data.clase_proceso || '' : ''}">
                    </div>
                    <div>
                        <label>Tipo de Cuantía</label>
                        <select name="cuantia_tipo">
                            <option value="">Seleccione...</option>
                            <option value="MINIMA" ${data?.cuantia_tipo === 'MINIMA' ? 'selected' : ''}>Mínima</option>
                            <option value="MENOR" ${data?.cuantia_tipo === 'MENOR' ? 'selected' : ''}>Menor</option>
                            <option value="MAYOR" ${data?.cuantia_tipo === 'MAYOR' ? 'selected' : ''}>Mayor</option>
                        </select>
                    </div>
                    <div>
                        <label>Fecha Última Actuación</label>
                        <input type="date" name="fecha_ultima_actuacion" value="${data ? data.fecha_ultima_actuacion || '' : ''}">
                    </div>
                    <div class="full-width">
                        <label>Partes (Demandante vs Demandado) *</label>
                        <input type="text" name="partes" value="${data ? data.partes : ''}" required>
                    </div>
                    <div class="full-width">
                        <label>Observaciones</label>
                        <textarea name="observaciones" rows="4">${data ? data.observaciones || '' : ''}</textarea>
                    </div>
                    <div class="full-width">
                        <button type="submit" class="btn btn-primary">${data ? 'Guardar Cambios' : 'Registrar Proceso'}</button>
                    </div>
                </div>
            </form>
            <div id="form-error" class="hidden" style="color:var(--error); margin-top:1rem; font-weight:600;"></div>
        </div>
    `;

    document.getElementById('proceso-form').onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const jsonData = Object.fromEntries(formData.entries());

        // Cleanup empty optional fields
        if (!jsonData.cuantia_tipo) delete jsonData.cuantia_tipo;
        if (!jsonData.fecha_ultima_actuacion) delete jsonData.fecha_ultima_actuacion;

        try {
            if (data) {
                await apiCall(`/procesos/${data.id}`, 'PUT', jsonData);
            } else {
                await apiCall('/procesos', 'POST', jsonData);
            }
            loadList();
        } catch (err) {
            const errorEl = document.getElementById('form-error');
            errorEl.innerText = err.message;
            errorEl.classList.remove('hidden');
        }
    };
}

async function deleteProceso(id) {
    if (confirm('¿Está seguro de eliminar este proceso? (Se realizará un borrado lógico)')) {
        try {
            await apiCall(`/procesos/${id}`, 'DELETE');
            loadList();
        } catch (err) {
            alert(err.message);
        }
    }
}

// ============================================
// SETTINGS
// ============================================

function renderSettings() {
    // Get all content from localStorage for debugging/viewing
    const storageItems = [];
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        const val = localStorage.getItem(key);
        // Try to parse to see if it's an object
        let parsed = val;
        let isObj = false;
        try {
            parsed = JSON.parse(val);
            if (typeof parsed === 'object' && parsed !== null) isObj = true;
        } catch (e) { }

        storageItems.push({ key, val, parsed, isObj });
    }

    content.innerHTML = `
        <div class="view-header">
            <h2>Configuración del Sistema</h2>
        </div>
        
        <div class="card">
            <h3>Preferencias Locales</h3>
            <p style="color:var(--text-light); margin-bottom:1rem;">
                Estas configuraciones se guardan en tu navegador.
            </p>
            
            <table>
                <thead>
                    <tr>
                        <th>Clave</th>
                        <th>Valor (Vista Previa)</th>
                        <th>Tipo</th>
                        <th>Acción</th>
                    </tr>
                </thead>
                <tbody>
                    ${storageItems.map(item => `
                        <tr>
                            <td><strong>${item.key}</strong></td>
                            <td title="${safeStringify(item.val)}">
                                ${item.isObj
            ? `<pre style="margin:0; font-size:0.75rem;">${safeStringify(item.parsed).slice(0, 50)}${JSON.stringify(item.parsed).length > 50 ? '...' : ''}</pre>`
            : item.val}
                            </td>
                            <td><span class="badge badge-${item.isObj ? 'activo' : 'terminado'}">${item.isObj ? 'JSON' : 'Texto'}</span></td>
                            <td>
                                <button class="btn-text" style="color:red;" onclick="localStorage.removeItem('${item.key}'); renderSettings();">Borrar</button>
                            </td>
                        </tr>
                    `).join('')}
                    ${storageItems.length === 0 ? '<tr><td colspan="4" style="text-align:center">No hay configuraciones guardadas</td></tr>' : ''}
                </tbody>
            </table>
            
            <div style="margin-top:2rem;">
                 <button class="btn" onclick="localStorage.clear(); renderSettings();">⚠️ Limpiar Todo</button>
            </div>
        </div>
        
        <div class="card">
            <h3>Diagnóstico UI</h3>
            <p>Prueba de renderizado de objetos (Anti-Bug):</p>
            <div id="debug-render-area" style="background:#f5f5f5; padding:1rem; border-radius:4px;">
                <!-- This should NOT show [object Object] -->
                ${safeStringify({ test: "OK", nested: { array: [1, 2, 3] } })}
            </div>
        </div>
    `;
}

// ============================================
// AI FUNCTIONS
// ============================================

async function performAISearch() {
    const query = document.getElementById('ai-search-input').value.trim();
    if (!query) {
        alert('Por favor ingresa una consulta');
        return;
    }

    try {
        const result = await apiCall('/ai/search', 'POST', { query });
        renderAIResults(result);
    } catch (err) {
        if (err.message.includes('503')) {
            alert('⚠️ Servicio de IA no disponible. Por favor configura GEMINI_API_KEY en el archivo .env');
        } else {
            alert('Error: ' + err.message);
        }
    }
}

function renderAIResults(result) {
    const procesos = result.resultados;

    content.innerHTML = `
        <div class="view-header">
            <h2>Resultados de Búsqueda IA <span class="ai-badge">GEMINI</span></h2>
            <button class="btn" onclick="loadList()">Volver</button>
        </div>

        <div class="ai-results-container">
            <div class="ai-interpretation">
                <strong>🤖 Interpretación:</strong> ${result.interpretacion}
            </div>
            
            ${result.sugerencias.length > 0 ? `
                <div>
                    <strong>💡 Búsquedas sugeridas:</strong>
                    <div class="ai-suggestions">
                        ${result.sugerencias.map(s => `
                            <span class="suggestion-chip" onclick="document.getElementById('ai-search-input').value='${s}'; performAISearch();">${s}</span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        </div>

        <div class="card">
            <h3>Resultados (${result.total_resultados})</h3>
            <table>
                <thead>
                    <tr>
                        <th>Radicación</th>
                        <th>Número de Proceso</th>
                        <th>Partes</th>
                        <th>Estado</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    ${procesos.map(p => `
                        <tr>
                            <td>${p.fecha_radicacion}</td>
                            <td><strong>${p.numero_proceso}</strong></td>
                            <td>${p.partes}</td>
                            <td><span class="badge badge-${p.estado.toLowerCase()}">${p.estado}</span></td>
                            <td>
                                <button class="btn-text" onclick="loadDetail(${p.id})">Ver</button>
                                <button class="btn-text" onclick="analyzeWithAI(${p.id})">🤖 Analizar</button>
                            </td>
                        </tr>
                    `).join('')}
                    ${procesos.length === 0 ? '<tr><td colspan="5" style="text-align:center">No se encontraron resultados</td></tr>' : ''}
                </tbody>
            </table>
        </div>
    `;
}

async function analyzeWithAI(procesoId) {
    try {
        const result = await apiCall(`/ai/analyze/${procesoId}`);
        showAIAnalysis(result);
    } catch (err) {
        alert('Error al analizar: ' + err.message);
    }
}

function showAIAnalysis(result) {
    const p = result.proceso;
    const a = result.analisis;

    content.innerHTML = `
        <div class="view-header">
            <h2>Análisis IA: ${p.numero_proceso} <span class="ai-badge">GEMINI</span></h2>
            <button class="btn" onclick="loadList()">Volver</button>
        </div>

        <div class="card">
            <h3>📊 Resumen Ejecutivo</h3>
            <p>${a.resumen}</p>
        </div>

        ${a.alertas && a.alertas.length > 0 ? `
            <div class="card" style="border-left: 4px solid var(--warning);">
                <h3>⚠️ Alertas</h3>
                <ul>
                    ${a.alertas.map(alert => `<li>${alert}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        <div class="card">
            <h3>🏷️ Clasificación Sugerida</h3>
            <p>${a.clasificacion_sugerida}</p>
        </div>

        ${a.acciones_recomendadas && a.acciones_recomendadas.length > 0 ? `
            <div class="card" style="border-left: 4px solid var(--success);">
                <h3>✅ Acciones Recomendadas</h3>
                <ul>
                    ${a.acciones_recomendadas.map(accion => `<li>${accion}</li>`).join('')}
                </ul>
            </div>
        ` : ''}

        <div class="card">
            <h3>📄 Datos del Proceso</h3>
            <div class="form-grid">
                <div><label>Número</label><p>${p.numero_proceso}</p></div>
                <div><label>Estado</label><p><span class="badge badge-${p.estado.toLowerCase()}">${p.estado}</span></p></div>
                <div><label>Fecha Radicación</label><p>${p.fecha_radicacion}</p></div>
                <div><label>Clase</label><p>${p.clase_proceso || 'N/A'}</p></div>
                <div class="full-width"><label>Partes</label><p>${p.partes}</p></div>
            </div>
            <button class="btn btn-primary" onclick="findSimilarCases(${p.id})">🔍 Buscar Casos Similares</button>
        </div>
    `;
}

async function findSimilarCases(procesoId) {
    try {
        const result = await apiCall(`/ai/similar/${procesoId}`);
        showSimilarCases(result);
    } catch (err) {
        alert('Error al buscar casos similares: ' + err.message);
    }
}

function showSimilarCases(result) {
    const ref = result.proceso_referencia;
    const similar = result.casos_similares;

    content.innerHTML = `
        <div class="view-header">
            <h2>Casos Similares <span class="ai-badge">GEMINI</span></h2>
            <button class="btn" onclick="loadDetail(${ref.id})">Ver Proceso Original</button>
        </div>

        <div class="card">
            <h3>📌 Proceso de Referencia</h3>
            <p><strong>${ref.numero_proceso}</strong> - ${ref.partes}</p>
            <p>Clase: ${ref.clase_proceso || 'N/A'} | Estado: <span class="badge badge-${ref.estado.toLowerCase()}">${ref.estado}</span></p>
        </div>

        <div class="card">
            <h3>🔍 Casos Similares Encontrados (${result.total_encontrados})</h3>
            ${similar.length > 0 ? `
                <table>
                    <thead>
                        <tr>
                            <th>Número</th>
                            <th>Partes</th>
                            <th>Clase</th>
                            <th>Estado</th>
                            <th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${similar.map(p => `
                            <tr>
                                <td><strong>${p.numero_proceso}</strong></td>
                                <td>${p.partes}</td>
                                <td>${p.clase_proceso || 'N/A'}</td>
                                <td><span class="badge badge-${p.estado.toLowerCase()}">${p.estado}</span></td>
                                <td><button class="btn-text" onclick="loadDetail(${p.id})">Ver Detalle</button></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            ` : '<p>No se encontraron casos similares.</p>'}
        </div>
    `;
}

// Chat Widget
let chatHistory = [];

function toggleChat() {
    const widget = document.getElementById('ai-chat-widget');
    widget.classList.toggle('hidden');

    if (!widget.classList.contains('hidden') && chatHistory.length === 0) {
        addChatMessage('assistant', '¡Hola! Soy tu asistente legal virtual. ¿En qué puedo ayudarte hoy?');
    }
}

function addChatMessage(role, message) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.textContent = message;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    chatHistory.push({ role, message });
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    addChatMessage('user', message);
    input.value = '';

    try {
        const result = await apiCall('/ai/chat', 'POST', { message });
        addChatMessage('assistant', result.respuesta);
    } catch (err) {
        if (err.message.includes('503')) {
            addChatMessage('assistant', '⚠️ El servicio de IA no está disponible. Por favor configura GEMINI_API_KEY.');
        } else {
            addChatMessage('assistant', 'Lo siento, ocurrió un error: ' + err.message);
        }
    }
}

// Start
loadList();
