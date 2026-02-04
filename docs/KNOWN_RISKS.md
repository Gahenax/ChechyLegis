# KNOWN RISKS - CHECHYLEGIS (GAHENAX-GOLD)

These risks are accepted for the **Role Simulation** deployment model (Single Tenant/Personal Use).

## 1. Authentication Spoofing
- **Risk**: Any user with network access to the API or UI can switch roles (Viewer/Operator/Admin) and perform actions (including deletions).
- **Impact**: Unauthorized data modification.
- **Likelihood**: High (on shared networks).
- **Mitigation**: Deploy **ONLY** on a single-user machine (localhost) or behind a secure VPN/Zero Trust Access proxy.

## 2. File Concurrency (SQLite)
- **Risk**: Writes may block if multiple concurrent requests hit the API simultaneously.
- **Impact**: `500 Internal Server Error` or timeout during heavy write operations.
- **Likelihood**: Low (single user). Medium (5+ users).
- **Mitigation**: Keep user count low (<3 concurrent writers).

## 3. Data Durability (Local Storage)
- **Risk**: Loss of `judicial_archive.db` or `storage/` directory due to disk failure or accidental deletion.
- **Impact**: Critical data loss.
- **Likelihood**: Medium (depends on user backup hygiene).
- **Mitigation**: Users must schedule regular backups of the project folder.

## 4. AI Hallucinations
- **Risk**: Google Gemini response may contain plausible but incorrect legal references or summaries.
- **Impact**: Incorrect decision making if not verified.
- **Likelihood**: Medium (varies by model and prompt complexity).
- **Mitigation**: ALWAYS verify AI output against official court documents.

## 5. Network Eavesdropping
- **Risk**: Traffic is unencrypted (HTTP) by default.
- **Impact**: Sensitive case data intercepted on LAN.
- **Likelihood**: High (on untrusted Wi-Fi).
- **Mitigation**: Use a VPN or SSH tunnel when accessing remotely.
