# CORRECCIÓN: Problema "FAILED (NETWORK)" en Dominio HTML

## Problema Identificado

El error **"FAILED (NETWORK)"** aparece cuando el frontend de ChechyLegis intenta conectarse al backend API pero no puede establecer la conexión.

### Causas Comunes:
1. ✗ El backend no está corriendo
2. ✗ La URL del API no está configurada correctamente
3. ✗ Problemas de CORS (si backend está en dominio diferente)
4. ✗ El backend no está desplegado en el servidor (solo HTML estático)

## Soluciones Implementadas

### 1. **Configuración Flexible del API** ✅

Creamos `static/config.js` que permite configurar la URL del backend según el entorno:

```javascript
// Para desarrollo local
window.GAHENAX_API_URL = '/api';

// Para producción con backend en otro servidor
window.GAHENAX_API_URL = 'https://tu-api.railway.app/api';
```

### 2. **Mejor Manejo de Errores de Red** ✅

Actualizamos `static/api/client.js` para:
- Detectar errores de conexión de red
- Mostrar mensajes más claros al usuario
- Manejar gracefully la falta de conexión al backend

### 3. **Implementación del Módulo de Soporte** ✅

Añadimos el método `showSupportDesk()` en `static/ui/render.js` con:
- Formulario completo de soporte CRM
- Manejo de errores cuando el backend no está disponible
- Mensaje alternativo con información de contacto en modo offline

### 4. **Guía de Despliegue** ✅

Creamos `GUIA_DESPLIEGUE_HOSTINGER.md` con instrucciones detalladas para:
- Desplegar solo frontend estático (página de descarga)
- Desplegar aplicación completa con backend
- Configurar backend en servicios externos (Railway, Render, etc.)

## Archivos Modificados

| Archivo | Cambio | Estado |
|---------|--------|--------|
| `static/api/client.js` | Mejor manejo de errores + URL configurable | ✅ Actualizado |
| `static/config.js` | Nuevo archivo de configuración | ✅ Creado |
| `static/index.html` | Incluye config.js | ✅ Actualizado |
| `static/ui/render.js` | Implementado showSupportDesk() | ✅ Actualizado |
| `GUIA_DESPLIEGUE_HOSTINGER.md` | Guía completa de deployment | ✅ Creado |

## Pasos Siguientes

### Para Testing Local (Recomendado)

1. **Iniciar el backend:**
   ```bash
   cd c:\Users\USUARIO\OneDrive\Desktop\Legischechy
   python -m uvicorn app.main:app --reload
   ```

2. **Abrir la aplicación:**
   - Abre un navegador
   - Navega a: `http://localhost:8000/static/index.html`
   - O visita: `http://localhost:8000` (si está configurado el routing)

### Para Desplegar en Hostinger

#### Opción A: Solo Frontend Estático (Más Fácil)
1.  Sube solo `gahenax_hub.html` a Hostinger
2. Renómbralo a `index.html`
3. Sube la carpeta `downloads/` con los archivos
4. ✅ Listo - no necesita backend

#### Opción B: Aplicación Completa con Backend en Railway (Recomendado)

**Paso 1: Deploy Backend en Railway**
1. Crea cuenta en [Railway.app](https://railway.app)
2. Conecta tu repositorio o sube el código
3. Railway detectará automáticamente que es Python
4. Configura las variables de entorno necesarias
5. Obtén la URL del deploy (ej: `https://chechylegis.up.railway.app`)

**Paso 2: Configurar Frontend**
1. Edita `static/config.js`:
   ```javascript
   window.GAHENAX_API_URL = 'https://chechylegis.up.railway.app/api';
   ```

2. Sube la carpeta `static/` completa a Hostinger

**Paso 3: Configurar CORS en Backend**
En `app/main.py`, añade:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio-hostinger.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Verificación

Después del despliegue, abre la consola del navegador (F12) y verifica:

```
GAHENAX Config: API URL = [la URL configurada]
```

Si ves errores de red:
1. Verifica que el backend esté corriendo
2. Revisa que la URL en `config.js` sea correcta
3. Comprueba que CORS esté configurado si backend está en otro dominio

## Modo Offline

Ahora la aplicación **maneja gracefully** la falta de backend:
- ✅ El formulario de soporte muestra información de contacto alternativa
- ✅ Los errores son más descriptivos
- ✅ El usuario sabe exactamente qué hacer

## Soporte

Si sigues teniendo problemas, el formulario de soporte ahora incluye:
- Información de contacto directa para modo offline
- Mejor feedback al usuario
- Instrucciones claras sobre qué hacer

---

**Fecha de Corrección:** 2026-02-04
**Versión:** ChechyLegis v1.1.0-REF
