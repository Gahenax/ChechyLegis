# SECURITY BASELINE - CHECHYLEGIS (GAHENAX-GOLD)

Based on OWASP ASVS and Certification Gates.

## 1. AUTHENTICATION & ACCESS CONTROL
- **Role Model**: Simulation (Viewer/Operator/Admin).
- **Enforcement**: Middleware `RoleMiddleware` checks required scopes.
- **Limitation**: In this version (Phase 0), security depends on network/device security. No password login is implemented within the app.
- **Recommendation**: Deploy behind an authenticated reverse proxy (e.g., Cloudflare Access, Nginx Basic Auth) for any shared network access.

## 2. INPUT VALIDATION & DATA INTEGRITY
- **Validation**: Strict Pydantic V2 schemas for all API inputs.
- **Fail-Safe**: Rejects malformed JSON, dates, or enums with 422 Unprocessable Entity.
- **Mutation Control**: Only documented models (`Proceso`, `Document`) are mutable.
- **Soft Deletes**: Deletions are logical (`deleted=true`), preventing accidental data loss via API.

## 3. SECURE CONFIGURATION
- **Secrets Management**: `.env` file for `GEMINI_API_KEY` and `DATABASE_URL`.
- **Exclusion**: `.env` is gitignored.
- **Docker**: Runs as non-root user (implied best practice for containerization).
- **Default Port**: 8000 (standard dev port, easily changed via ENV).

## 4. AUDIT LOGGING
- **Requirement**: "No mutation without representation."
- **Implementation**: Every create/update/delete operation is logged to the `AuditLog` table.
- **Content**: Timestamp, Action, Old Value, New Value, User Role.
- **Tampering**: Logs are immutable via API (read-only endpoints).

## 5. FILE SANDBOX
- **Storage Root**: `./storage` (configurable via `FILES_ROOT`).
- **Traversal Protection**: Filenames are hashed/sanitized. `..` paths are blocked.
- **Type Restrictions**: Only allowed MIME types processed.

## 6. AI SAFETY (LLM)
- **Prompt Injection**: Basic system prompt constraints.
- **Data Privacy**: No sensitive PII (Personally Identifiable Information) beyond case details is sent to Google.
- **User Warning**: Explicit disclaimers on AI-generated content.

## 7. KNOWN GAPS (ACCEPTABLE RISKS)
- **Risk**: No CSRF protection (stateless API, no session cookies).
- **Mitigation**: Local usage context.
- **Risk**: Rate Limiting absent.
- **Mitigation**: Single-tenant usage pattern.
- **Risk**: SQLite concurrency locking.
- **Mitigation**: Low user count target.
