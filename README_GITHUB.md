# ChechyLegis 🏛️

**Archivo Virtual de Procesos Judiciales con Inteligencia Artificial**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-purple.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Características Principales

### 📋 Gestión de Procesos
- ✅ **CRUD Completo**: Crear, leer, actualizar y eliminar procesos
- 🔍 **Filtros Avanzados**: Por fecha, estado, número de proceso
- 📊 **Auditoría Total**: Registro completo de todos los cambios
- 🔐 **Control de Acceso**: Roles (Admin, Operator, Viewer)
- 💾 **Soft Delete**: Borrado lógico sin pérdida de datos

### 🤖 Inteligencia Artificial (Gemini)
- 🔎 **Búsqueda Natural**: "procesos activos de enero", "casos de María García"
- 📈 **Análisis Automático**: Resumen ejecutivo, alertas, clasificación
- 🎯 **Casos Similares**: Encuentra procesos relacionados semánticamente
- 💬 **Asistente Virtual**: Chat para consultas legales
- 💡 **Sugerencias Inteligentes**: Recomendaciones contextuales

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/ChechyLegis.git
cd ChechyLegis

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key de Gemini
# Edita .env y agrega tu API key
GEMINI_API_KEY=tu_api_key_aqui

# Iniciar servidor
uvicorn app.main:app --reload
```

### Acceso
Abre tu navegador en: **http://127.0.0.1:8000**

---

## 📸 Capturas de Pantalla

### Interfaz Principal
- Listado de procesos con filtros avanzados
- Diseño moderno y responsive
- Control de roles en tiempo real

### Búsqueda con IA
- Barra de búsqueda inteligente
- Interpretación de consultas en lenguaje natural
- Sugerencias de búsquedas relacionadas

### Análisis de Procesos
- Resumen ejecutivo generado por IA
- Alertas y puntos de atención
- Acciones recomendadas

### Chat Asistente
- Widget flotante de chat
- Respuestas contextuales
- Asistencia legal virtual

---

## 🛠️ Tecnologías

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM para gestión de base de datos
- **Pydantic**: Validación de datos
- **SQLite**: Base de datos local

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Diseño moderno con gradientes y animaciones
- **JavaScript**: Lógica de aplicación SPA

### Inteligencia Artificial
- **Google Gemini**: Modelo de lenguaje avanzado
- **Gemini 2.0 Flash**: Análisis rápido y preciso

---

## 📊 Modelo de Datos

### Proceso
```python
{
  "numero_proceso": "2024-001",
  "fecha_radicacion": "2024-01-15",
  "estado": "ACTIVO",
  "partes": "Demandante vs Demandado",
  "clase_proceso": "Civil",
  "cuantia_tipo": "MENOR",
  "observaciones": "..."
}
```

### Auditoría
```python
{
  "usuario": "admin",
  "accion": "UPDATE",
  "campo_modificado": "estado",
  "valor_anterior": "ACTIVO",
  "valor_nuevo": "TERMINADO",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 🔌 API Endpoints

### CRUD
- `POST /api/procesos` - Crear proceso
- `GET /api/procesos` - Listar procesos
- `GET /api/procesos/{id}` - Obtener detalle
- `PUT /api/procesos/{id}` - Actualizar proceso
- `DELETE /api/procesos/{id}` - Eliminar proceso

### IA
- `POST /api/ai/search` - Búsqueda en lenguaje natural
- `GET /api/ai/analyze/{id}` - Análisis automático
- `GET /api/ai/similar/{id}` - Buscar casos similares
- `POST /api/ai/chat` - Chat con asistente

---

## 🔐 Roles y Permisos

| Rol | Crear | Editar | Eliminar | Ver |
|-----|-------|--------|----------|-----|
| **Viewer** | ❌ | ❌ | ❌ | ✅ |
| **Operator** | ✅ | ✅ | ❌ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ |

---

## 📖 Documentación

- [README.md](README.md) - Documentación completa
- [PROYECTO_COMPLETADO.md](PROYECTO_COMPLETADO.md) - Guía de inicio
- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Configuración de GitHub

---

## 🧪 Testing

```bash
# Ejecutar script de verificación
python verify_mvp.py
```

Verifica:
- ✅ Creación de procesos
- ✅ Validación de campos
- ✅ Filtros funcionales
- ✅ Auditoría de cambios
- ✅ Control de permisos
- ✅ Performance

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

---

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@TU_USUARIO](https://github.com/TU_USUARIO)

---

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Google Gemini](https://ai.google.dev/) - Inteligencia Artificial
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM

---

## 📞 Soporte

¿Tienes preguntas? Abre un [issue](https://github.com/TU_USUARIO/ChechyLegis/issues)

---

**Desarrollado con ❤️ usando FastAPI + Gemini AI**
