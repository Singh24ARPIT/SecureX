# SentinelAI – Autonomous AI-Powered Real-Time DAST Platform
### VOYAGEHACK 4.0 | TBO Security Hackathon 2026

**SentinelAI** (SecureX) is a multi-agent cybersecurity platform that continuously monitors API deployments, maps endpoint trees, synthesizes targeted security test vectors, identifies complex business logic flaws (fare manipulation, duplicate refunds, cross-agency IDOR), eliminates false positives with deterministic proof verification, and provides closed-loop regression retesting.

---

## 1. Multi-Agent Architecture

The system coordinates **10 Autonomous Agents**:

| Agent | Name | Primary Responsibility |
|---|---|---|
| **Agent 1** | **Change Detection Agent** | Ingests CI/CD deployment webhooks, analyzes commit diffs, and triggers targeted scans when APIs change. |
| **Agent 2** | **Recon & API Discovery Agent** | Discovers endpoints across `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, maps parameter trees and auth rules. |
| **Agent 3** | **API Inventory Agent** | Classifies endpoints into **Active**, **Zombie** (obsolete reachable routes), and **Shadow** (undocumented). |
| **Agent 4** | **Attack Planning Agent** | Semantically selects targeted tests (e.g. IDOR for booking retrieval, business logic for payments/refunds). |
| **Agent 5** | **Security Testing Suite** | Specialized testers for **Access Control (IDOR)**, **Business Logic (Fare/Refund)**, **Auth**, **Injection**, and **API Security**. |
| **Agent 6** | **Safety & Policy Agent** | Mandatory gatekeeper enforcing target allowlists, rate limiting (5 RPS), and non-destructive testing boundaries. |
| **Agent 7** | **Vulnerability Verification Agent** | Deterministically rechecks findings against live responses to eliminate false positives and extract minimal proof. |
| **Agent 8** | **Risk & Severity Assessment Agent**| Computes CVSS v3.1 scores, evaluates financial revenue impact and cross-agency data exposure risks. |
| **Agent 9** | **Reporting Agent** | Compiles executive audit reports, remediation roadmaps, and downloadable CSV/JSON exports. |
| **Agent 10** | **Retesting Agent** | Executes automated post-fix verification tests against developer patches to confirm resolution. |

---

## 2. Business Logic & Complex Travel Vulnerabilities Detected

Conventional scanners miss application-specific logic flaws. SentinelAI specifically detects:
1. **Cross-Agency IDOR / BOLA**: Travel Agency 202 accessing bookings and customer itineraries belonging to Agency 101 via parameter reference tampering.
2. **Client-Side Fare Manipulation**: Booking accommodations by submitting manipulated prices ($1.00) rather than server-calculated tariff amounts.
3. **Duplicate Refund Workflow Abuse**: Submitting multiple cancellation refund requests on a single settled booking reference without idempotency locks.
4. **Zombie Legacy API Exposure**: Outdated unauthenticated endpoints leaking passenger PII without rate limiting or governance.
5. **Shadow APIs**: Unregistered internal endpoints discovered via network traffic.

---

## 3. Technology Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, PyJWT, Bcrypt
- **Frontend**: React 18, Vite, Tailwind CSS, Recharts, Lucide Icons, Axios, React Router
- **Database**: SQLite (local zero-config default) with full PostgreSQL production schema compatibility
- **Safety Engine**: Token-bucket rate limiter, scope allowlist verification, health tripwires

---

## 4. Database Schema (15 Production Models)

1. `users` (RBAC: Admin, Security Engineer, Auditor, Agency Admin)
2. `roles` (Permission matrix)
3. `authorized_targets` (Allowlist, rate limits, environment isolation)
4. `api_endpoints` (Paths, methods, classification: Active/Zombie/Shadow, risk scores)
5. `api_parameters` (Parameters in path, query, header, body)
6. `api_inventory_history` (Schema diffs, change logs)
7. `deployment_events` (CI/CD webhook commits, service deploy triggers)
8. `security_scans` (Scan states, execution metadata, stop reasons)
9. `agent_execution_logs` (Live stream of all 10 agents' turns and durations)
10. `vulnerabilities` (Title, category, CVSS, status, business impact)
11. `vulnerability_evidence` (Minimal HTTP request/response dumps, proof)
12. `risk_assessments` (Technical, financial, and cross-agency risk breakdown)
13. `remediation_records` (Developer patch commit details)
14. `retest_history` (Closed-loop post-fix verification logs)
15. `audit_logs` (Compliance audit trail)

---

## 5. Quick Start & Setup

### Automated Single-Command Startup
```bash
./start.sh
```

### Manual Backend Setup
```bash
# 1. Virtual environment & dependencies
python3 -m venv venv
./venv/bin/pip install -r backend/requirements.txt

# 2. Start FastAPI Server
PYTHONPATH=backend ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Manual Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

- **Frontend Console**: [http://localhost:5173](http://localhost:5173)
- **Interactive API Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Pre-Seeded Hackathon Accounts
- **Chief Security Architect**: `admin` / `SentinelAdmin2026!`
- **Security Engineer**: `sec_engineer` / `SecurityEng2026!`
- **Travel Agency 101 User**: `agency1_user` / `AgencyPass2026!`
- **Travel Agency 202 User**: `agency2_user` / `AgencyPass2026!`

---

## 6. Demonstration Scenario Walkthrough (VOYAGEHACK 4.0)

You can demonstrate the entire 11-step hackathon scenario directly from the **Staging App Testbed** tab in the UI:

1. **Deploy New API**: Emits a CI/CD Webhook for `/staging/bookings`.
2. **Change Detection (Agent 1)**: Detects the schema change and triggers testing.
3. **Recon Discovery (Agent 2)**: Discovers endpoints and analyzes parameters.
4. **Inventory Classification (Agent 3)**: Catalogs Active, Zombie, and Shadow routes.
5. **Attack Planning (Agent 4)**: Maps targeted test vectors for booking & refund logic.
6. **Safety Policy (Agent 6)**: Asserts allowlist boundaries and 5 RPS limits.
7. **Security Testing (Agent 5)**: Identifies Cross-Agency IDOR and Fare Manipulation.
8. **Verification (Agent 7)**: Filters false positives and stores minimal HTTP proof.
9. **Risk Assessment (Agent 8)**: Assigns CVSS 9.3 Critical severity and financial loss rating.
10. **Reporting (Agent 9)**: Generates executive reports and CSV/JSON downloads.
11. **Retesting (Agent 10)**: Developer applies patch via live toggle switch -> Agent 10 reruns the test and verifies the issue is resolved with HTTP 403 / 400 assertion.

