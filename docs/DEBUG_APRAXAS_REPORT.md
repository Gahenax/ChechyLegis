# 🔬 ANTIGRAVITY/APRAXAS DEBUG REPORT
**Protocol:** APRAXAS/G1/G2 (Architecture → Refactor → Hardening)  
**Date:** 2026-02-04  
**Commit:** 7cb86824e9e37bb41099ef0dccf968bcad15ad34  
**Branch:** fix/apraxas-layout-cohesion  
**Total Files:** 1671  

---

## PHASE 0 — BASELINE INTAKE ✅

### Git Status
```
On branch: fix/apraxas-layout-cohesion (NUEVO)
Parent commit: 7cb86824e9e37bb41099ef0dccf968bcad15ad34
Modified files: 4
- static/api/client.js
- static/index.html
- static/styles/chechylegis-theme.css
- static/ui/render.js

Untracked docs: 8 (reportes ya generados)
```

### Architecture Discovery

**Entrypoint:** `static/app.js` (SPA Orchestrator)

```javascript
App.init() → 
  ├─ GahenaxRender.init('content')
  ├─ GahenaxStore.subscribe()
  └─ setupNavigation()
```

**Key Components:**
- **Orchestrator:** `app.js` - Maneja navegación y eventos
- **Renderer:** `ui/render.js` - Controla TODA la UI
- **Store:** `state/store.js` - Estado global
- **API:** `api/client.js` - Backend communication

**Discovery:** Es una **SPA pura** donde `render.js` tiene **AUTORIDAD TOTAL** sobre el DOM.

---

## PHASE 1 — STATE AUDIT 🔍

### P0 - BLOQUEADORES CRÍTICOS

#### **P0.1: CONFLICTO DE RENDER AUTHORITY** 🔴

**Root Cause:**  
`index.html` contiene markup HTML estático del sidebar/header, pero `render.js` **SOBRESCRIBE** todo mediante `this.appContent.innerHTML`.

**Evidence:**
```javascript
// ui/render.js línea 99, 149, 184, 231, 284, 353, 439
this.appContent.innerHTML = html;  // ← REEMPLAZA TODO EL CONTENIDO
```

**Locations Where DOM is Overwritten:**
1. `showExpedientesList()` - línea 99
2. `showExpedienteDetail()` - línea 149
3. `showAnalysisReport()` - línea 184
4. `showExpedienteForm()` - línea 231
5. `showSettingsArchive()` - línea 284
6. `showSupportDesk()` - línea 353
7. `renderError()` - línea 439

**Impact:**  
- ❌ Cualquier cambio en `index.html` al sidebar/header se **IGNORA**
- ❌ Enlaces agregados en HTML no aparecen
- ❌ El link "ECOSISTEMA" está en HTML pero el JS lo ignora

**Ranking:** **P0** - Bloquea funcionalidad principal

---

#### **P0.2: NO HAY SINGLE SOURCE OF TRUTH PARA NAVEGACIÓN** 🔴

**Root Cause:**  
Los enlaces del sidebar están **hardcodeados** en `index.html` sin representación en JavaScript.

**Evidence:**
```html
<!-- index.html líneas 44-65 -->
<li><a href="#" id="nav-list">EXPEDIENTES</a></li>
<li><a href="#" id="nav-create">RADICACIÓN</a></li>
<li><a href="#" id="nav-support">SOPORTE CRM</a></li>
<li><a href="#" id="nav-settings">ARCHIVO CENTRAL</a></li>
<li><a href="https://gahenaxaisolutions.com" id="nav-ecosystem">ECOSISTEMA</a></li>
```

Pero en `app.js` líneas 24-27:
```javascript
document.getElementById('nav-list').onclick = () => this.navigate('list');
document.getElementById('nav-create').onclick = () => this.navigate('form');
document.getElementById('nav-support').onclick = () => this.navigate('support');
document.getElementById('nav-settings').onclick = () => this.navigate('settings');
// ❌ NO HAY HANDLER PARA 'nav-ecosystem'
```

