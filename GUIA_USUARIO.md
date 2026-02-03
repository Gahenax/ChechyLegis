# 📦 ChechyLegis - Guía de Usuario del Instalador

## 🎯 Bienvenido a ChechyLegis

**ChechyLegis** es un sistema profesional de gestión de procesos judiciales con capacidades avanzadas de Inteligencia Artificial.

---

## 🚀 Instalación Rápida

1. **Ejecutar el instalador**
   - Doble click en `ChechyLegis_Setup_v1.0.0.exe`
   - Seguir el asistente de instalación

2. **Configurar API Key de Gemini** (GRATIS)
   - Obtener API Key: https://aistudio.google.com/app/apikey
   - Abrir: `C:\Program Files\ChechyLegis\.env`
   - Agregar: `GEMINI_API_KEY=tu_api_key_aqui`

3. **Ejecutar ChechyLegis**
   - Desde el icono del escritorio
   - O desde el menú de inicio

4. **Acceder al sistema**
   - Abrir navegador en: http://127.0.0.1:8000

---

## ✨ Características Principales

### Gestión de Procesos
- ✅ Crear, editar y eliminar procesos judiciales
- ✅ Filtros avanzados por fecha, estado, número
- ✅ Historial completo de auditoría
- ✅ Control de acceso por roles

### Inteligencia Artificial 🤖
- ✅ **Búsqueda en Lenguaje Natural**: "procesos activos de enero"
- ✅ **Análisis Automático**: Insights y recomendaciones
- ✅ **Casos Similares**: Encuentra procesos relacionados
- ✅ **Asistente Virtual**: Responde tus preguntas

---

## 🎮 Uso Básico

### Crear un Proceso
1. Click en "Nuevo Proceso"
2. Completar el formulario
3. Guardar

### Buscar con IA
1. Escribir en lenguaje natural: "procesos de María García"
2. La IA encontrará los procesos relevantes

### Analizar un Proceso
1. Abrir un proceso
2. Click en "🤖 Analizar"
3. Ver insights y recomendaciones

### Cambiar Rol de Usuario
1. Selector en esquina superior derecha
2. Elegir: Viewer, Operator o Admin

---

## 🔐 Roles y Permisos

| Rol | Ver | Crear | Editar | Eliminar |
|-----|-----|-------|--------|----------|
| **Viewer** | ✅ | ❌ | ❌ | ❌ |
| **Operator** | ✅ | ✅ | ✅ | ❌ |
| **Admin** | ✅ | ✅ | ✅ | ✅ |

---

## ⚙️ Configuración

### Archivo .env
Ubicación: `C:\Program Files\ChechyLegis\.env`

```env
# API Key de Google Gemini (OBLIGATORIO para IA)
GEMINI_API_KEY=tu_api_key_aqui

# Base de datos (NO MODIFICAR)
DATABASE_URL=sqlite:///./judicial_archive.db
```

### Obtener API Key de Gemini
1. Ir a: https://aistudio.google.com/app/apikey
2. Iniciar sesión con cuenta Google
3. Click en "Create API Key"
4. Copiar la key generada
5. Pegarla en el archivo `.env`

---

## 🐛 Solución de Problemas

### La aplicación no inicia
**Solución**: 
- Verificar que el puerto 8000 no esté en uso
- Cerrar otras aplicaciones que usen el puerto
- Reiniciar ChechyLegis

### "Servicio de IA no disponible"
**Solución**:
- Verificar que la API Key esté configurada en `.env`
- Verificar conexión a Internet
- Verificar que la API Key sea válida

### Error al crear proceso
**Solución**:
- Verificar que todos los campos obligatorios estén completos
- Verificar que el número de proceso sea único
- Cambiar rol a Operator o Admin

### No puedo editar procesos
**Solución**:
- Cambiar rol a Operator o Admin
- Viewer solo puede ver procesos

---

## 📊 Base de Datos

### Ubicación
`C:\Program Files\ChechyLegis\judicial_archive.db`

### Respaldo
Para hacer backup:
1. Cerrar ChechyLegis
2. Copiar `judicial_archive.db` a ubicación segura
3. Reiniciar ChechyLegis

### Restauración
Para restaurar backup:
1. Cerrar ChechyLegis
2. Reemplazar `judicial_archive.db` con el backup
3. Reiniciar ChechyLegis

---

## 🔄 Actualización

### Instalar Nueva Versión
1. Descargar nuevo instalador
2. Ejecutar instalador (sobrescribirá archivos)
3. **La base de datos y configuración se preservan**

---

## 🗑️ Desinstalación

### Proceso
1. Panel de Control → Programas → Desinstalar
2. Buscar "ChechyLegis"
3. Click en "Desinstalar"

### Datos Preservados
Durante la desinstalación se preguntará:
- ¿Conservar base de datos? (judicial_archive.db)
- ¿Conservar configuración? (.env)

---

## 📞 Soporte

### Documentación
- README completo en: `C:\Program Files\ChechyLegis\README.md`
- Guía de empaquetado: `EMPAQUETADO.md`

### Recursos Online
- GitHub: https://github.com/yourusername/ChechyLegis
- Documentación Gemini: https://ai.google.dev/docs
- Documentación FastAPI: https://fastapi.tiangolo.com/

---

## 📋 Requisitos del Sistema

- **Sistema Operativo**: Windows 10 o superior (64 bits)
- **Espacio en Disco**: 500 MB libres
- **RAM**: 2 GB mínimo (4 GB recomendado)
- **Internet**: Requerido para funciones de IA
- **Navegador**: Chrome, Firefox, Edge (versiones recientes)

---

## 🎉 ¡Listo para Usar!

ChechyLegis está instalado y listo para gestionar tus procesos judiciales con el poder de la Inteligencia Artificial.

**¡Disfruta de ChechyLegis! 🚀**

---

*Versión 1.0.0 - 2026*
