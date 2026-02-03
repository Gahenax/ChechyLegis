# 🏛️ Archivo Virtual de Procesos Judiciales con IA

Sistema completo de gestión de procesos judiciales con capacidades de **Inteligencia Artificial** usando **Gemini API**.

## 🚀 Características

### MVP Base (Fase 1)
- ✅ **CRUD completo** de procesos judiciales
- ✅ **Auditoría total** de cambios (quién, cuándo, qué cambió)
- ✅ **Control de acceso** por roles (Admin, Operator, Viewer)
- ✅ **Filtros avanzados** (fecha, estado, número)
- ✅ **Validación estricta** de datos
- ✅ **Soft delete** (borrado lógico)

### IA con Gemini (Fase 2) 🤖
- 🔍 **Búsqueda en lenguaje natural**: "procesos activos de enero"
- 📊 **Análisis automático** de procesos con insights
- 🎯 **Búsqueda de casos similares** usando análisis semántico
- 💬 **Asistente conversacional** para consultas generales
- 💡 **Sugerencias inteligentes** de búsquedas relacionadas

## 📋 Requisitos

- Python 3.8+
- API Key de Gemini (gratis en https://aistudio.google.com/app/apikey)

## ⚙️ Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar API Key de Gemini

Edita el archivo `.env` y reemplaza `tu_api_key_aqui` con tu API key real:

```env
GEMINI_API_KEY=AIzaSy...tu_key_real_aqui
```

**Obtén tu API key gratis aquí:** https://aistudio.google.com/app/apikey

### 3. Iniciar el servidor

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Abrir en el navegador

Navega a: **http://127.0.0.1:8000**

## 🎯 Uso del Sistema

### Funciones Básicas

1. **Crear Proceso**: Click en "Nuevo Proceso"
2. **Filtrar**: Usa los filtros por fecha, estado, número
3. **Ver Detalle**: Click en "Ver" para ver el proceso completo
4. **Editar**: Click en "Editar" (requiere rol Operator o Admin)
5. **Eliminar**: Click en "Eliminar" (solo Admin)

### Funciones de IA 🤖

#### 1. Búsqueda Inteligente
Usa la barra de búsqueda superior con lenguaje natural:

**Ejemplos:**
- "procesos activos de enero"
- "casos de María García"
- "procesos terminados este mes"
- "demandas de cuantía mayor"

#### 2. Análisis de Proceso
En cualquier proceso, click en "🤖 Analizar" para obtener:
- Resumen ejecutivo
- Alertas y puntos de atención
- Clasificación sugerida
- Acciones recomendadas

#### 3. Casos Similares
Desde el análisis de un proceso, click en "🔍 Buscar Casos Similares" para encontrar procesos relacionados usando IA semántica.

#### 4. Asistente Virtual
Click en el botón "💬 Asistente IA" (esquina inferior derecha) para chatear con el asistente legal virtual.

**Ejemplos de preguntas:**
- "¿Cómo clasifico un proceso civil?"
- "¿Qué significa estado SUSPENDIDO?"
- "¿Cuándo debo actualizar la fecha de última actuación?"

## 🔐 Roles y Permisos

| Rol | Crear | Editar | Eliminar | Ver |
|-----|-------|--------|----------|-----|
| **Viewer** | ❌ | ❌ | ❌ | ✅ |
| **Operator** | ✅ | ✅ | ❌ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ |

Cambia de rol usando el selector en la esquina superior derecha.

## 📊 API Endpoints

### CRUD Básico
- `POST /api/procesos` - Crear proceso
- `GET /api/procesos` - Listar procesos (con filtros)
- `GET /api/procesos/{id}` - Detalle + historial de auditoría
- `PUT /api/procesos/{id}` - Editar proceso
- `DELETE /api/procesos/{id}` - Eliminar (soft delete)

### Endpoints de IA
- `POST /api/ai/search` - Búsqueda en lenguaje natural
- `GET /api/ai/analyze/{id}` - Análisis automático de proceso
- `GET /api/ai/similar/{id}` - Buscar casos similares
- `POST /api/ai/chat` - Chat con asistente virtual

## 📁 Estructura del Proyecto

```
Legischechy/
├── app/
│   ├── main.py              # FastAPI app + endpoints
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── crud.py              # Operaciones CRUD + auditoría
│   ├── database.py          # Configuración DB
│   └── gemini_service.py    # Servicio de IA con Gemini
├── static/
│   ├── index.html           # UI principal
│   ├── styles.css           # Estilos
│   └── app.js               # Lógica frontend + IA
├── .env                     # Variables de entorno (API keys)
├── requirements.txt         # Dependencias Python
└── judicial_archive.db      # Base de datos SQLite
```

## 🧪 Verificación del Sistema

Ejecuta el script de verificación para probar todos los criterios:

```bash
python verify_mvp.py
```

Este script verifica:
- ✅ Creación de procesos válidos
- ❌ Validación de campos obligatorios
- 🔍 Funcionamiento de filtros
- 🧾 Auditoría de cambios
- 🔒 Control de permisos por rol
- ⏱️ Performance del sistema

## 🔧 Troubleshooting

### Error: "Servicio de IA no disponible"
**Solución:** Verifica que tu API key de Gemini esté correctamente configurada en el archivo `.env`

### Error: "Module not found"
**Solución:** Ejecuta `pip install -r requirements.txt`

### El servidor no inicia
**Solución:** Verifica que el puerto 8000 no esté en uso. Usa otro puerto: `uvicorn app.main:app --port 8001`

## 🎨 Características de la UI

- 🎨 **Diseño moderno** con gradientes y animaciones
- 📱 **Responsive** (funciona en móviles y tablets)
- 🌙 **Colores profesionales** con paleta curada
- ⚡ **Interacciones fluidas** con micro-animaciones
- 🤖 **Badges de IA** para distinguir funciones inteligentes

## 📝 Modelo de Datos

### Proceso
- `numero_proceso` (string, único, obligatorio)
- `fecha_radicacion` (date, obligatorio)
- `estado` (ACTIVO | TERMINADO | SUSPENDIDO | RECHAZADO)
- `partes` (string, obligatorio)
- `clase_proceso` (string, opcional)
- `cuantia_tipo` (MINIMA | MENOR | MAYOR, opcional)
- `fecha_ultima_actuacion` (date, opcional)
- `observaciones` (text, opcional)

### Auditoría
Cada cambio registra:
- Usuario que realizó el cambio
- Acción (CREATE | UPDATE | DELETE)
- Campo modificado
- Valor anterior y nuevo
- Timestamp

## 🚀 Próximas Funcionalidades (No implementadas)

- 📄 **OCR de documentos** escaneados
- 🏷️ **Clasificación automática** de procesos
- 📈 **Dashboard de métricas** y estadísticas
- 🔔 **Notificaciones** de cambios importantes
- 📤 **Exportación** a PDF/Excel
- 🔍 **Búsqueda por contenido** de observaciones

## 📄 Licencia

Este proyecto es un MVP para demostración de capacidades técnicas.

## 👨‍💻 Soporte

Para consultas o problemas, revisa la documentación de:
- **FastAPI**: https://fastapi.tiangolo.com/
- **Gemini API**: https://ai.google.dev/docs
- **SQLAlchemy**: https://www.sqlalchemy.org/

---

**Desarrollado con ❤️ usando FastAPI + Gemini AI**
