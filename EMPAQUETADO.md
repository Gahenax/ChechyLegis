# 📦 Guía de Empaquetado - ChechyLegis

## 🎯 Objetivo
Esta guía explica cómo crear un instalador profesional de **ChechyLegis** para distribuir a usuarios finales.

---

## 📋 Requisitos Previos

### Software Necesario

1. **Python 3.8+** (ya instalado)
   - Verificar: `python --version`

2. **PyInstaller** (se instala automáticamente)
   - Para instalación manual: `pip install pyinstaller`

3. **Inno Setup 6** (para crear el instalador)
   - Descargar: https://jrsoftware.org/isdl.php
   - Instalar en la ubicación por defecto

---

## 🚀 Proceso de Empaquetado

### Opción 1: Build Completo Automático (RECOMENDADO)

```bash
# Ejecutar el script maestro
build_all.bat
```

Este script realiza:
1. ✅ Construcción del ejecutable con PyInstaller
2. ✅ Creación del instalador con Inno Setup
3. ✅ Verificación de todos los archivos

### Opción 2: Paso a Paso Manual

#### Paso 1: Construir Ejecutable
```bash
build_exe.bat
```

**Resultado**: `dist/ChechyLegis/ChechyLegis.exe`

#### Paso 2: Crear Instalador
```bash
build_installer.bat
```

**Resultado**: `installers/ChechyLegis_Setup_v1.0.0.exe`

---

## 📁 Archivos de Configuración

### `ChechyLegis.spec`
Configuración de PyInstaller:
- Define qué archivos incluir
- Configura módulos ocultos
- Establece icono y nombre del ejecutable
- Excluye módulos innecesarios

### `installer.iss`
Script de Inno Setup:
- Define el proceso de instalación
- Crea accesos directos
- Configura desinstalación inteligente
- Preserva datos del usuario

### `build_config.py`
Configuración centralizada:
- Versión de la aplicación
- Información del autor
- Parámetros de compilación

---

## 🔧 Personalización

### Cambiar Versión

Editar `build_config.py`:
```python
APP_VERSION = "1.0.1"  # Nueva versión
```

### Cambiar Icono

Reemplazar `icon.ico` con tu propio icono (formato .ico)

### Modificar Información del Instalador

Editar `installer.iss`:
```ini
#define MyAppPublisher "Tu Nombre"
#define MyAppURL "https://tu-sitio.com"
```

---

## 📦 Estructura del Ejecutable

```
dist/ChechyLegis/
├── ChechyLegis.exe          # Ejecutable principal
├── _internal/               # Dependencias empaquetadas
│   ├── Python DLLs
│   ├── Librerías
│   └── Módulos
├── static/                  # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── app/                     # Backend
│   ├── main.py
│   ├── models.py
│   └── ...
├── .env.example             # Plantilla de configuración
├── icon.ico                 # Icono
└── README.md                # Documentación
```

---

## 🎨 Características del Instalador

### Durante la Instalación
- ✅ Instalación en `C:\Program Files\ChechyLegis`
- ✅ Creación de accesos directos
- ✅ Opción de icono en escritorio
- ✅ Copia automática de `.env.example` a `.env`
- ✅ Configuración de permisos

### Durante la Desinstalación
- ✅ Pregunta si conservar la base de datos
- ✅ Pregunta si conservar la configuración (.env)
- ✅ Limpieza de archivos temporales
- ✅ Eliminación de accesos directos

---

## ⚙️ Configuración Post-Instalación

Después de instalar, el usuario debe:

1. **Configurar API Key de Gemini**
   - Abrir `C:\Program Files\ChechyLegis\.env`
   - Agregar: `GEMINI_API_KEY=tu_api_key_aqui`

2. **Ejecutar la aplicación**
   - Doble click en el icono del escritorio
   - O desde el menú de inicio

3. **Acceder al sistema**
   - Abrir navegador en: `http://127.0.0.1:8000`

---

## 🐛 Solución de Problemas

### Error: "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### Error: "Inno Setup no encontrado"
- Descargar e instalar desde: https://jrsoftware.org/isdl.php
- Reintentar la construcción

### Error: "Módulo no encontrado" al ejecutar
- Agregar el módulo a `hidden_imports` en `ChechyLegis.spec`
- Reconstruir el ejecutable

### El ejecutable es muy grande
- Normal, incluye Python completo (~50-100 MB)
- Para reducir tamaño, revisar `excludes` en `.spec`

---

## 📊 Tamaños Esperados

- **Ejecutable empaquetado**: ~80-120 MB
- **Instalador comprimido**: ~40-60 MB
- **Instalación completa**: ~150-200 MB

---

## 🔐 Seguridad

### Archivos NO Incluidos en el Instalador
- ❌ `.env` (configuración local)
- ❌ `judicial_archive.db` (base de datos)
- ❌ `__pycache__` (archivos compilados)
- ❌ `.git` (repositorio Git)

### Archivos SÍ Incluidos
- ✅ `.env.example` (plantilla)
- ✅ Código fuente de la aplicación
- ✅ Frontend (HTML/CSS/JS)
- ✅ Documentación

---

## 🚀 Distribución

### Subir a GitHub Releases

1. Crear release en GitHub
2. Subir `ChechyLegis_Setup_v1.0.0.exe`
3. Agregar notas de versión

### Compartir Directamente

El instalador es un archivo único `.exe` que se puede:
- Enviar por email
- Subir a Google Drive / Dropbox
- Compartir en red local
- Distribuir en USB

---

## 📝 Checklist de Pre-Release

Antes de distribuir, verificar:

- [ ] Versión actualizada en `build_config.py`
- [ ] README.md actualizado
- [ ] LICENSE.txt incluido
- [ ] `.env.example` con todas las variables
- [ ] Iconos correctos (icon.ico, icon.png)
- [ ] Prueba de instalación en máquina limpia
- [ ] Prueba de desinstalación
- [ ] Verificación de funcionalidades principales
- [ ] Documentación de usuario completa

---

## 🎯 Comandos Rápidos

```bash
# Build completo
build_all.bat

# Solo ejecutable
build_exe.bat

# Solo instalador (requiere ejecutable previo)
build_installer.bat

# Limpiar builds anteriores
rmdir /s /q build dist
```

---

## 📞 Soporte

Para problemas durante el empaquetado:
1. Revisar logs en `build/`
2. Verificar `ChechyLegis.spec`
3. Consultar documentación de PyInstaller
4. Revisar issues de Inno Setup

---

## 🎉 Resultado Final

Después de ejecutar `build_all.bat`, tendrás:

```
✅ dist/ChechyLegis/ChechyLegis.exe
   - Ejecutable portable (puede ejecutarse sin instalar)

✅ installers/ChechyLegis_Setup_v1.0.0.exe
   - Instalador profesional de Windows
   - Listo para distribuir
```

---

**¡Listo para empaquetar y distribuir ChechyLegis! 🚀**