**Impact:**
- ❌ No hay data structure para los links
- ❌ Agregar nuevo link requiere tocar 3 archivos (HTML + app.js + render.js)
- ❌ El link ECOSISTEMA no tiene event listener

**Ranking:** **P0** - Rompe coherencia arquitectónica

---

### P1 - ROMPE DETERMINISMO

#### **P1.1: HEADER/SIDEBAR NO SE RENDERIZAN PROGRAMÁTICAMENTE** 🟡

**Root Cause:**  
El header y sidebar están **fijos en index.html** y nunca se regeneran dinámicamente.

**Evidence:**
```javascript
// render.js NO tiene métodos:
// renderHeader() ❌
// renderSidebar() ❌
// renderLayout() solo cambia #content ❌
```

**Current Architecture:**
```
index.html (shell estático)
  └─ #content ← render.js SOLO controla esto
  └─ .lex-header ← NUNCA CAMBIA (estático)
  └─ .lex-sidebar ← NUNCA CAMBIA (estático)
```

**Impact:**
- ⚠️ No se puede modificar header/sidebar sin tocar HTML
- ⚠️ No se pueden agregar elementos dinámicos al header
- ⚠️ Dificulta testing y componenti

zación

**Ranking:** **P1** - Impide evolución del sistema

---

#### **P1.2: INYECCIÓN DE SCRIPT NO ES IDEMPOTENTE** 🟡

**Root Cause:**  
Hay un script en `index.html` (líneas 171-192) que busca un elemento que **no existe**.

**Evidence:**
```javascript
// index.html línea 175
const banner = document.getElementById('ecosystem-banner');
// ❌ Este elemento NO EXISTE en el HTML
```

**Impact:**
- ⚠️ Console error silencioso
- ⚠️ Script inútil consumiendo recursos
- ⚠️ Código muerto que confunde

**Ranking:** **P1** - Code smell severo

---

### P2 - CALIDAD/MANTENIBILIDAD

#### **P2.1: DUPLICACIÓN DE ESTILOS INLINE** 🟢

**Evidence:**
```html
<!-- index.html tiene estilos inline masivos -->
style="text-decoration:none; color:inherit; display:flex; align-items:center..."
```

**Impact:**
- Dificulta theme consistency
- Violates DRY principle

**Ranking:** **P2** - Deuda técnica

---

#### **P2.2: NO HAY VERIFICACIÓN DETERMINÍSTICA** 🟢

**Root Cause:**  
No hay tests o checks automáticos.

**Impact:**
- Cambios se verifican manualmente
- Propenso a regresiones

**Ranking:** **P2** - Falta de QA

---

## SUMMARY OF FINDINGS

### P0 Issues (MUST FIX):
1. ✅ P0.1: Render Authority Conflict
2. ✅ P0.2: No Single Source for Navigation

### P1 Issues (SHOULD FIX):
1. ✅ P1.1: No Dynamic Header/Sidebar Rendering
2. ✅ P1.2: Dead Script Code

### P2 Issues (NICE TO HAVE):
1. P2.1: Inline Style Duplication
2. P2.2: No Automated QA

**Total Critical Issues:** 4  
**Blocking Production:** 2 (P0.1, P0.2)

---

## NEXT STEPS → PHASE 2

**Strategy:** Minimal Invasive Refactor

**Approach:**
1. **Create Layout Renderer** - Single authority for header/sidebar
2. **Convert HTML to Pure Shell** - Remove all feature markup
3. **Create Navigation Data Structure** - SIDEBAR_LINKS array
4. **Implement Idempotent Rendering** - Use data-id + replaceChildren

**Expected Outcome:**
- ✅ ECOSISTEMA link appears deterministically
- ✅ Single source of truth for UI
- ✅ Testable, deterministic rendering

---

**Report Generated:** 2026-02-04  
**Status:** AUDIT COMPLETE → READY FOR PHASE 2
