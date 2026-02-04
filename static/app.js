/**
 * GAHENAX CORE - App Orchestrator
 * Lex-Tech Tribunal Digital
 */

const App = {
    async init() {
        console.log("GAHENAX Core Initializing (Lex-Tech Standard)...");

        // Initialize UI Engine
        window.GahenaxRender.init('content');

        // Sync Initial State
        const initialState = window.GahenaxStore.state;
        this.updateUI(initialState);

        // Role Sync
        document.getElementById('role-selector').onchange = (e) => {
            window.GahenaxStore.setRole(e.target.value);
            document.getElementById('current-user-display').innerText = e.target.value.toUpperCase();
        };

        // Navigation
        document.getElementById('nav-list').onclick = () => this.navigate('list');
        document.getElementById('nav-create').onclick = () => this.navigate('form');
        document.getElementById('nav-support').onclick = () => this.navigate('support');
        document.getElementById('nav-settings').onclick = () => this.navigate('settings');

        // Store Subscription
        window.GahenaxStore.subscribe((state) => this.updateUI(state));
    },

    navigate(view) {
        // Clear edit state if navigating away from form
        if (view !== 'form') window.GahenaxStore.state.editData = null;

        window.GahenaxStore.setView(view);
        this.updateActiveNav(`nav-${view === 'list' ? 'list' : (view === 'form' ? 'create' : (view === 'support' ? 'support' : 'settings'))}`);
    },

    updateUI(state) {
        window.GahenaxRender.renderLayout(state);
    },

    updateActiveNav(id) {
        document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
        const el = document.getElementById(id);
        if (el) el.classList.add('active');
    },

    updateFilter(key, val) {
        const filters = { ...window.GahenaxStore.state.filters, [key]: val };
        window.GahenaxStore.setFilters(filters);
    },

    async viewDetail(id) {
        window.GahenaxStore.state.activeId = id;
        this.navigate('detail');
    },

    async editExpediente(id) {
        try {
            const data = await window.GahenaxAPI.getExpediente(id);
            window.GahenaxStore.state.editData = data;
            this.navigate('form');
        } catch (err) { alert(err.message); }
    },

    // Global AI Search Bridge
    async performAISearch() {
        const input = document.getElementById('ai-search-input');
        const query = input.value.trim();
        if (!query) return;

        window.GahenaxRender.clearContent();
        try {
            const result = await window.GahenaxAPI.analyzeCriminalCase(query);
            window.GahenaxStore.state.lastAnalysis = result;
            window.GahenaxStore.state.lastQuery = query;
            this.navigate('analysis');
        } catch (err) { window.GahenaxRender.renderError(err); }
    },

    async dispatchJules(action, label, content = null) {
        const panel = document.getElementById('jules-status-panel');
        panel.style.display = 'block';
        panel.innerHTML = `<div style="color:var(--lex-primary);">DESPACHANDO TAREA: ${label}...</div>`;

        try {
            const data = { action, content: content || label };
            const { task_id } = await window.GahenaxAPI.dispatchJulesTask(data);
            panel.innerHTML = `<div style="color:var(--lex-primary);">TAREA EN COLA: ${task_id}</div>`;

            // Poll for status
            const poll = setInterval(async () => {
                try {
                    const report = await window.GahenaxAPI.fetchJulesReport(task_id);
                    if (report.status === 'DONE' || report.status === 'FAILED' || report.status === 'ERROR') {
                        clearInterval(poll);
                        const color = report.status === 'DONE' ? 'var(--success)' : 'var(--error)';
                        panel.innerHTML = `
                            <div style="color:${color}; font-weight:700;">FINALIZADO: ${report.status}</div>
                            <div style="margin-top:0.5rem; opacity:0.8; white-space:pre-wrap;">${report.message}</div>
                        `;
                    } else {
                        panel.innerHTML = `<div style="color:var(--lex-accent);">JULES PROCESANDO: ${task_id}... (${report.status})</div>`;
                    }
                } catch (e) { /* Pending or error */ }
            }, 3000);

        } catch (err) {
            panel.innerHTML = `<div style="color:var(--lex-error);">FALLO DE DESPACHO: ${err.message}</div>`;
        }
    }
};

// Global Exposure for UI Handlers
window.App = App;

// Initialization
document.addEventListener('DOMContentLoaded', () => App.init());

/**
 * Chat Support Logic (Digital Bridge)
 */
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const container = document.getElementById('chat-messages');
    const text = input.value.trim();
    if (!text) return;

    container.innerHTML += `<div class="chat-message user" style="border-radius:0; border:1px solid var(--lex-border); background:rgba(255,255,255,0.02);">${text}</div>`;
    input.value = '';
    container.scrollTop = container.scrollHeight;

    try {
        container.innerHTML += `<div class="chat-message assistant" id="lex-typing">Iniciando consulta al motor jurídico...</div>`;
        const result = await window.GahenaxAPI.analyzeCriminalCase(text);
        document.getElementById('lex-typing').remove();

        container.innerHTML += `
            <div class="chat-message assistant" style="border-radius:0; border:1px solid var(--lex-primary);">
                <span class="accent-color" style="font-weight:700;">GAHENAX LEGAL REPORT:</span><br>
                ${result.analysis.substring(0, 150)}...
                <br><br>
                <button class="lex-btn" style="padding:0.2rem 0.6rem; font-size:0.6rem;" onclick="App.navigate('analysis'); GahenaxStore.state.lastAnalysis = ${JSON.stringify(result).replace(/"/g, '&quot;')}; GahenaxStore.state.lastQuery = '${text}';">VER INFORME EXPERTO</button>
            </div>`;
        container.scrollTop = container.scrollHeight;
    } catch (err) {
        if (document.getElementById('lex-typing')) document.getElementById('lex-typing').remove();
        container.innerHTML += `<div class="chat-message assistant" style="color:var(--lex-error)">FALLO DE CONEXIÓN: ${err.message}</div>`;
    }
}

function toggleChat() {
    document.getElementById('ai-chat-widget').classList.toggle('hidden');
}

// Map old global calls to the new orchestrator
function performAISearch() { App.performAISearch(); }
