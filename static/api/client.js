/**
 * GAHENAX CORE - API Client
 * Lex-Tech Architecture
 */

const APIClient = {
    // Configuración del backend
    // Para desarrollo local: '/api' (relativo)
    // Para producción: especifica la URL completa, ej: 'https://tu-dominio.com/api'
    BASE_URL: window.GAHENAX_API_URL || '/api',

    async request(endpoint, method = 'GET', body = null) {
        const state = window.GahenaxStore.state;
        const headers = {
            'Content-Type': 'application/json',
            'X-User-Role': state.currentRole,
            'X-User-Name': `Gahenax_Lex_${state.currentRole}`,
            'Authorization': `Bearer ${state.currentRole === 'admin' ? 'admin-token' : 'operator-token'}`
        };

        const config = { method, headers };
        if (body) config.body = JSON.stringify(body);

        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, config);

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Fallo de Protocolo' }));
                throw new Error(error.detail || 'Error en Gahenax Core');
            }

            return response.json();
        } catch (error) {
            // Mejor manejo de errores de red
            if (error.name === 'TypeError' && error.message.includes('fetch')) {
                throw new Error('FAILED (NETWORK): No se puede conectar al servidor. Verifica que el backend esté corriendo.');
            }
            throw error;
        }
    },

    async getExpedientes(filters) {
        const activeFilters = {};
        for (const [key, value] of Object.entries(filters)) {
            if (value) activeFilters[key] = value;
        }
        const query = new URLSearchParams(activeFilters).toString();
        return this.request(`/procesos?${query}`);
    },

    async getExpediente(id) {
        return this.request(`/procesos/${id}`);
    },

    async saveExpediente(data, id = null) {
        if (id) return this.request(`/procesos/${id}`, 'PUT', data);
        return this.request('/procesos', 'POST', data);
    },

    async deleteExpediente(id) {
        return this.request(`/procesos/${id}`, 'DELETE');
    },

    async analyzeCriminalCase(query) {
        return this.request(`/analysis/criminal?query=${encodeURIComponent(query)}`, 'POST');
    },

    async submitSupportTicket(data) {
        return this.request('/support/ticket', 'POST', data);
    },

    async dispatchJulesTask(data) {
        return this.request('/jules/dispatch', 'POST', data);
    },

    async fetchJulesReport(taskId) {
        return this.request(`/jules/status/${taskId}`);
    }
};

window.GahenaxAPI = APIClient;
