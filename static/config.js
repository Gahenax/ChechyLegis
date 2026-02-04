/**
 * GAHENAX Configuration
 * Configura este archivo según tu entorno de despliegue
 */

// IMPORTANTE: Cambia esta URL según donde esté desplegado tu backend

// Para desarrollo local (cuando corres el backend en tu computadora):
// window.GAHENAX_API_URL = '/api';  // URL relativa

// Para producción en Hostinger (si el backend está en el mismo dominio):
// window.GAHENAX_API_URL = '/api';  // URL relativa

// Para producción con backend separado (si el backend está en otro servidor):
// window.GAHENAX_API_URL = 'https://api.tudominio.com/api';  // URL absoluta

// Configuración por defecto (desarrollo local)
window.GAHENAX_API_URL = '/api';

// Si estás desplegando SOLO el frontend en Hostinger sin backend:
// Considera comentar la línea anterior y descomentar la siguiente:
// window.GAHENAX_API_URL = null; // Esto deshabilitará las funciones que requieren backend

console.log('GAHENAX Config: API URL =', window.GAHENAX_API_URL || 'default (/api)');
