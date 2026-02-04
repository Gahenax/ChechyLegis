# AUDIT READINESS GUIDE (Phase 5)

This document is for external auditors reviewing the GAHENAX-GOLD release of ChechyLegis.

## 1. ARCHITECTURE OVERVIEW
- **Type**: Single Page Application (SPA) served by FastAPI.
- **Data**: Local SQLite + Local Filesystem.
- **AI**: Gateway to Google Gemini API (stateless).

## 2. THREAT MODEL SUMMARY
- **Primary Asset**: Case files (`storage/`) and metadata (`judicial_archive.db`).
- **Primary Threat**: Unauthorized local network access (due to lack of password auth).
- **Secondary Threat**: SQL Injection (mitigated by SQLAlchemy).
- **Secondary Threat**: XSS (mitigated by modern frameworks, though needs checking).
- **Accepted Risk**: No authentication layer (Role Simulation only).

## 3. HOW TO AUDIT
1. **Source Code**: Review `app/` directory (Python) and `static/` (JS).
2. **Configuration**: Check `.env.example` vs `.env` handling.
3. **Database**: Inspect `judicial_archive.db` schema using `sqlite3`.
4. **Logs**: Verify `AuditLog` table entries match actions performed.

## 4. SECURITY CONTROLS MAP
| Control | Implementation | File |
|---------|----------------|------|
| Input Validation | Pydantic V2 | `app/schemas.py` |
| Output Encoding | Standard JSON | `app/main.py` |
| Access Control | RoleMiddleware | `app/main.py` |
| Audit Trail | AuditMiddleware | `app/crud.py` |
| Sandboxing | Hash Filenames | `app/main.py` |

## 5. TEST ACCOUNTS (SIMULATION)
- **Admin**: Full access.
- **Operator**: Can create/edit, cannot delete.
- **Viewer**: Read-only.
- **Switching**: Use UI dropdown (top right).

## 6. DATA HANDLING STATEMENT
- No user data is sent to Antigravity or third parties other than Google (for AI inference).
- Google Gemini API data retention policy applies.
