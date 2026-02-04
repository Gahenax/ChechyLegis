/**
 * GAHENAX CORE - UI Render Engine
 * Lex-Tech Edition: Tribunal Digital
 */

const Render = {
    appContent: null,

    init(elementId) {
        this.appContent = document.getElementById(elementId);
    },

    renderLayout(state) {
        // En esta arquitectura, el layout base está en index.html
        // Aquí manejamos el contenido dinámico del área 'content'
        switch (state.currentView) {
            case 'list': return this.showExpedientesList(state);
            case 'detail': return this.showExpedienteDetail(state);
            case 'form': return this.showExpedienteForm(state);
            case 'support': return this.showSupportDesk(state);
            case 'settings': return this.showSettingsArchive(state);
            case 'analysis': return this.showAnalysisReport(state);
        }
    },

    clearContent() {
        this.appContent.innerHTML = '<div class="loader">ACCEDIENDO AL ARCHIVO CENTRAL...</div>';
    },

    header(title, providencias = '') {
        return `
            <div class="view-header" style="border-bottom: 2px solid var(--lex-border); margin-bottom: 2.5rem; padding-bottom: 1rem;">
                <div>
                    <h2 style="font-size: 2.2rem; color: var(--lex-text-main); font-weight: 400;">${title.toUpperCase()}</h2>
                    <span style="font-size: 0.65rem; color: var(--lex-accent); font-weight: 700; letter-spacing: 2px;">SALA DE TRIBUNAL DIGITAL</span>
                </div>
                <div class="header-providencias" style="display:flex; gap:1rem;">${providencias}</div>
            </div>
        `;
    },

    async showExpedientesList(state) {
        this.clearContent();
        try {
            const procesos = await window.GahenaxAPI.getExpedientes(state.filters);

            let html = this.header('Archivo de Expedientes',
                state.currentRole !== 'viewer' ?
                    `<button class="lex-btn lex-btn-primary" onclick="App.navigate('form')"><i class="fas fa-file-signature"></i> NUEVA RADICACIÓN</button>` : ''
            );

            // Filtros Estilo Despacho
            html += `
                <div style="margin-bottom: 3rem; padding: 1.5rem; border: 1px solid var(--lex-border); background: var(--lex-sidebar);">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                        <div>
                            <label class="lex-label">Búsqueda por Radicado</label>
                            <input type="text" class="lex-input" placeholder="Ej: 2024-001..." value="${state.filters.numero_proceso}" oninput="App.updateFilter('numero_proceso', this.value)">
                        </div>
                        <div>
                            <label class="lex-label">Estado Procesal</label>
                            <select class="lex-input" onchange="App.updateFilter('estado', this.value)">
                                <option value="">TODOS LOS ESTADOS</option>
                                <option value="ACTIVO" ${state.filters.estado === 'ACTIVO' ? 'selected' : ''}>ACTIVO</option>
                                <option value="TERMINADO" ${state.filters.estado === 'TERMINADO' ? 'selected' : ''}>TERMINADO</option>
                                <option value="SUSPENDIDO" ${state.filters.estado === 'SUSPENDIDO' ? 'selected' : ''}>SUSPENDIDO</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;

            // Lista de Expedientes
            html += `<div class="expedientes-grid">`;
            procesos.forEach(p => {
                html += `
                    <div class="lex-expediente">
                        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                            <div>
                                <span style="font-size:0.7rem; color:var(--lex-text-muted);">${p.fecha_radicacion}</span>
                                <h3 style="margin: 0.5rem 0; font-size: 1.3rem;">RADICADO: <span class="accent-color">${p.numero_proceso}</span></h3>
                                <p style="font-size:0.85rem; opacity:0.8; margin-bottom: 1rem;">${p.partes}</p>
                            </div>
                            <span class="lex-status lex-status-${p.estado.toLowerCase() === 'activo' ? 'activo' : 'error'}">${p.estado}</span>
                        </div>
                        <div style="border-top:1px solid var(--lex-border); padding-top:1rem; display:flex; gap:1rem; justify-content:flex-end;">
                            <button class="lex-btn" style="padding:0.4rem 0.8rem; font-size:0.6rem;" onclick="App.viewDetail(${p.id})">CONSULTAR FOJA</button>
                            ${state.currentRole !== 'viewer' ? `<button class="lex-btn" style="padding:0.4rem 0.8rem; font-size:0.6rem;" onclick="App.editExpediente(${p.id})">ANOTAR</button>` : ''}
                        </div>
                    </div>
                `;
            });
            html += `</div>`;

            if (procesos.length === 0) {
                html += `<div style="text-align:center; padding:5rem; opacity:0.4;">EL ARCHIVO NO CONTIENE REGISTROS PARA LA CONSULTA ACTUAL.</div>`;
            }

            this.appContent.innerHTML = html;
        } catch (err) {
            this.renderError(err);
        }
    },

    async showExpedienteDetail(state) {
        this.clearContent();
        try {
            const p = await window.GahenaxAPI.getExpediente(state.activeId);
            let html = this.header(`Expediente N° ${p.numero_proceso}`, `<button class="lex-btn" onclick="App.navigate('list')"><i class="fas fa-chevron-left"></i> REGRESAR AL ARCHIVO</button>`);

            html += `
                <div class="lex-expediente" style="padding: 3rem;">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 3rem; margin-bottom: 3rem;">
                        <div>
                            <label class="lex-label">Fecha de Apertura</label>
                            <p style="font-family:var(--lex-font-heading); font-size:1.2rem;">${p.fecha_radicacion}</p>
                        </div>
                        <div>
                            <label class="lex-label">Calificación Actual</label>
                            <p><span class="lex-status lex-status-activo">${p.estado}</span></p>
                        </div>
                        <div class="full-width" style="grid-column: span 2;">
                            <label class="lex-label">Cuerpo de Intervinientes</label>
                            <p style="font-size:1.1rem; border-bottom:1px solid var(--lex-border); padding-bottom:0.5rem;">${p.partes}</p>
                        </div>
                        <div class="full-width" style="grid-column: span 2;">
                            <label class="lex-label">Observaciones de la Magistratura</label>
                            <div style="background:rgba(255,255,255,0.02); padding:1.5rem; font-family:var(--lex-font-heading); line-height:1.8; color:var(--lex-text-muted); font-style:italic;">
                                ${p.observaciones || 'No se han registrado anotaciones adicionales en este folio.'}
                            </div>
                        </div>
                    </div>

                    <div style="margin-top:4rem;">
                        <h4 style="border-bottom:1px solid var(--lex-border); padding-bottom:0.5rem; margin-bottom:1.5rem;">REGISTRO DE ACTUACIONES (SISTEMA DE AUDITORÍA)</h4>
                        <div class="audit-log">
                            ${p.audit_trail.map(log => `
                                <div style="font-size:0.75rem; margin-bottom:0.75rem; display:flex; gap:1rem;">
                                    <span style="color:var(--lex-accent); min-width:140px;">[${new Date(log.timestamp).toLocaleString()}]</span>
                                    <span style="color:var(--lex-text-muted); font-weight:600;">${log.usuario}:</span>
                                    <span>${log.accion} en ${log.entidad}</span>
                                    ${log.campo_modificado ? `<span class="italic" style="opacity:0.6;">(${log.campo_modificado}: ${log.valor_anterior} → ${log.valor_nuevo})</span>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
            this.appContent.innerHTML = html;
        } catch (err) { this.renderError(err); }
    },

    showAnalysisReport(state) {
        // state.lastAnalysis y state.lastQuery deben estar poblados
        const result = state.lastAnalysis;
        const query = state.lastQuery;

        let html = this.header('Informe de Análisis Jurídico', `<button class="lex-btn" onclick="App.navigate('list')"><i class="fas fa-chevron-left"></i> CERRAR INFORME</button>`);

        html += `
            <div class="lex-invoice-report">
                <div class="lex-invoice-header">
                    <h2 style="margin:0; letter-spacing:4px;">GAHENAX AI SYSTEM</h2>
                    <p style="font-size:0.8rem; opacity:0.6; margin-top:0.5rem;">MOTOR DE INTELIGENCIA PROCESAL V1.1</p>
                    <div style="margin-top:1rem; font-size:0.7rem;">CONSULTA N° ${Math.floor(Math.random() * 1000000)} | EMITIDO: ${new Date().toLocaleString()}</div>
                </div>
                <div style="margin-bottom:2rem; font-style:italic; text-align:center; opacity:0.8;">
                    "En relación a la consulta: ${query}"
                </div>
                <div class="lex-invoice-body">
                    ${result.analysis}
                    
                    <h3 style="margin-top:3rem; border-bottom:1px solid var(--lex-border);">HIPÓTESIS Y PRECEDENTES</h3>
                    <ul>
                        ${result.hypothesis.map(h => `<li style="margin-bottom:1rem;">${h}</li>`).join('')}
                    </ul>
                </div>
                <div style="margin-top:4rem; border-top:1px solid var(--lex-border); padding-top:1rem; font-size:0.7rem; color:var(--lex-text-muted); text-align:center;">
                    <p>${result.disclaimer}</p>
                    <p style="margin-top:1rem; font-weight:700;">DOCUMENTO GENERADO PARA USO EXCLUSIVO DE PROFESIONALES DEL DERECHO.</p>
                </div>
            </div>
        `;
        this.appContent.innerHTML = html;
    },

    showExpedienteForm(state) {
        this.clearContent();
        const data = state.editData; // null si es nuevo
        let html = this.header(data ? 'Edición de Expediente' : 'Apertura de Expediente', `<button class="lex-btn" onclick="App.navigate('list')">ABORTAR</button>`);

        html += `
            <div class="lex-expediente" style="max-width: 800px; margin: 0 auto;">
                <form id="lex-form">
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                        <div>
                            <label class="lex-label">Código de Radicado *</label>
                            <input type="text" name="numero_proceso" class="lex-input" value="${data?.numero_proceso || ''}" required>
                        </div>
                        <div>
                            <label class="lex-label">Fecha de Inicio *</label>
                            <input type="date" name="fecha_radicacion" class="lex-input" value="${data?.fecha_radicacion || ''}" required>
                        </div>
                        <div>
                            <label class="lex-label">Calificación Jurídica *</label>
                            <select name="estado" class="lex-input" required>
                                <option value="ACTIVO" ${data?.estado === 'ACTIVO' ? 'selected' : ''}>ACTIVO</option>
                                <option value="TERMINADO" ${data?.estado === 'TERMINADO' ? 'selected' : ''}>TERMINADO</option>
                                <option value="SUSPENDIDO" ${data?.estado === 'SUSPENDIDO' ? 'selected' : ''}>SUSPENDIDO</option>
                            </select>
                        </div>
                        <div>
                            <label class="lex-label">Clase de Proceso</label>
                            <input type="text" name="clase_proceso" class="lex-input" value="${data?.clase_proceso || ''}">
                        </div>
                        <div style="grid-column: span 2;">
                            <label class="lex-label">Intervinientes (Sujetos Procesales) *</label>
                            <input type="text" name="partes" class="lex-input" value="${data?.partes || ''}" required>
                        </div>
                        <div style="grid-column: span 2;">
                            <label class="lex-label">Anotaciones y Hechos</label>
                            <textarea name="observaciones" class="lex-input" style="height:150px; resize:none;">${data?.observaciones || ''}</textarea>
                        </div>
                    </div>
                    <div style="margin-top:3rem;">
                        <button type="submit" class="lex-btn lex-btn-primary" style="width:100%; justify-content:center;">REFORZAR REGISTRO</button>
                    </div>
                </form>
            </div>
        `;
        this.appContent.innerHTML = html;

        document.getElementById('lex-form').onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const jsonData = Object.fromEntries(formData.entries());
            try {
                await window.GahenaxAPI.saveExpediente(jsonData, data?.id);
                App.navigate('list');
            } catch (err) { alert(err.message); }
        };
    },

    showSettingsArchive(state) {
        this.clearContent();
        let html = this.header('Archivo Central GAHENAX', '');
        html += `
            <div class="lex-expediente">
                <h4 style="margin-bottom:1.5rem; border-bottom:1px solid var(--lex-border); padding-bottom:0.5rem;"><i class="fas fa-microchip"></i> JULES CONTROL CENTER</h4>
                <p style="font-size:0.75rem; color:var(--lex-text-muted); margin-bottom:1.5rem;">Delegación de tareas asíncronas de mantenimiento y despliegue.</p>
                <div style="display:flex; flex-direction:column; gap:1rem;">
                    <button class="lex-btn" onclick="App.dispatchJules('AUDIT', 'Security Scan')">
                        <i class="fas fa-shield-halved"></i> AUDITORÍA DE SEGURIDAD
                    </button>
                    <button class="lex-btn" onclick="App.dispatchJules('EXEC', 'Build Portable', 'python build_portable.py --src ./static --out ./release --name Chechy --version 1.1.0 --platform windows')">
                        <i class="fas fa-box-open"></i> GENERAR RELEASE ZIP
                    </button>
                </div>
                <div id="jules-status-panel" style="margin-top:2rem; padding:1rem; background:rgba(0,0,0,0.2); font-size:0.7rem; display:none;">
                    <!-- Status injection -->
                </div>
            </div>
        `;
        this.appContent.innerHTML = html;
    },

    showSupportDesk(state) {
        this.clearContent();
        let html = this.header('Soporte CRM', '');

        html += `
            <div class="lex-expediente" style="max-width: 800px; margin: 0 auto;">
                <div style="margin-bottom: 2rem; padding: 1.5rem; background: rgba(99, 102, 241, 0.1); border-left: 3px solid var(--lex-accent);">
                    <h3 style="margin-bottom: 1rem;"><i class="fas fa-info-circle"></i> Sistema de Soporte</h3>
                    <p style="margin: 0; opacity: 0.9;">
                        Utiliza este formulario para reportar problemas, solicitar funcionalidades o hacer consultas sobre el sistema ChechyLegis.
                    </p>
                </div>

                <form id="support-form">
                    <div style="display:grid; gap: 2rem;">
                        <div>
                            <label class="lex-label">Nombre Completo *</label>
                            <input type="text" name="nombre" class="lex-input" required>
                        </div>
                        
                        <div>
                            <label class="lex-label">Correo Electrónico *</label>
                            <input type="email" name="email" class="lex-input" required>
                        </div>
                        
                        <div>
                            <label class="lex-label">Empresa / Organización</label>
                            <input type="text" name="empresa" class="lex-input" placeholder="Opcional">
                        </div>
                        
                        <div>
                            <label class="lex-label">Prioridad *</label>
                            <select name="prioridad" class="lex-input" required>
                                <option value="BAJA">Baja - Consulta general</option>
                                <option value="MEDIA" selected>Media - Problema que afecta el uso</option>
                                <option value="ALTA">Alta - Error crítico</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="lex-label">Asunto *</label>
                            <input type="text" name="asunto" class="lex-input" placeholder="Ej: Error al conectar con el servidor" required>
                        </div>
                        
                        <div>
                            <label class="lex-label">Descripción del Problema *</label>
                            <textarea name="descripcion" class="lex-input" style="height:150px; resize:vertical;" placeholder="Describe el problema con el mayor detalle posible..." required></textarea>
                        </div>
                    </div>
                    
                    <div style="margin-top:3rem; display: flex; gap: 1rem;">
                        <button type="submit" class="lex-btn lex-btn-primary" style="flex: 1; justify-content:center;">
                            <i class="fas fa-paper-plane"></i> ENVIAR TICKET
                        </button>
                        <button type="button" class="lex-btn" onclick="App.navigate('list')" style="padding: 0 2rem;">
                            CANCELAR
                        </button>
                    </div>
                </form>
                
                <div id="support-response" style="margin-top: 2rem; display: none;">
                    <!-- Response will be injected here -->
                </div>
            </div>
        `;

        this.appContent.innerHTML = html;

        // Form submission handler
        document.getElementById('support-form').onsubmit = async (e) => {
            e.preventDefault();
            const responseDiv = document.getElementById('support-response');
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"]');

            // Disable button during submission
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ENVIANDO...';

            const formData = new FormData(form);
            const ticketData = {
                subject: formData.get('asunto'),
                description: `
Solicitante: ${formData.get('nombre')}
Email: ${formData.get('email')}
Empresa: ${formData.get('empresa') || 'N/A'}
Prioridad: ${formData.get('prioridad')}

Descripción:
${formData.get('descripcion')}
                `.trim(),
                priority: formData.get('prioridad'),
                user_email: formData.get('email')
            };

            try {
                await window.GahenaxAPI.submitSupportTicket(ticketData);

                responseDiv.style.display = 'block';
                responseDiv.innerHTML = `
                    <div style="padding: 2rem; background: rgba(16, 185, 129, 0.1); border: 1px solid var(--lex-accent); text-align: center;">
                        <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--lex-accent); margin-bottom: 1rem;"></i>
                        <h3 style="color: var(--lex-accent); margin-bottom: 1rem;">TICKET ENVIADO EXITOSAMENTE</h3>
                        <p style="opacity: 0.9;">
                            Tu solicitud ha sido registrada en nuestro sistema CRM. Nuestro equipo te contactará a<br>
                            <strong>${formData.get('email')}</strong> en las próximas 24-48 horas.
                        </p>
                        <button class="lex-btn" onclick="App.navigate('list')" style="margin-top: 1.5rem;">
                            <i class="fas fa-home"></i> VOLVER AL INICIO
                        </button>
                    </div>
                `;
                form.style.display = 'none';

            } catch (err) {
                // Si el backend no está disponible, mostramos un mensaje alternativo
                if (err.message.includes('FAILED (NETWORK)')) {
                    responseDiv.style.display = 'block';
                    responseDiv.innerHTML = `
                        <div style="padding: 2rem; background: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; text-align: center;">
                            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #eab308; margin-bottom: 1rem;"></i>
                            <h3 style="color: #eab308; margin-bottom: 1rem;">MODO OFFLINE</h3>
                            <p style="opacity: 0.9; margin-bottom: 1.5rem;">
                                El sistema CRM no está disponible en este momento. Por favor, contacta directamente a:
                            </p>
                            <div style="background: rgba(0,0,0,0.3); padding: 1rem; font-family: monospace;">
                                <strong>Email:</strong> soporte@gahenax.com<br>
                                <strong>Teléfono:</strong> +57 300 XXX XXXX
                            </div>
                            <p style="margin-top: 1.5rem; font-size: 0.85rem; opacity: 0.7;">
                                O espera a que el backend esté en línea para enviar tickets automáticamente.
                            </p>
                        </div>
                    `;
                } else {
                    responseDiv.style.display = 'block';
                    responseDiv.innerHTML = `
                        <div style="padding: 2rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--lex-error); text-align: center;">
                            <i class="fas fa-times-circle" style="font-size: 3rem; color: var(--lex-error); margin-bottom: 1rem;"></i>
                            <h3 style="color: var(--lex-error); margin-bottom: 1rem;">ERROR AL ENVIAR</h3>
                            <p>${err.message}</p>
                        </div>
                    `;
                }

                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> REINTENTAR ENVÍO';
            }
        };
    },

    renderError(err) {
        this.appContent.innerHTML = `
            <div class="lex-expediente" style="border-color:var(--lex-error); text-align:center; padding:5rem;">
                <h2 style="color:var(--lex-error);">FALLO DE SISTEMA</h2>
                <p>${err.message}</p>
                <button class="lex-btn" onclick="location.reload()" style="margin-top:2rem;">REINTENTAR ACCESO</button>
            </div>
        `;
    }
};

window.GahenaxRender = Render;
