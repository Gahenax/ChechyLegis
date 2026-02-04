# CHANGELOG - CHECHYLEGIS (GAHENAX-GOLD)

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - GAHENAX-GOLD - 2026-02-03
### Added
- **AI Analysis**: Google Gemini 1.5/2.0 search, summary, and analysis features.
- **Audit System**: Full database-level audit log for all mutations.
- **Role Simulation**: Viewer/Operator/Admin roles for local multi-user scenarios.
- **Soft Deletes**: Safety mechanism for process removal.
- **Documentation**: Comprehensive `CONTRACT.md` and `REPORTE_PROYECTO.md`.

### Changed
- **Backend**: Migrated to Pydantic V2 (`from_attributes=True`).
- **Dependencies**: Replaced `google-generativeai` with `google-genai` (v1.61.0).
- **Frontend**: Glassmorphism UI/UX with responsive design.
- **Build System**: Reproducible build process (Docker & PyInstaller).
- **File Structure**: Centralized `storage/` directory with sandboxing.
- **Configuration**: Standardized via `.env`.

### Fixed
- Deprecation warnings from Pydantic V1/V2 transition.
- Deprecation warnings from Google GenAI legacy SDK.
- SPA routing issue (404 on `/settings` or refresh) handled via backend catch-all or hash routing.

### Security
- Added `RoleMiddleware` for access control.
- Added `AuditMiddleware` for accountability.
- Enforced `FILES_ROOT` sandboxing to prevent path traversal.
