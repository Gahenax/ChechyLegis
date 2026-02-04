# GAHENAX CONTRACT LOCK (PHASE 0)

## 1. PUBLIC API ROUTES
LOCKED for Version 1.0.0 (GAHENAX-GOLD).
Any change requires bumping version and recertification.

### Core (Procesos)
- GET /api/procesos - List with filters
- POST /api/procesos - Create new process
- GET /api/procesos/{id} - Get details + history
- PUT /api/procesos/{id} - Update fields
- DELETE /api/procesos/{id} - Soft delete

### AI Engine (Gemini)
- POST /api/ai/search - Semantic search
- GET /api/ai/analyze/{id} - Case analysis
- GET /api/ai/similar/{id} - Similar cases
- POST /api/ai/chat - RAG Chat

### System
- GET /api/health - Status check
- GET /api/storage/* - File access (sandboxed)

---

## 2. DATABASE SCHEMA SIGNATURE
Engine: SQLite (Strict Strict Tables where possible, but using SQLAlchemy).

### Tables
1. **Model: Proceso**
   - PK: id (Integer)
   - Unique: numero_proceso (String)
   - Fields: fecha_radicacion, estado (Enum), partes, observaciones, deleted_at

2. **Model: AuditLog**
   - PK: id
   - Immutable: usuario, accion, entidad, entidad_id, valor_anterior, valor_nuevo, timestamp

3. **Model: Document**
   - PK: id
   - Identity: sha256 (colisión imposible en uso normal)
   - Store: storage/ hashed filenames

4. **Model: FileRecord**
   - PK: id
   - Sandbox metadata for general file storage.

---

## 3. FILESYSTEM LAYOUT (SANDBOX)
Root: `./storage`
- No traversal allowed (`..` blocked).
- Files stored by hash or unique ID to prevent overwrites.

---

## 4. AUDIT COMPLIANCE
Rule: "No mutation without representation"
- Every INSERT/UPDATE/DELETE on `procesos` MUST trigger an AuditLog entry within the same transaction.
- Middleware `AuditMiddleware` captures request context.

---

## 5. LICENSE MODE: FREE
- No cloud dependencies other than Gemini API.
- Local SQLite.
- No user accounts (Single tenant / Role simulation).
- Unlimited local records (constrained by disk).
