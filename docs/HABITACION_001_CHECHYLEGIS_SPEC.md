# ============================================================
# ANTIGRAVITY — INSTRUCCIÓN DE INTEGRACIÓN (HABITACIÓN 001)
# ============================================================

## INTEGRATE FIRST ROOM: CHECHYLEGIS

### Scope:
- Integrate ChechyLegis as the FIRST and ONLY active room in the Hotel system.
- Do NOT add or enable any other rooms yet.
- Use ChechyLegis to validate the entire Hotel architecture:
  auth, keys, access control, logging, and UI door states.

### Room Definition (CANON):

```json
{
  "slug": "chechylegis",
  "name": "ChechyLegis",
  "floor": 4,
  "type": "web_room",
  "tagline": "Norma, jurisprudencia y prueba convertidas en decisión.",
  "description_short": "Sistema jurídico-operativo para análisis penal estructurado y decisiones defendibles.",
  "description_long": "Habitación legal del Hotel Gahenax que aplica un método por capas — norma, jurisprudencia, prueba, riesgo y decisión — permitiendo simular providencias, estructurar argumentos y registrar el razonamiento de forma auditada.",
  "tags": ["Legal", "Penal", "Decisión", "Colombia"],
  "requirements": [
    "Cuenta activa",
    "Rol customer o superior",
    "Llave Pro o Max"
  ],
  "services": [
    "Análisis normativo (CP / CPP)",
    "Jurisprudencia CSJ y Corte Constitucional",
    "Evaluación probatoria",
    "Simulación de providencias",
    "Registro lógico del razonamiento",
    "Historial auditado de decisiones"
  ],
  "access_policy": {
    "allowed_plans": ["pro", "max"],
    "min_role": "customer"
  },
  "status": "active"
}
```

### Rules:

1. **Seed ONLY this room** in the database / manifest.
2. **Enforce access via valid RoomKey** (Pro or Max).
3. **Block access for:**
   - Unauthenticated users
   - Authenticated users without key
   - Expired or revoked keys
4. **Log ALL access attempts** (allowed and denied) with clear reason.
5. **UI must show ChechyLegis** in the Hotel map as the only available room.
6. **Do NOT scaffold, stub, or reference** any other rooms.

### Verification (MANDATORY):

| Test Case | Expected Result |
|-----------|----------------|
| Access without login | ❌ denied + log |
| Login without key | ❌ denied + log |
| Login with expired key | ❌ denied + log |
| Login with valid key | ✅ access granted + room_entered event logged |

### Integration Points with Existing ChechyLegis:

#### Current ChechyLegis Location:
```
c:\Users\USUARIO\OneDrive\Desktop\Legischechy\
```

#### Current ChechyLegis Architecture:
- **Backend**: Python + FastAPI (NOT Flask as assumed)
- **Frontend**: Vanilla JavaScript SPA (NOT React)
- **Database**: SQLite (`judicial_archive.db`)
- **AI**: Google Gemini 1.5 Flash
- **Port**: 8000 (Uvicorn)

#### Integration Strategy:

**Option A: Wrap Existing ChechyLegis**
- Create Hotel wrapper around existing app
- Existing app runs as-is at `/chechylegis/*`
- Hotel handles auth/keys at gateway level
- Minimal changes to ChechyLegis code

**Option B: Deep Integration**
- Add Hotel tables to existing SQLite DB
- Modify ChechyLegis auth to use Hotel system
- Full integration of access control
- More invasive but cleaner

**RECOMMENDED: Option A** (Minimal invasiveness, faster validation)

### Architecture Adjustments Needed:

Based on actual ChechyLegis stack, update assumptions:

```json
{
  "backend_framework": "FastAPI",  // NOT Flask
  "frontend": "Vanilla",           // NOT React
  "db": "SQLite",                  // Confirmed
  "existing_app_path": "/chechylegis",
  "hotel_gateway_path": "/api/hotel"
}
```

### End Condition:

✅ ChechyLegis is fully accessible ONLY with a valid key  
✅ All access checks pass  
✅ Audit logs show all attempts with reasons  
✅ UI shows room door with correct state (locked/unlocked)  
✅ No other rooms visible or accessible  

---

## ⚠️ CRITICAL: DO NOT IMPLEMENT YET

This is a **SPECIFICATION DOCUMENT** only.

**Next steps:**
1. ✅ Review and approve this spec
2. ⏳ Adjust prompt generator for ChechyLegis-only mode
3. ⏳ Generate updated implementation prompt
4. ⏳ Execute implementation with QA

---

**Created**: 2026-02-04T18:53:02Z  
**Status**: SPECIFICATION (NOT IMPLEMENTED)  
**Author**: José de Ávila / Antigravity AI
