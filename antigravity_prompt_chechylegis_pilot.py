#!/usr/bin/env python3
"""
ANTIGRAVITY PROMPT MASTER — PILOT ROOM (ChechyLegis Only)

Generates a focused prompt for integrating ONLY ChechyLegis as the first hotel room,
validating the entire Hotel architecture before scaling to other rooms.

Usage:
  python antigravity_prompt_chechylegis_pilot.py > PROMPT_CHECHYLEGIS_PILOT.txt
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import textwrap


# =========================
# REAL STACK (ChechyLegis)
# =========================
ASSUMPTIONS = {
    "backend_framework": "FastAPI",    # ChechyLegis uses FastAPI, NOT Flask
    "db": "SQLite",                    # judicial_archive.db exists
    "orm": "SQLAlchemy",               # Assumed (confirm if using raw SQL)
    "storage": "Local",                # Start with local, migrate to R2 later
    "frontend": "Vanilla",             # ChechyLegis uses Vanilla JS, NOT React
    "auth": "session+jwt",             # To be implemented
    "existing_app_port": 8000,         # ChechyLegis runs on :8000
    "existing_app_path": "c:\\Users\\USUARIO\\OneDrive\\Desktop\\Legischechy",
    "domain": "gahenaxaisolutions.com",
    "integration_strategy": "Gateway Wrapper",  # Minimal invasiveness
}

# =========================
# PILOT ROOM: ChechyLegis
# =========================
PILOT_ROOM = {
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
    "status": "active",
    "existing_url": "http://localhost:8000/static/index.html",
    "version": "v1.1.0"
}


@dataclass
class PromptSection:
    title: str
    body: str


def codeblock(lang: str, content: str) -> str:
    return f"```{lang}\n{content.rstrip()}\n```"


def make_pilot_manifest() -> dict:
    return {
        "hotel": {
            "domain": ASSUMPTIONS["domain"],
            "concept": "Hotel model: site=lobby, each app=room, access via keys, everything logged.",
            "mode": "PILOT",
            "pilot_room": "chechylegis"
        },
        "floors": [
            {"id": 4, "name": "Legal", "active": True},
            {"id": 1, "name": "Operación", "active": False},
            {"id": 2, "name": "Decisión", "active": False},
            {"id": 3, "name": "Producción", "active": False},
            {"id": 5, "name": "Mercado", "active": False},
        ],
        "plans": [
            {"id": "core", "name": "Core Stay", "price": 0},
            {"id": "pro", "name": "Pro Stay", "price": 50},
            {"id": "max", "name": "Max Stay", "price": 100},
        ],
        "access_rules": {
            "roles": ["viewer", "customer", "operator", "admin"],
            "rule_1": "Public can view lobby and room door but cannot enter without auth+valid key.",
            "rule_2": "Backend always authorizes. ChechyLegis accessible only via Hotel gateway.",
            "rule_3": "All enter attempts are logged with allow/deny reasons.",
        },
        "ui_routes": [
            {"path": "/", "name": "Lobby", "public": True},
            {"path": "/hotel", "name": "Hotel Map (Single Room)", "public": True},
            {"path": "/hotel/chechylegis", "name": "ChechyLegis Door", "public": True},
            {"path": "/reception", "name": "Guest Reception", "auth_required": True},
            {"path": "/frontdesk", "name": "Admin FrontDesk", "role": "admin"},
        ],
        "api_routes": [
            {"method": "GET", "path": "/api/hotel/rooms", "desc": "List rooms (only ChechyLegis)"},
            {"method": "GET", "path": "/api/hotel/rooms/chechylegis", "desc": "Room details"},
            {"method": "POST", "path": "/api/reception/checkin", "desc": "Login"},
            {"method": "GET", "path": "/api/reception/me", "desc": "Current user info"},
            {"method": "GET", "path": "/api/reception/keys/mine", "desc": "My active keys"},
            {"method": "POST", "path": "/api/hotel/rooms/chechylegis/enter", "desc": "Attempt room access"},
            {"method": "POST", "path": "/api/frontdesk/keys/issue", "desc": "Admin: issue key", "role": "admin"},
            {"method": "POST", "path": "/api/frontdesk/keys/revoke", "desc": "Admin: revoke key", "role": "admin"},
            {"method": "GET", "path": "/api/frontdesk/events", "desc": "Admin: view logs", "role": "admin"},
        ],
        "rooms_seed": [PILOT_ROOM],
        "integration": {
            "strategy": ASSUMPTIONS["integration_strategy"],
            "existing_app": {
                "path": ASSUMPTIONS["existing_app_path"],
                "port": ASSUMPTIONS["existing_app_port"],
                "framework": ASSUMPTIONS["backend_framework"],
                "frontend": ASSUMPTIONS["frontend"],
            }
        }
    }


def build_prompt() -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = make_pilot_manifest()
    manifest_json = json.dumps(manifest, ensure_ascii=False, indent=2)
    
    sections: list[PromptSection] = []

    sections.append(PromptSection(
        "ROLE",
        "\n".join([
            "You are ANTIGRAVITY — Build & QA Gatekeeper for the GAHENAX HOTEL SYSTEM (PILOT MODE).",
            "You will integrate ChechyLegis as the FIRST and ONLY room to validate the Hotel architecture.",
        ])
    ))

    sections.append(PromptSection(
        "CONTEXT",
        "\n".join([
            f"Domain: {ASSUMPTIONS['domain']}",
            "Mode: PILOT (single room validation)",
            "Pilot Room: ChechyLegis (existing app at v1.1.0)",
            "",
            "ChechyLegis is an existing, working FastAPI application:",
            f"- Location: {ASSUMPTIONS['existing_app_path']}",
            f"- Port: {ASSUMPTIONS['existing_app_port']}",
            "- Frontend: Vanilla JavaScript SPA",
            "- DB: SQLite (judicial_archive.db)",
            "- Status: PRODUCTIVE",
            "",
            "Goal: Add Hotel layer (auth, keys, access control) WITHOUT breaking existing app.",
        ])
    ))

    sections.append(PromptSection(
        "NON-NEGOTIABLE RULES",
        "\n".join([
            "1) PILOT MODE: Integrate ONLY ChechyLegis. Do NOT add other rooms.",
            "2) Minimal invasiveness: Wrap existing app, don't rewrite it.",
            "3) Strict causality order: schema → auth → gateway → UI → logs → QA.",
            "4) Every phase must include deterministic verification steps with evidence.",
            "5) ChechyLegis must remain functional if Hotel layer is disabled.",
            "6) Backend framework is FastAPI (NOT Flask).",
            "7) Frontend is Vanilla JS (NOT React).",
            "8) Do NOT touch existing ChechyLegis core logic unless absolutely necessary.",
        ])
    ))

    sections.append(PromptSection(
        "ASSUMPTIONS (VERIFIED FOR CHECHYLEGIS)",
        codeblock("json", json.dumps(ASSUMPTIONS, indent=2))
    ))

    sections.append(PromptSection(
        "INTEGRATION STRATEGY: GATEWAY WRAPPER",
        "\n".join([
            "Architecture:",
            "",
            "┌─────────────────────────────────────────┐",
            "│  Hotel Gateway (NEW)                   │",
            "│  - Auth & Session Management           │",
            "│  - Room Key Validation                 │",
            "│  - Access Control Middleware           │",
            "│  - Audit Logging                       │",
            "└────────────┬────────────────────────────┘",
            "             │",
            "             ▼ (proxy if key valid)",
            "┌─────────────────────────────────────────┐",
            "│  ChechyLegis (EXISTING v1.1.0)          │",
            "│  - Runs unchanged on :8000              │",
            "│  - All existing routes work             │",
            "│  - No modifications to core logic       │",
            "└─────────────────────────────────────────┘",
            "",
            "Flow:",
            "1. User requests /hotel/chechylegis/enter",
            "2. Gateway checks: auth → key → plan → expiry",
            "3. If ALL pass: proxy to ChechyLegis + log 'room_entered'",
            "4. If ANY fail: deny + log reason (no_auth / no_key / expired / wrong_plan)",
            "",
            "Benefits:",
            "- ChechyLegis remains untouched and stable",
            "- Hotel layer can be toggled on/off",
            "- Easy to debug and rollback",
            "- Fast to implement and test",
        ])
    ))

    sections.append(PromptSection(
        "PILOT MANIFEST (CREATE FIRST)",
        "\n".join([
            "Create hotel_manifest_pilot.json with ONLY ChechyLegis:",
            codeblock("json", manifest_json),
            "",
            "Rules:",
            "- Seed ONLY this one room in the database.",
            "- UI shows ONLY this room in the Hotel map.",
            "- Do NOT reference or scaffold other rooms.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 1 — DATA MODEL + MIGRATION (HOTEL TABLES ONLY)",
        "\n".join([
            "Add NEW tables to existing judicial_archive.db (do NOT touch existing tables):",
            "",
            "hotel_guests:",
            "  id, email(unique), name, role, password_hash, created_at",
            "",
            "hotel_rooms:",
            "  id, slug(unique), name, floor, type, tagline, description_short, description_long,",
            "  tags(json), requirements(json), services(json), access_policy(json), status, created_at",
            "",
            "hotel_room_keys:",
            "  id, guest_id(FK), room_id(FK), plan, status, issued_at, expires_at, revoked_at",
            "",
            "hotel_entry_logs:",
            "  id, guest_id(FK), room_id(FK), action, allow(bool), reason, ip, user_agent, ts",
            "",
            "Seed:",
            "- Insert ChechyLegis room from manifest",
            "- Create test guest: test@gahenax.com / password: test123 / role: customer",
            "- Create test key: guest=test@gahenax.com, room=chechylegis, plan=pro, expires=+30days",
            "",
            "Verification:",
            "1) SELECT COUNT(*) FROM hotel_rooms; -- expect 1",
            "2) SELECT * FROM hotel_guests WHERE email='test@gahenax.com'; -- expect 1 row",
            "3) SELECT * FROM hotel_room_keys WHERE guest_id=1; -- expect 1 active key",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 2 — AUTH + KEY VALIDATION MIDDLEWARE",
        "\n".join([
            "Create FastAPI dependencies:",
            "",
            "1) get_current_user() -> Guest | None",
            "   - Check session or JWT",
            "   - Return Guest object or None",
            "",
            "2) require_auth() -> Guest",
            "   - Calls get_current_user()",
            "   - Raises 401 if None",
            "",
            "3) require_room_key(room_slug: str) -> RoomKey",
            "   - Requires auth first",
            "   - Query hotel_room_keys where:",
            "     * guest_id = current_user.id",
            "     * room_id = (room with slug)",
            "     * status = 'active'",
            "     * expires_at > now()",
            "   - Raises 403 if not found, expired, or wrong plan",
            "   - Returns valid RoomKey",
            "",
            "Verification:",
            "- Request /api/hotel/rooms/chechylegis/enter WITHOUT auth -> 401",
            "- WITH auth (test@gahenax.com) but DELETE key -> 403 'no_key'",
            "- WITH auth + expired key -> 403 'expired'",
            "- WITH auth + valid key -> 200 (enter allowed)",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 3 — HOTEL API ROUTES (MINIMAL SET)",
        "\n".join([
            "Public routes:",
            "GET /api/hotel/rooms",
            "  -> returns [ChechyLegis] (only room in pilot)",
            "",
            "GET /api/hotel/rooms/chechylegis",
            "  -> returns room details + door state (locked/unlocked for current user)",
            "",
            "Auth routes:",
            "POST /api/reception/checkin",
            "  body: {email, password}",
            "  -> login, create session, return user info",
            "",
            "GET /api/reception/me",
            "  -> current user info (requires auth)",
            "",
            "GET /api/reception/keys/mine",
            "  -> list my active keys",
            "",
            "Room access:",
            "POST /api/hotel/rooms/chechylegis/enter",
            "  -> validate key, log attempt, return access_url or deny",
            "  -> if allowed: return {allowed: true, url: 'http://localhost:8000/static/index.html'}",
            "  -> if denied: return {allowed: false, reason: 'no_key|expired|wrong_plan'}",
            "",
            "Admin routes:",
            "POST /api/frontdesk/keys/issue (admin only)",
            "  body: {guest_email, room_slug, plan, expires_days}",
            "",
            "POST /api/frontdesk/keys/revoke (admin only)",
            "  body: {key_id}",
            "",
            "GET /api/frontdesk/events (admin only)",
            "  -> query entry_logs with filters",
            "",
            "ALL routes must log entry attempts with reason.",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 4 — MINIMAL LOBBY UI (VANILLA JS)",
        "\n".join([
            "Create NEW files (do NOT modify existing ChechyLegis static/):",
            "",
            "hotel_lobby/",
            "  index.html         -- Lobby landing page",
            "  hotel.html         -- Hotel map (shows only ChechyLegis)",
            "  room_door.html     -- ChechyLegis door page",
            "  reception.html     -- Login + My Keys",
            "  frontdesk.html     -- Admin panel (keys, logs)",
            "  css/",
            "    lobby.css        -- Styling",
            "  js/",
            "    hotel_api.js     -- API client",
            "    lobby.js         -- Lobby logic",
            "    hotel_map.js     -- Map rendering",
            "    room_door.js     -- Door state + enter button",
            "",
            "Components:",
            "- RoomCard: shows ChechyLegis with lock icon (locked/unlocked based on user's keys)",
            "- EnterButton: state-aware (Login / No Key / Expired / Enter)",
            "- LoginForm: email/password -> /api/reception/checkin",
            "- KeyList: shows user's active keys with expiry",
            "",
            "UX Rules:",
            "- If not logged in: show 'Login to enter'",
            "- If logged in but no key: show 'No access key. Contact admin.'",
            "- If expired: show 'Key expired on {date}'",
            "- If valid: show 'Enter ChechyLegis →' (clickable)",
            "",
            "On 'Enter' click:",
            "- POST /api/hotel/rooms/chechylegis/enter",
            "- If allowed: redirect to response.url (ChechyLegis)",
            "- If denied: show error modal with reason",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 5 — AUDIT LOGGING (ALL ACCESS ATTEMPTS)",
        "\n".join([
            "Every access attempt MUST log to hotel_entry_logs:",
            "",
            "Fields:",
            "- guest_id: user.id or NULL if not authenticated",
            "- room_id: chechylegis room id",
            "- action: 'enter_attempt'",
            "- allow: true/false",
            "- reason: 'success' / 'no_auth' / 'no_key' / 'expired' / 'wrong_plan' / 'revoked'",
            "- ip: request.client.host",
            "- user_agent: request.headers['user-agent']",
            "- ts: UTC timestamp",
            "",
            "Log points:",
            "1) Before key validation (log 'enter_attempt')",
            "2) After validation (update allow + reason)",
            "",
            "Admin can query:",
            "GET /api/frontdesk/events?room=chechylegis&guest_email=x&allow=false",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 6 — DETERMINISTIC QA (MUST PASS)",
        "\n".join([
            "Create qa_pilot_chechylegis.py that tests:",
            "",
            "Test 1: Public can list rooms",
            "  GET /api/hotel/rooms",
            "  -> expect 200, [ChechyLegis]",
            "",
            "Test 2: Public can view door (but not enter)",
            "  GET /api/hotel/rooms/chechylegis",
            "  -> expect 200, room details",
            "",
            "Test 3: Unauthenticated enter -> denied",
            "  POST /api/hotel/rooms/chechylegis/enter (no auth)",
            "  -> expect 401",
            "  -> verify entry_log: allow=false, reason='no_auth'",
            "",
            "Test 4: Authenticated without key -> denied",
            "  Login as user with no keys",
            "  POST /api/hotel/rooms/chechylegis/enter",
            "  -> expect 403",
            "  -> verify entry_log: allow=false, reason='no_key'",
            "",
            "Test 5: Expired key -> denied",
            "  Create key with expires_at in past",
            "  Login + POST enter",
            "  -> expect 403",
            "  -> verify entry_log: allow=false, reason='expired'",
            "",
            "Test 6: Valid key -> allowed",
            "  Login as test@gahenax.com (has valid pro key)",
            "  POST /api/hotel/rooms/chechylegis/enter",
            "  -> expect 200, {allowed: true, url: '...'}",
            "  -> verify entry_log: allow=true, reason='success'",
            "",
            "Test 7: Admin can issue key",
            "  Login as admin",
            "  POST /api/frontdesk/keys/issue {guest_email, room_slug, plan, expires_days}",
            "  -> expect 201",
            "  -> verify new key in DB",
            "",
            "Test 8: Admin can revoke key",
            "  POST /api/frontdesk/keys/revoke {key_id}",
            "  -> expect 200",
            "  -> verify key status='revoked' in DB",
            "",
            "Final output:",
            "PILOT QA SUMMARY:",
            "✓ Public access works",
            "✓ Unauthenticated denied",
            "✓ No key denied",
            "✓ Expired key denied",
            "✓ Valid key allowed",
            "✓ All attempts logged",
            "ALL CHECHYLEGIS PILOT CHECKS PASSED",
        ])
    ))

    sections.append(PromptSection(
        "PHASE 7 — ROLLBACK PLAN",
        "\n".join([
            "If anything breaks:",
            "",
            "1) Hotel tables are isolated (no FK to existing ChechyLegis tables)",
            "2) ChechyLegis can run standalone on :8000 without Hotel layer",
            "3) To disable Hotel: stop Hotel gateway, access ChechyLegis directly",
            "",
            "Rollback steps:",
            "- DROP hotel_* tables",
            "- DELETE hotel_lobby/ directory",
            "- ChechyLegis remains untouched and functional",
        ])
    ))

    sections.append(PromptSection(
        "OUTPUT FORMAT (STRICT)",
        "\n".join([
            "Return a structured report:",
            "1) Changes summary (new files, new tables, no changes to existing code)",
            "2) Integration point (how gateway proxies to ChechyLegis)",
            "3) QA results (all 8 tests with evidence)",
            "4) Next steps (how to add more rooms after pilot succeeds)",
            "",
            "Do NOT modify existing ChechyLegis code unless absolutely critical.",
            "Do NOT add rooms other than ChechyLegis.",
        ])
    ))

    # Assemble
    header = "\n".join([
        f"GAHENAX HOTEL PILOT — CHECHYLEGIS INTEGRATION (generated {now})",
        "=" * 92,
        "",
        "MODE: PILOT (Single Room Validation)",
        "ROOM: ChechyLegis v1.1.0",
        "STRATEGY: Gateway Wrapper (Minimal Invasiveness)",
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
    if sys.stdout.encoding != 'utf-8':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    prompt = build_prompt()
    print(prompt, end="")


if __name__ == "__main__":
    main()
