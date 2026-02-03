#!/usr/bin/env python3
"""
ANTIGRAVITY AUDIT — Proxy + API + UI/UX (Black-box)
- Deterministic checks with evidence:
  1) Proxy/Edge: TLS assumptions (via https), headers, HSTS, CSP, CORS preflight, caching, timeouts.
  2) API: health checks, auth surface hints, schema/size, error disclosure, rate-limit hints.
  3) UI/UX: HTML-based heuristics (title/meta, viewport, accessibility hints, error/loading markers if detectable).

USAGE:
  python antigravity_audit.py \
    --frontend https://example.com \
    --api https://api.example.com \
    --endpoints /health /api/health /api/config /api/auth/verify \
    --origins https://example.com,http://localhost:5173 \
    --out ./audit_out

NOTES:
- This tool does not prove security; it surfaces high-signal smells.
- For deeper API auth tests you can pass --auth "Bearer <token>".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


# ----------------------------
# Models
# ----------------------------

@dataclass
class Evidence:
    method: str
    url: str
    status: Optional[int]
    elapsed_ms: Optional[float]
    request_headers: Dict[str, str]
    response_headers: Dict[str, str]
    snippet: str


@dataclass
class Finding:
    area: str           # PROXY | API | UIUX
    severity: str       # P0 | P1 | P2 | INFO
    title: str
    why: str
    patch_hint: str
    evidence_ref: str   # key to evidence map


@dataclass
class Report:
    target_frontend: str
    target_api: str
    timestamp_utc: str
    findings: List[Finding]
    evidences: Dict[str, Evidence]


# ----------------------------
# Helpers
# ----------------------------

def now_utc_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def safe_snippet(text: str, limit: int = 600) -> str:
    text = text or ""
    text = text.replace("\r", "")
    return text[:limit]


def mk_headers(auth: Optional[str], extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    h = {
        "User-Agent": "Antigravity-Audit/1.0",
        "Accept": "*/*",
    }
    if auth:
        # If user passes already "Bearer x", keep it
        h["Authorization"] = auth
    if extra:
        h.update(extra)
    return h


def request_with_evidence(
    key: str,
    method: str,
    url: str,
    headers: Dict[str, str],
    timeout_s: float = 12.0,
    data: Optional[bytes] = None,
) -> Tuple[str, Evidence]:
    try:
        t0 = time.perf_counter()
        resp = requests.request(method, url, headers=headers, timeout=timeout_s, data=data, allow_redirects=False)
        elapsed = (time.perf_counter() - t0) * 1000.0
        snippet = ""
        ct = resp.headers.get("content-type", "")
        if "text" in ct or "json" in ct or ct == "" or ct.startswith("application/"):
            try:
                snippet = safe_snippet(resp.text)
            except Exception:
                snippet = ""
        ev = Evidence(
            method=method,
            url=url,
            status=resp.status_code,
            elapsed_ms=round(elapsed, 2),
            request_headers={k: v for k, v in headers.items()},
            response_headers={k.lower(): v for k, v in resp.headers.items()},
            snippet=snippet,
        )
        return key, ev
    except Exception as e:
        ev = Evidence(
            method=method,
            url=url,
            status=None,
            elapsed_ms=None,
            request_headers={k: v for k, v in headers.items()},
            response_headers={},
            snippet=f"REQUEST_ERROR: {repr(e)}",
        )
        return key, ev


def classify_severity(condition: bool, p_if_true: str) -> str:
    return p_if_true if condition else "INFO"


def is_https(url: str) -> bool:
    return url.lower().startswith("https://")


def join_url(base: str, path: str) -> str:
    base = base.rstrip("/")
    path = path if path.startswith("/") else f"/{path}"
    return base + path


def header_get(headers: Dict[str, str], name: str) -> Optional[str]:
    return headers.get(name.lower())


# ----------------------------
# Audit logic
# ----------------------------

SEC_HEADERS = {
    "strict-transport-security": ("P1", "Enable HSTS (be careful: only after HTTPS stable)."),
    "x-content-type-options": ("P2", "Add X-Content-Type-Options: nosniff"),
    "referrer-policy": ("P2", "Add Referrer-Policy (e.g., no-referrer or strict-origin-when-cross-origin)."),
}

CSP_HINT = ("P2", "Add a baseline Content-Security-Policy; start permissive then tighten.")
FRAME_HINT = ("P2", "Prevent clickjacking via CSP frame-ancestors 'none' or X-Frame-Options DENY.")


def audit_proxy(frontend: str, api: str, origins: List[str], auth: Optional[str],
                evidences: Dict[str, Evidence], findings: List[Finding]) -> None:
    area = "PROXY"

    # 1) Basic HEAD on frontend and API root
    for target_name, base in [("frontend", frontend), ("api", api)]:
        if not base:
            continue
        url = base
        key, ev = request_with_evidence(f"{area}:{target_name}:HEAD", "HEAD", url, mk_headers(auth))
        evidences[key] = ev

        if ev.status is None:
            findings.append(Finding(
                area=area, severity="P0",
                title=f"{target_name} unreachable",
                why=f"Could not reach {url}. Network/DNS/TLS/proxy issue blocks all other checks.",
                patch_hint="Verify DNS, TLS cert, proxy target, and upstream health. Fix routing first.",
                evidence_ref=key
            ))
            continue

        # 2) Enforce HTTPS sanity (basic)
        if not is_https(url):
            findings.append(Finding(
                area=area, severity="P0",
                title=f"{target_name} not using HTTPS URL in audit target",
                why="If your public entry is HTTP, you risk mixed content and credential leakage.",
                patch_hint="Serve only HTTPS externally and redirect HTTP to HTTPS (301/308).",
                evidence_ref=key
            ))

        # 3) Security headers presence
        for hname, (sev, hint) in SEC_HEADERS.items():
            if header_get(ev.response_headers, hname) is None:
                findings.append(Finding(
                    area=area, severity=sev,
                    title=f"Missing security header: {hname} ({target_name})",
                    why=f"{hname} not present on {target_name} responses. This increases baseline risk.",
                    patch_hint=hint,
                    evidence_ref=key
                ))

        # CSP / frame protections
        csp = header_get(ev.response_headers, "content-security-policy")
        xfo = header_get(ev.response_headers, "x-frame-options")
        if not csp:
            findings.append(Finding(
                area=area, severity=CSP_HINT[0],
                title=f"Missing Content-Security-Policy ({target_name})",
                why="No CSP means higher XSS blast radius.",
                patch_hint=CSP_HINT[1],
                evidence_ref=key
            ))
        else:
            # Check frame-ancestors
            if "frame-ancestors" not in csp.lower() and not xfo:
                findings.append(Finding(
                    area=area, severity=FRAME_HINT[0],
                    title=f"No clickjacking protection (frame-ancestors/x-frame-options) ({target_name})",
                    why="Without frame controls, your UI can be embedded and clickjacked.",
                    patch_hint=FRAME_HINT[1],
                    evidence_ref=key
                ))

        # Caching smell (for API especially)
        cc = header_get(ev.response_headers, "cache-control")
        if target_name == "api" and cc and ("public" in cc.lower() or "max-age" in cc.lower()):
            findings.append(Finding(
                area=area, severity="P1",
                title="API responses appear cacheable at the edge",
                why=f"Cache-Control='{cc}' on API root. Risk: stale or leaked responses depending on proxy/CDN.",
                patch_hint="For sensitive API endpoints, use Cache-Control: no-store (or private, no-cache) and set Vary appropriately.",
                evidence_ref=key
            ))

    # 4) CORS preflight checks against API (OPTIONS)
    if api and origins:
        for origin in origins:
            # Typical preflight to /api/health if exists, else /health
            preflight_path = "/api/health"
            url = join_url(api, preflight_path)
            headers = mk_headers(auth, {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type,authorization"
            })
            key, ev = request_with_evidence(f"{area}:api:OPTIONS:{origin}", "OPTIONS", url, headers)
            evidences[key] = ev

            if ev.status is None:
                findings.append(Finding(
                    area=area, severity="P0",
                    title="CORS preflight unreachable",
                    why=f"OPTIONS to {url} failed. Browser calls from {origin} may be blocked.",
                    patch_hint="Ensure proxy forwards OPTIONS and API responds with correct CORS headers for preflight.",
                    evidence_ref=key
                ))
                continue

            aco = header_get(ev.response_headers, "access-control-allow-origin")
            acc = header_get(ev.response_headers, "access-control-allow-credentials")
            if not aco:
                findings.append(Finding(
                    area=area, severity="P0",
                    title="CORS missing Access-Control-Allow-Origin",
                    why=f"Preflight response lacks ACAO for Origin={origin}. Browser will block requests.",
                    patch_hint="Set Access-Control-Allow-Origin to the exact allowed origin(s). Avoid '*' if credentials are used.",
                    evidence_ref=key
                ))
            else:
                if aco.strip() == "*" and (acc and acc.lower() == "true"):
                    findings.append(Finding(
                        area=area, severity="P0",
                        title="CORS invalid: '*' with credentials",
                        why="ACAO='*' cannot be used with Access-Control-Allow-Credentials=true.",
                        patch_hint="Return the specific Origin instead of '*', or disable credentials.",
                        evidence_ref=key
                    ))

            # Allow methods/headers sanity
            am = header_get(ev.response_headers, "access-control-allow-methods") or ""
            ah = header_get(ev.response_headers, "access-control-allow-headers") or ""
            if "post" not in am.lower():
                findings.append(Finding(
                    area=area, severity="P1",
                    title="CORS preflight does not allow POST",
                    why=f"Allow-Methods='{am}' may block forms/mutations from the UI.",
                    patch_hint="Include required methods in Access-Control-Allow-Methods (GET,POST,PUT,DELETE...).",
                    evidence_ref=key
                ))
            if "authorization" not in ah.lower():
                findings.append(Finding(
                    area=area, severity="P1",
                    title="CORS preflight may block Authorization header",
                    why=f"Allow-Headers='{ah}' missing 'authorization'.",
                    patch_hint="Include 'authorization' and 'content-type' in Access-Control-Allow-Headers.",
                    evidence_ref=key
                ))


def audit_api(api: str, endpoints: List[str], auth: Optional[str],
              evidences: Dict[str, Evidence], findings: List[Finding]) -> None:
    if not api:
        return
    area = "API"

    # Default endpoints if none provided
    if not endpoints:
        endpoints = ["/health", "/api/health", "/api/config", "/api/auth/verify"]

    # 1) GET checks
    for ep in endpoints:
        url = join_url(api, ep)
        key, ev = request_with_evidence(f"{area}:GET:{ep}", "GET", url, mk_headers(auth))
        evidences[key] = ev

        if ev.status is None:
            findings.append(Finding(
                area=area, severity="P0",
                title="API endpoint unreachable",
                why=f"GET {ep} failed. Could be routing, proxy, or upstream crash.",
                patch_hint="Fix proxy route to API, ensure upstream process is healthy, verify base URL.",
                evidence_ref=key
            ))
            continue

        # Error disclosure smell
        if ev.snippet and re.search(r"traceback|stack trace|exception", ev.snippet, re.IGNORECASE):
            findings.append(Finding(
                area=area, severity="P0",
                title="Potential stack trace / exception disclosure",
                why="Response body contains traceback/exception terms. This can leak internals and aid attacks.",
                patch_hint="Implement safe error handler: return generic client errors; log full stack only server-side.",
                evidence_ref=key
            ))

        # Config exposure smell
        if "/config" in ep and ev.status == 200:
            findings.append(Finding(
                area=area, severity="P1",
                title="Config endpoint publicly readable (possible info leak)",
                why=f"{ep} returned 200. If it exposes internal policy/config, this is an information disclosure risk.",
                patch_hint="Require auth + RBAC for config reads; redact secrets; consider splitting public vs internal config.",
                evidence_ref=key
            ))

        # Missing rate limit hints (not proof, but smell)
        if header_get(ev.response_headers, "x-ratelimit-limit") is None and "/auth" in ep:
            findings.append(Finding(
                area=area, severity="P2",
                title="No visible rate-limit headers on auth endpoint",
                why="Absence of rate-limit headers doesn't prove none exists, but often correlates with missing throttling.",
                patch_hint="Add rate limiting to /auth/* and public endpoints; expose standard headers if desired.",
                evidence_ref=key
            ))

    # 2) Oversized payload rejection probe (POST)
    # We try /api/submit if present in endpoints, else /api/auth/verify else skip
    candidate = None
    for c in ["/api/submit", "/api/auth/verify", "/api/leads", "/api/config"]:
        if c in endpoints or any(c in e for e in endpoints):
            candidate = c
            break
    if candidate:
        url = join_url(api, candidate)
        big = ("A" * 200_000).encode("utf-8")  # 200 KB
        headers = mk_headers(auth, {"Content-Type": "application/json"})
        key, ev = request_with_evidence(f"{area}:POST:big:{candidate}", "POST", url, headers, data=big)
        evidences[key] = ev

        if ev.status and ev.status in (200, 201, 204):
            findings.append(Finding(
                area=area, severity="P1",
                title="Large payload accepted without obvious rejection",
                why="Accepting big payloads can amplify abuse and memory pressure if not bounded.",
                patch_hint="Enforce request size limits at proxy and app layer; validate schema; reject unknown fields.",
                evidence_ref=key
            ))
        elif ev.status and ev.status in (413, 400, 422):
            findings.append(Finding(
                area=area, severity="INFO",
                title="Large payload rejected (good signal)",
                why=f"POST {candidate} returned {ev.status}. Indicates some input bounding/validation.",
                patch_hint="Keep strict limits; ensure error message is safe and consistent.",
                evidence_ref=key
            ))


def audit_uiux(frontend: str, auth: Optional[str],
              evidences: Dict[str, Evidence], findings: List[Finding]) -> None:
    if not frontend:
        return
    area = "UIUX"

    # Fetch HTML
    key, ev = request_with_evidence(f"{area}:GET:root", "GET", frontend, mk_headers(auth, {"Accept": "text/html"}))
    evidences[key] = ev

    if ev.status is None:
        findings.append(Finding(
            area=area, severity="P0",
            title="Frontend unreachable",
            why="Cannot load UI, so UX is blocked before it begins.",
            patch_hint="Fix DNS/TLS/proxy routing for the frontend.",
            evidence_ref=key
        ))
        return

    # Basic meta tags
    html = ev.snippet or ""
    if "<title" not in html.lower():
        findings.append(Finding(
            area=area, severity="P2",
            title="Missing <title> tag in initial HTML",
            why="Hurts usability (tabs/history) and SEO/social previews.",
            patch_hint="Ensure server-rendered HTML includes a meaningful <title>.",
            evidence_ref=key
        ))
    if 'name="viewport"' not in html.lower():
        findings.append(Finding(
            area=area, severity="P2",
            title="Missing viewport meta",
            why="Mobile rendering may be broken or scaled oddly.",
            patch_hint='Add <meta name="viewport" content="width=device-width,initial-scale=1" />',
            evidence_ref=key
        ))

    # Accessibility heuristics
    if 'lang="' not in html.lower():
        findings.append(Finding(
            area=area, severity="P2",
            title="HTML lang attribute missing",
            why="Screen readers and browsers rely on lang for pronunciation and defaults.",
            patch_hint='Set <html lang="es"> (or appropriate locale).',
            evidence_ref=key
        ))

    # Detect “silent failure” UX smell: no obvious loading/error markers
    # Heuristic only: search for common tokens
    tokens = ["loading", "cargando", "error", "retry", "reintentar", "toast", "notification", "alert"]
    token_hits = [t for t in tokens if t in html.lower()]
    if len(token_hits) == 0:
        findings.append(Finding(
            area=area, severity="INFO",
            title="No detectable loading/error affordances in initial HTML (heuristic)",
            why="Not a proof, but SPAs sometimes forget clear states. Worth verifying in-app flows.",
            patch_hint="Ensure UI has explicit Loading/Empty/Error/Success states with actionable copy.",
            evidence_ref=key
        ))


# ----------------------------
# Report rendering
# ----------------------------

def to_markdown(report: Report) -> str:
    lines = []
    lines.append(f"# ANTIGRAVITY AUDIT REPORT")
    lines.append("")
    lines.append(f"- Frontend: `{report.target_frontend}`")
    lines.append(f"- API: `{report.target_api}`")
    lines.append(f"- Timestamp (UTC): `{report.timestamp_utc}`")
    lines.append("")
    lines.append("## Findings (P0/P1/P2)")
    lines.append("")
    if not report.findings:
        lines.append("✅ No findings generated (this is unusual; verify targets and endpoints).")
    else:
        # Sort by severity order
        order = {"P0": 0, "P1": 1, "P2": 2, "INFO": 3}
        for f in sorted(report.findings, key=lambda x: order.get(x.severity, 99)):
            lines.append(f"### [{f.severity}] {f.area}: {f.title}")
            lines.append(f"- Why: {f.why}")
            lines.append(f"- Patch hint: {f.patch_hint}")
            lines.append(f"- Evidence: `{f.evidence_ref}`")
            lines.append("")
    lines.append("## Evidence")
    lines.append("")
    for k, ev in report.evidences.items():
        lines.append(f"### {k}")
        lines.append(f"- {ev.method} {ev.url}")
        lines.append(f"- Status: {ev.status} | Time: {ev.elapsed_ms}ms")
        # show key headers compact
        interesting = ["server", "content-type", "cache-control", "strict-transport-security",
                       "content-security-policy", "x-frame-options", "access-control-allow-origin",
                       "access-control-allow-credentials", "access-control-allow-methods", "access-control-allow-headers"]
        h = []
        for name in interesting:
            val = ev.response_headers.get(name)
            if val:
                h.append(f"  - {name}: {val}")
        if h:
            lines.append("- Response headers (selected):")
            lines.extend(h)
        if ev.snippet:
            lines.append("- Snippet:")
            lines.append("```")
            lines.append(ev.snippet)
            lines.append("```")
        lines.append("")
    return "\n".join(lines)


def write_outputs(out_dir: Path, report: Report) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out_dir / "antigravity_audit_report.json"
    payload = {
        "target_frontend": report.target_frontend,
        "target_api": report.target_api,
        "timestamp_utc": report.timestamp_utc,
        "findings": [asdict(f) for f in report.findings],
        "evidences": {k: asdict(v) for k, v in report.evidences.items()},
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown
    md_path = out_dir / "antigravity_audit_report.md"
    md_path.write_text(to_markdown(report), encoding="utf-8")

    print("=== ANTIGRAVITY AUDIT COMPLETE ===")
    print(f"JSON: {json_path}")
    print(f"MD:   {md_path}")


# ----------------------------
# CLI
# ----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Antigravity black-box audit (Proxy + API + UI/UX).")
    p.add_argument("--frontend", default="", help="Frontend base URL (e.g., https://example.com).")
    p.add_argument("--api", default="", help="API base URL (e.g., https://api.example.com).")
    p.add_argument("--endpoints", nargs="*", default=[], help="API endpoints to check (paths), e.g. /health /api/config")
    p.add_argument("--origins", default="", help="Comma-separated origins for CORS checks, e.g. https://x.com,http://localhost:5173")
    p.add_argument("--auth", default="", help='Optional Authorization header value, e.g. "Bearer <token>"')
    p.add_argument("--out", default="./audit_out", help="Output directory for reports.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    frontend = args.frontend.strip()
    api = args.api.strip()
    endpoints = [e.strip() for e in args.endpoints if e.strip()]
    origins = [o.strip() for o in args.origins.split(",") if o.strip()] if args.origins else []
    auth = args.auth.strip() or None

    evidences: Dict[str, Evidence] = {}
    findings: List[Finding] = []

    # Strict causality order
    audit_proxy(frontend, api, origins, auth, evidences, findings)
    audit_api(api, endpoints, auth, evidences, findings)
    audit_uiux(frontend, auth, evidences, findings)

    report = Report(
        target_frontend=frontend,
        target_api=api,
        timestamp_utc=now_utc_iso(),
        findings=findings,
        evidences=evidences,
    )

    write_outputs(Path(args.out), report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
