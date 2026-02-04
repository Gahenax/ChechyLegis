# 🗺️ ROADMAP: REFACTORIZACIÓN ESTRUCTURAL GAHENAX
**Proyecto**: ChechyLegis (v1.1.0-REF)
**Autoría**: Antigravity (IA) en colaboración con Jules (Background Worker)

Este documento detalla los pasos técnicos para elevar la arquitectura del sistema antes de su distribución final en la nube de Hostinger.

---

## 🛠️ Fase 1: Backend - Modularización y Estándares
**Objetivo**: Eliminar la saturación de `main.py` y centralizar la lógica de negocio.
1.  **Rutas Modulares**: Separar los endpoints en `/routers/`:
    *   `procesos.py`: CRUD y lógica de expedientes.
    *   `ai_engine.py`: Búsquedas semánticas y análisis de Gemini.
    *   `storage.py`: Gestión de archivos y sandbox.
2.  **Núcleo de Configuración**: Crear `core/config.py` para manejar:
    *   Validación de API Keys.
    *   Control estricto de `LICENSE_MODE` (FREE/PRO).
    *   Límites de hardware y almacenamiento.
3.  **Middleware de Auditoría**: Refinar la "Caja Negra" para que sea un middleware de FastAPI, capturando cambios de forma automática sin ensuciar el `crud.py`.

## 🎨 Fase 2: Frontend - Clean UI & Hub Integration
**Objetivo**: Mejorar el rendimiento de la interfaz y unificar la marca Gahenax.
1.  **Refactor de `app.js`**: Separar las funciones de Renderizado de las funciones de Llamada a API.
2.  **Gahenax Branding**: Inyectar el nuevo sistema de diseño (Glassmorphism + Indigo Glow) en todas las vistas internas.
3.  **Hub Direct Access**: Integrar un acceso directo al `gahenax_hub.html` (Centro de Descargas) desde los ajustes.

## 🤖 Fase 3: Delegación a Jules (Background Tasks)
**Objetivo**: Usar a Jules para tareas que bloquean el hilo principal.
1.  **Worker Tasks**: Crear definiciones de tareas en `json` para que Jules ejecute:
    *   `task_build_release`: Limpieza y empaquetado del ZIP.
    *   `task_security_audit`: Escaneo de vulnerabilidades en dependencias.
2.  **Lifecycle Monitoring**: Implementar un sistema de notificaciones en la UI para ver el estado de Jules.

## 🏁 Fase 4: Auditoría y Despliegue (Gahenax Force)
**Objetivo**: Certificación final y subida a Hostinger.
1.  **Prueba de Estrés FREE**: Validar que los límites (3 procesos) sean infranqueables a nivel de base de datos.
2.  **Documentación**: Generar `TECNOLOGIAS_GAHENAX.md` para el Hub.
3.  **Push de Sincronización**: Envío final a GitHub con el tag `GAHENAX-GOLD`.

---

### ⚠️ Riesgos Residuales
- Compatibilidad de rutas relativas al mover archivos a `/routers`.
- Pérdida momentánea de persistencia durante la migración de la DB (se hará backup previo).

**¿Aprobado para ejecución?**
> "El código es ley, pero la arquitectura es su justicia."
