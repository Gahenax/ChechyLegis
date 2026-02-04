/**
 * GAHENAX CORE - State Management
 * Lex-Tech Edition
 */

const Store = {
    state: {
        currentRole: 'admin',
        currentUser: 'ADMIN',
        filters: JSON.parse(localStorage.getItem('gahenax_filters')) || {
            fecha_desde: '',
            fecha_hasta: '',
            estado: '',
            numero_proceso: ''
        },
        currentView: 'list', // list, detail, form, support, settings
        activeTaskId: null
    },

    setRole(role) {
        this.state.currentRole = role;
        this.state.currentUser = role.toUpperCase();
        this.notify();
    },

    setFilters(filters) {
        this.state.filters = { ...this.state.filters, ...filters };
        localStorage.setItem('gahenax_filters', JSON.stringify(this.state.filters));
        this.notify();
    },

    setView(view) {
        this.state.currentView = view;
        this.notify();
    },

    // Simple observer pattern
    listeners: [],
    subscribe(fn) {
        this.listeners.push(fn);
    },
    notify() {
        this.listeners.forEach(fn => fn(this.state));
    }
};

window.GahenaxStore = Store;
