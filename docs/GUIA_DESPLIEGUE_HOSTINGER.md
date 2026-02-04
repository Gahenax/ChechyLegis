# GUÍA DE DESPLIEGUE EN HOSTINGER

## Problema Actual

El error **"FAILED (NETWORK)"** ocurre porque:
- El frontend HTML está intentando conectarse al backend API
- El backend no está disponible o no está corriendo
- La URL de la API no está configurada correctamente

## Soluciones

### OPCIÓN 1: Despliegue Solo Frontend (Página Estática)

Si solo quieres mostrar la **página de descarga** (gahenax_hub.html), sigue estos pasos:

1. **Sube solo `gahenax_hub.html`** a Hostinger
2. Renómbralo a `index.html` en Hostinger
3. Sube también la carpeta `/downloads/` con los archivos descargables
4. Esta página NO requiere backend y funcionará perfectamente

**Archivos a subir:**
```
public_html/
├── index.html (renombrado de gahenax_hub.html)
└── downloads/
    └── Chechy-v1.1.0-windows.zip
```

---

### OPCIÓN 2: Despliegue Completo (Frontend + Backend)

Para tener la aplicación completa funcionando con todas las características:

#### Paso 1: Configurar Backend en Hostinger

Hostinger soporta Python si tienes un plan VPS o Cloud. **NO funciona en hosting compartido básico**.

Si tienes VPS/Cloud:

1. Conecta por SSH a tu servidor
2. Instala las dependencias:
   ```bash
   cd /home/tu-usuario/public_html
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Configura un servicio systemd para mantener el backend corriendo:
   ```bash
   sudo nano /etc/systemd/system/chechylegis.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=ChechyLegis Backend API
   After=network.target

   [Service]
   User=tu-usuario
   WorkingDirectory=/home/tu-usuario/public_html
   Environment="PATH=/home/tu-usuario/public_html/venv/bin"
   ExecStart=/home/tu-usuario/public_html/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```

4. Inicia el servicio:
   ```bash
   sudo systemctl enable chechylegis
   sudo systemctl start chechylegis
   ```

5. Configura nginx como proxy reverso (si no está ya configurado):
   ```nginx
   location /api {
       proxy_pass http://localhost:8000/api;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

#### Paso 2: Configurar Frontend

1. Edita `static/config.js` en tu proyecto local:
   ```javascript
   // Para producción en Hostinger (mismo dominio)
   window.GAHENAX_API_URL = '/api';
   ```

2. Sube toda la carpeta `static/` a Hostinger:
   ```
   public_html/
   ├── static/
   │   ├── config.js
   │   ├── index.html
   │   ├── app.js
   │   ├── styles.css
   │   ├── api/
   │   ├── ui/
   │   └── state/
   └── app/ (código Python del backend)
   ```

3. Configura el archivo `.htaccess` para redirecciones SPA:
   ```apache
   RewriteEngine On
   RewriteBase /

   # API requests go to the backend
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^api/(.*)$ http://localhost:8000/api/$1 [P,L]

   # Everything else goes to index.html (SPA)
   RewriteCond %{REQUEST_FILENAME} !-f
   RewriteCond %{REQUEST_FILENAME} !-d
   RewriteRule ^(.*)$ /static/index.html [L]
   ```

---

### OPCIÓN 3: Backend Separado (Recomendado para Producción)

Si el backend está en un servidor diferente (ej: Railway, Render, Heroku):

1. Despliega el backend en el servicio cloud de tu elección
2. Obtén la URL del backend (ej: `https://chechylegis-api.railway.app`)
3. Edita `static/config.js`:
   ```javascript
   window.GAHENAX_API_URL = 'https://chechylegis-api.railway.app/api';
   ```
4. Sube solo la carpeta `static/` a Hostinger
5. Hostinger solo servirá el frontend estático

**IMPORTANTE:** Necesitarás configurar CORS en el backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Tu dominio de Hostinger
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Verificación

Después del despliegue, verifica en la consola del navegador:

```
GAHENAX Config: API URL = /api
```

O la URL que hayas configurado.

---

## Para Testing Local

Para probar localmente antes de subir a Hostinger:

1. Inicia el backend:
   ```bash
   cd c:\Users\USUARIO\OneDrive\Desktop\Legischechy
   python -m uvicorn app.main:app --reload
   ```

2. Abre `static/index.html` en un navegador
   - O usa un servidor local: `python -m http.server 8080`
   - Luego abre: `http://localhost:8080/static/index.html`

---

## Resumen Rápido

| Escenario | Solución | Dificultad |
|-----------|----------|------------|
| Solo página de descarga | Sube `gahenax_hub.html` | ⭐ Fácil |
| Frontend + Backend (mismo servidor) | VPS/Cloud + configuración nginx | ⭐⭐⭐ Avanzado |
| Frontend en Hostinger + Backend separado | Backend en Railway/Render | ⭐⭐ Medio |

**Recomendación:** Para empezar rápido, usa la **Opción 1** o la **Opción 3** con backend en Railway (gratuito).
