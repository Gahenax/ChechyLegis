#!/usr/bin/env python3
"""
ANTIGRAVITY PROMPT MASTER (Python) — GAHENAX HOTEL SYSTEM
Goal: Generate a single, deterministic, copy-paste prompt for Antigravity to
implement the "Hotel" structure (Lobby + Rooms + Keys + FrontDesk) in the CRM/web stack.

Usage:
  python antigravity_prompt_hotel.py > PROMPT_ANTIGRAVITY_HOTEL.txt

Notes:
- This script does NOT implement the system. It outputs a precise build prompt.
- Edit ASSUMPTIONS if your stack differs (Flask/FastAPI, React/Vite, etc).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import textwrap


# =========================
# ASSUMPTIONS (EDIT IF NEEDED)
# =========================
ASSUMPTIONS = {
    "backend_framework": "Flask",      # "Flask" or "FastAPI"
    "db": "SQLite",                    # "SQLite" first; must be Postgres-compatible later
    "orm": "SQLAlchemy",               # "SQLAlchemy" or "raw_sql"
    "storage": "Cloudflare R2",        # "Cloudflare R2" or "S3-compatible" or "Hostinger local"
    "frontend": "React",               # "React" or "Vanilla"
    "auth": "session+jwt",             # "session+jwt" or "jwt_only"
    "repo_scope_rule": "Work only on website + backend modules necessary for Hotel; do not touch unrelated modules.",
    "domain": "gahenaxaisolutions.com",
}

# =========================
# INITIAL HOTEL INVENTORY
# =========================
ROOMS_SEED = [
    {
        "slug": "gkx-promptkit",
        "name": "GKX (GAHENAX PromptKit)",
        "floor": 3,
        "type": "kit_room",
        "tagline": "Playbook de prompts ejecutables con QA determinista.",
        "tags": ["Prompts", "QA", "Producción"],
        "requirements": ["Python 3.10+"],
        "services": ["Plantillas", "Reglas fijas", "Checklist DoD", "QA determinista"],
        "status": "active",
    },
    {
        "slug": "judegx0-decision",
        "name": "JudeGX0 (Decision Filter)",
        "floor": 2,
        "type": "web_room",
        "tagline": "Filtro decisional: señal, acción, riesgo y descarte.",
        "tags": ["Decisión", "Operación"],
        "requirements": ["Cuenta activa"],
        "services": ["Elegibilidad", "Criterio", "Condición de descarte", "Logs"],
        "status": "active",
    },
    {
        "slug": "tiamat-forge",
        "name": "TIAMAT FORGE",
        "floor": 3,
        "type": "kit_room",
        "tagline": "Motor narrativo: tensión, costo y consecuencia.",
        "tags": ["Narrativa", "Creativo"],
        "requirements": ["Python 3.10+"],
        "services": ["Estructura narrativa", "QA de sentido", "Reglas anti-degradación"],
        "status": "active",
    },
    {
        "slug": "antigravity-playbook",
        "name": "Antigravity Playbook",
        "floor": 3,
        "type": "kit_room",
        "tagline": "Compilación y QA Gatekeeping para cambios con causalidad estricta.",
        "tags": ["QA", "Debug", "DevOps"],
        "requirements": ["Python 3.10+", "Acceso repo"],
        "services": ["Causalidad", "Parches mínimos", "Verificación determinista"],
        "status": "active",
    },
    {
        "slug": "chechy-penalista",
        "name": "Chechy (Penalista)",
        "floor": 4,
        "type": "web_room",
        "tagline": "Norma → jurisprudencia → prueba → riesgo → decisión.",
        "tags": ["Legal", "Penal", "Colombia"],
        "requirements": ["Cuenta activa", "Rol customer+"],
        "services": ["Simulación de providencias", "Análisis por capas", "Plantillas"],
        "status": "active",
    },
    {
        "slug": "archivo-judicial",
        "name": "Archivo Judicial Digital",
        "floor": 4,
        "type": "web_room",
        "tagline": "Organización por año, clase, cuantía y estado (terminado/suspendido/rechazado).",
        "tags": ["Legal", "Gestión", "Archivo"],
        "requirements": ["Cuenta activa"],
        "services": ["Clasificación", "Búsqueda", "Estados", "Reportes"],
        "status": "active",
    },
    {
        "slug": "atlas-modo-nitro",
        "name": "Atlas (Modo: Nitro)",
        "floor": 1,
        "type": "kit_room",
        "tagline": "Entrenador estructural de gym con progresión y adherencia.",
        "tags": ["Fitness", "Planificación"],
        "requirements": ["Python 3.10+"],
        "services": ["Rutinas", "Progresión", "Adherencia", "Seguimiento"],
        "status": "active",
    },
    {
        "slug": "varg-fin-ops",
        "name": "Varg (FIN-Market Ops)",
        "floor": 5,
        "type": "web_room",
        "tagline": "Lectura operativa de mercado + simulación de escenarios.",
        "tags": ["Finanzas", "Riesgo", "Simulación"],
        "requirements": ["Cuenta activa", "Rol customer+"],
        "services": ["Señal", "Riesgo", "Escenarios", "Percentiles"],
        "status": "active",
    },
]

# =========================
# PROMPT BUILDER
# =========================

@dataclass
class PromptSection:
    title: str
    body: str

def wrap(s: str) -> str:
    return textwrap.fill(s, width=92, replace_whitespace=False)

def codeblock(lang: str, content: str) -> str:
    return f"```{lang}\n{content.rstrip()}\n```"

def make_manifest_skeleton() -> dict:
    return {
        "hotel": {
            "domain": ASSUMPTIONS["domain"],
            "concept": "Hotel model: site=lobby, each app=room, access via keys, everything logged.",
        },
        "floors": [
            {"id": 1, "name": "Operación"},
            {"id": 2, "name": "Decisión"},
            {"id": 3, "name": "Producción"},
            {"id": 4, "name": "Legal"},
            {"id": 5, "name": "Mercado"},
        ],
        "plans": [
            {"id": "core", "name": "Core Stay"},
            {"id": "pro", "name": "Pro Stay"},
            {"id": "max", "name": "Max Stay"},
        ],
        "access_rules": {
            "roles": ["viewer", "customer", "operator", "admin"],
            "rule_1": "Public can view lobby/rooms but cannot enter/pickup without auth+valid key.",
            "rule_2": "Backend always authorizes. No public direct download links.",
            "rule_3": "All enter/pickup attempts are logged with allow/deny reasons.",
        },
        "ui_routes": [
            {"path": "/", "name": "Lobby"},
            {"path": "/hotel", "name": "Hotel Map"},
            {"path": "/hotel/:slug", "name": "Room Door"},
            {"path": "/reception", "name": "Guest Reception"},
            {"path": "/frontdesk", "name": "Admin FrontDesk"},
        ],
        "api_routes": [
            {"method": "GET", "path": "/api/hotel/rooms"},
            {"method": "GET", "path": "/api/hotel/rooms/{slug}"},
            {"method": "POST", "path": "/api/reception/checkin"},
            {"method": "GET", "path": "/api/reception/me"},
            {"method": "GET", "path": "/api/reception/keys/mine"},
            {"method": "POST", "path": "/api/hotel/rooms/{id}/enter"},
            {"method": "POST", "path": "/api/hotel/rooms/{id}/pickup"},
            {"method": "POST", "path": "/api/frontdesk/rooms"},
            {"method": "POST", "path": "/api/frontdesk/rooms/{id}/versions"},
            {"method": "POST", "path": "/api/frontdesk/keys/issue"},
            {"method": "POST", "path": "/api/frontdesk/keys/revoke"},
            {"method": "GET", "path": "/api/frontdesk/events"},
        ],
        "rooms_seed": ROOMS_SEED,
    }

def build_prompt() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    manifest = make_manifest_skeleton()
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)

    sections: list[PromptSection] = []

    sections.append(PromptSection(
        "ROLE",
        "\n".join([
            "You are ANTIGRAVITY — Build & QA Gatekeeper for the GAHENAX HOTEL SYSTEM.",
            "You will implement a hotel-structured catalog and access control layer on the website.",
        ])
    ))

    sections.append(PromptSection(
        "CONTEXT",
        "\n".join([
            f"Domain: {ASSUMPTIONS['domain']}",
            "Concept: Company is a hotel. Website is the lobby. Each web app/tool is a room or hotel area.",
            "Guests must check-in (auth), receive keys (licenses), and only then can enter rooms or pick up kits.",
            "Everything must be logged (audit trail).",
        ])
    ))

    sections.append(PromptSection(
        "NON-NEGOTIABLE RULES",
        "\n".join([
            "1) Minimal changes only. Do not touch unrelated modules.",
            "2) Strict causality order: schema/data model first → auth/RBAC → API → UI → storage/signed downloads → telemetry → QA.",
            "3) No speculative refactors. Identify exact insertion points and patch minimally.",
            "4) Every phase must include deterministic verification steps with evidence (commands + expected outputs).",
            "5) Backend is the source of truth for authorization. No public direct download URLs.",
            f"6) Repo scope: {ASSUMPTIONS['repo_scope_rule']}",
        ])
    ))

    sections.append(PromptSection(
        "ASSUMPTIONS (CHANGE ONLY IF TRUE)",
        codeblock("json", json.dumps(ASSUMPTIONS, indent=2))
    ))

    sections.append(PromptSection(
        "DELIVERABLES",
        "\n".join([
            "A) hotel_manifest.json created at repo root (or agreed config directory) as the single source of truth.",
            "B) Backend modules:",
            "   - Data models: Room, RoomVersion, Guest, RoomKey, EntryLog",
            "   - RBAC + decorators/middleware for room access",
            "   - API endpoints for hotel, reception, enter/pickup, and frontdesk admin",
            "   - Signed download support (if storage supports it)",
            "   - Telemetry events + audit log",
            "C) Frontend routes and components:",
            "   - / (Lobby), /hotel (map), /hotel/:slug (door), /reception (keys), /frontdesk (admin)",
            "D) Deterministic QA checklist + tests that prove access control and logging are correct.",
        ])
    ))

    sections.append(PromptSection(
        "HOTEL MANIFEST (CREATE FIRST)",
        "\n".join([
            "Create the following file exactly and use it as the authoritative source:",
            codeblock("json", manifest_json),
            "Rules:",
            "- All rooms shown in UI must come from backend reading this manifest or the DB seeded from it.",
            "- Do not hardcode room lists in multiple places.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 1 — DATA MODEL + MIGRATION",
        "\n".join([
            "Implement DB tables/models (SQLite now; compatible with Postgres later):",
            "- rooms: id, slug(unique), name, floor, type, tagline, description_short/long, tags(json), "
            "requirements(json), services(json), status, created_at, updated_at",
            "- room_versions: id, room_id(FK), version, release_notes, artifact_type, file_key, web_url, "
            "sha256, size_bytes, created_at",
            "- guests: id, email(unique), name, role, org_id(optional), created_at",
            "- room_keys: id, guest_id(FK) or org_id, room_id(FK) or bundle, plan, status, expires_at, "
            "max_downloads(optional), created_at",
            "- entry_logs: id, guest_id(FK), room_id(FK), action, version(optional), allow(bool), reason, "
            "ip, user_agent, ts, meta_json",
            "",
            "Seed initial rooms from hotel_manifest.json rooms_seed.",
            "",
            "Verification (deterministic):",
            "1) Run migration/create tables.",
            "2) Insert seed rooms and confirm count == 8.",
            "3) Create a dummy guest and dummy key.",
            "4) Insert a dummy entry_log row.",
            "Evidence: print SQL/ORM queries results or CLI outputs.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 2 — AUTH + RBAC + KEY CHECKS",
        "\n".join([
            "Implement roles: viewer, customer, operator, admin.",
            "Implement key validation:",
            "- active only",
            "- not expired",
            "- not revoked/suspended",
            "",
            "Create middleware/decorator:",
            "- require_auth()",
            "- require_role(min_role)",
            "- require_room_key(room_id)  # checks guest has valid key for room or bundle",
            "",
            "Verification:",
            "- Request room enter/pickup without auth -> 401",
            "- With auth but no key -> 403 and logs 'pickup_denied'/'enter_denied'",
            "- With expired key -> 403 and logs reason 'expired'",
            "- With valid key -> 200 and logs allowed action",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 3 — API ROUTES (HOTEL / RECEPTION / FRONTDESK)",
        "\n".join([
            "Implement endpoints:",
            "Public:",
            "- GET /api/hotel/rooms",
            "- GET /api/hotel/rooms/{slug}",
            "",
            "Reception:",
            "- POST /api/reception/checkin (login)",
            "- GET /api/reception/me",
            "- GET /api/reception/keys/mine",
            "",
            "Room access:",
            "- POST /api/hotel/rooms/{id}/enter  (returns web_url if allowed; else deny)",
            "- POST /api/hotel/rooms/{id}/pickup (returns signed URL or streams file if allowed)",
            "",
            "FrontDesk (admin):",
            "- POST /api/frontdesk/rooms",
            "- POST /api/frontdesk/rooms/{id}/versions",
            "- POST /api/frontdesk/keys/issue",
            "- POST /api/frontdesk/keys/revoke",
            "- GET  /api/frontdesk/events (entry_logs + event aggregation)",
            "",
            "All allow/deny must write entry_logs with reason and metadata.",
            "Never return raw storage keys to clients.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 4 — PROTECTED DOWNLOADS (PICKUP)",
        "\n".join([
            f"Storage target: {ASSUMPTIONS['storage']}",
            "Pickup flow:",
            "1) Client calls pickup",
            "2) Backend validates auth + key",
            "3) Backend logs pickup_started",
            "4) Backend generates signed URL (TTL 60–300s) OR streams file",
            "5) Backend logs pickup_completed on success (or pickup_denied on failure)",
            "",
            "Verification:",
            "- Signed URL expires and fails after TTL",
            "- Attempt pickup without key never returns usable URL",
            "- Audit logs show started/completed/denied correctly",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 5 — FRONTEND ROUTES (LOBBY → MAP → DOOR → RECEPTION → FRONTDESK)",
        "\n".join([
            f"Frontend target: {ASSUMPTIONS['frontend']}",
            "Implement pages:",
            "- /           Lobby: hero + check-in CTA + featured rooms",
            "- /hotel      Hotel Map: search + filters (floor/tags/type) + cards",
            "- /hotel/:slug Room Door: services, requirements, changelog, CTA enter/pickup",
            "- /reception  My Keys: list keys, expiry, available rooms",
            "- /frontdesk  Admin: room CRUD, version publishing, key issuing/revoking, events table",
            "",
            "Components:",
            "- RoomCard, RoomDoor, KeyBadge, AccessButton(state-aware), Filters",
            "",
            "UX rule:",
            "- If user cannot enter/pickup, UI must explain WHY (not checked-in / no key / expired / revoked).",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 6 — TELEMETRY & AUDIT EVENTS",
        "\n".join([
            "Mandatory events (store in entry_logs or a dedicated events table):",
            "- room_viewed",
            "- room_entered",
            "- pickup_started",
            "- pickup_completed",
            "- pickup_denied",
            "- key_issued",
            "- key_revoked",
            "",
            "Each event must include: guest_id, room_id, ts, ip, user_agent, metadata.",
            "Admin can view events, normal users cannot delete logs.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 7 — DETERMINISTIC QA (MUST PASS)",
        "\n".join([
            "Create a QA checklist + automated tests (or script) that verifies:",
            "1) Public can list rooms and view doors",
            "2) Public cannot enter/pickup",
            "3) Auth without key cannot enter/pickup (403)",
            "4) Expired key denies (403) with correct reason",
            "5) Revoked key denies (403) with correct reason",
            "6) Valid key allows enter/pickup (200)",
            "7) All attempts write logs (allow/deny) with correct event names",
            "",
            "Final evidence must include:",
            "- Test command(s) run",
            "- Output summary showing all checks passed",
            "Expected final line:",
            "ALL HOTEL SYSTEM CHECKS PASSED",
        ])
    ))

    sections.append(PromptSection(
        "OUTPUT FORMAT (STRICT)",
        "\n".join([
            "Return a structured debug/build report:",
            "1) Root cause / reason for each change",
            "2) Patch summary (files changed, minimal diffs)",
            "3) Verification steps + evidence (commands + outputs)",
            "4) Risk notes and rollback hints",
            "",
            "Do NOT include unrelated improvements.",
            "Do NOT change naming away from the hotel metaphor.",
        ])
    ))

    # Assemble prompt
    header = "\n".join([
        f"GAHENAX HOTEL SYSTEM — ANTIGRAVITY BUILD PROMPT (generated {now})",
        "=" * 92,
    ])

    body_parts = [header]
    for sec in sections:
        body_parts.append("\n" + sec.title)
        body_parts.append("-" * 92)
        body_parts.append(sec.body.strip())

    return "\n".join(body_parts).rstrip() + "\n"


def main() -> None:
    import sys
    # Fix encoding for Windows console
    if sys.stdout.encoding != 'utf-8':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    prompt = build_prompt()
    print(prompt, end="")


if __name__ == "__main__":
    main()
