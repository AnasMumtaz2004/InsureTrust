# InsureTrust Repository Analytics

Audit date: 2026-10-02. Source of truth is executable code, not READMEs or `agent.yaml`. No source files were edited. Existing worktree state before documentation edits: `Backend/requirements.txt` modified and `Backend/uv.lock` untracked; these were preserved. The local `.env` was inspected by key names only; values are not reproduced. Counts below are a baseline snapshot taken before adding the three deliverable Markdown files.

## Size and Composition

No `cloc` or `tokei` executable was installed. Numbers below come from a read-only Python recursive walk, excluding `.git/`, `.venv/`, `node_modules/`, `dist/`, `build/`, and `__pycache__/`. It found 165 files: 163 UTF-8 text files included in the LOC pass, one `.env` excluded from LOC, and one binary `Frontend/src/assets/hero.png` excluded from LOC. LOC is physical lines. Comment classification counts full-line `#`, `//`, `/*`, `*`, `<!--`, or `-->` starts for applicable source extensions; inline comments and comments in data/docs are not parsed. For JSON, Markdown, YAML, and similar non-code formats, the `content`/code column means nonblank non-comment lines, not executable LOC. This is a transparent fallback estimate, not a language-aware cloc result.

| Language / format | Files | Content/code lines | Comment lines | Blank lines | Total physical lines |
|---|---:|---:|---:|---:|---:|
| Python | 78 | 2,058 | 78 | 349 | 2,485 |
| JSX | 42 | 2,428 | 12 | 255 | 2,695 |
| JavaScript | 8 | 185 | 20 | 44 | 249 |
| CSS | 2 | 60 | 4 | 13 | 77 |
| HTML | 1 | 17 | 0 | 0 | 17 |
| JSON | 2 | 3,438 | 0 | 0 | 3,438 |
| YAML | 8 | 255 | 0 | 7 | 262 |
| Markdown | 11 | 410 | 0 | 90 | 500 |
| SVG | 4 | 27 | 0 | 0 | 27 |
| TOML | 1 | 7 | 0 | 0 | 7 |
| Lock | 1 | 7 | 0 | 1 | 8 |
| Text | 1 | 18 | 0 | 0 | 18 |
| Env example | 1 | 19 | 0 | 4 | 23 |
| Gitignore / other text | 3 | 70 | 0 | 12 | 82 |
| **Total text files** | **163** | **8,999** | **114** | **775** | **9,888** |

| Top-level folder | Text files | Content/code lines | Comment lines | Blank lines | Physical lines |
|---|---:|---:|---:|---:|---:|
| `Backend/` | 101 | 2,766 | 78 | 444 | 3,288 |
| `Frontend/` | 61 | 6,186 | 36 | 321 | 6,543 |
| Root | 1 | 47 | 0 | 10 | 57 |

Top 15 largest text files by physical line count:

| Lines | File |
|---:|---|
| 3,406 | `Frontend/package-lock.json` |
| 217 | `Frontend/src/components/client/ClaimDrawer.jsx` |
| 190 | `Frontend/src/pages/CaseWorkspacePage.jsx` |
| 179 | `Backend/README.md` |
| 147 | `Backend/services/claim_service.py` |
| 137 | `Frontend/src/pages/OpsQueuePage.jsx` |
| 135 | `Backend/database/models.py` |
| 128 | `Frontend/src/pages/StaffLoginPage.jsx` |
| 127 | `Frontend/src/pages/AiAssistantPage.jsx` |
| 119 | `Frontend/src/pages/UserLoginPage.jsx` |
| 116 | `Frontend/src/pages/LandingPage.jsx` |
| 106 | `Backend/api/routes/claims.py` |
| 103 | `Frontend/src/components/ops/ClaimsTable.jsx` |
| 100 | `Backend/api/routes/explanation.py` |
| 98 | `Backend/graph/main_graph.py` |

Structural counts, from AST/source tree: 8 agent directories; 19 `@tool` functions; 20 API router endpoints plus the root health endpoint (21 decorated handlers total); 10 SQLAlchemy ORM classes; 7 React route pages; 24 React component files under `components/{client,ops,shared}` (barrel files excluded). Test discovery: 0 test files and 0 `test_*` Python functions. Coverage estimate: none; there are no tests/coverage data.

## Dependencies and Versions

### Backend

Declared minimums in [Backend/requirements.txt](Backend/requirements.txt): `fastapi>=0.109.0`, `uvicorn[standard]>=0.27.0`, `pydantic>=2.6.0`, `pydantic-settings>=2.1.0`, `langchain>=0.1.0`, `langchain-community>=0.0.20`, `langchain-core>=0.1.20`, `langgraph>=0.0.26`, `pyyaml>=6.0.1`, `sqlalchemy>=2.0.25`, `python-jose[cryptography]>=3.3.0`, `passlib[bcrypt]>=1.7.4`, `python-multipart>=0.0.6`, `python-dotenv>=1.0.0`, `faiss-cpu>=1.7.4`, `pytest>=8.0.0`, `email-validator>=2.0.0`, and unpinned `langchain-groq`. The last line is a pre-existing user modification in this worktree; the original committed dependency state was not audited here.

Backend source imports observed through Pylance: `fastapi`, `pydantic`, `pydantic_settings`, `langchain_core`, `langchain_community`, `langgraph`, `yaml`, `sqlalchemy`, `jose`, `passlib`, and `langchain_groq`; all resolved under the selected workspace interpreter. Therefore the seed issue “langchain-groq missing from requirements” is **false for the current working copy**, but `GROQ_API_KEY` is still not declared in Settings. The `pyproject.toml` declares `dependencies = []`, so it does not express those runtime dependencies.

Declared but not imported directly by application source: `faiss-cpu`, `pytest`, `email-validator`, and `langchain`. `uvicorn` is used as a CLI command rather than imported. `python-dotenv` is a settings/runtime support dependency and may be loaded by pydantic-settings rather than direct application import. Agent Pydantic state modules import a number of unused symbols; AST name-use heuristic found 28 candidate unused Python imports across the backend, including `config.os`, `database.database.uuid`, `schemas.documents.Field/Optional`, `api.routes.documents.validate_claim_fields`, and numerous `Field`/typing imports in unused agent-state models. This is a heuristic, not a Pylance unused-import diagnostic.

### Frontend

`npm list --depth=0` in `Frontend/` resolved: React/react-dom 19.2.8, React Router 7.18.2, Vite 8.2.0, Tailwind 4.3.3, `@tailwindcss/vite` 4.3.3, lucide-react 1.28.0, Recharts 3.10.1, `@vitejs/plugin-react` 6.0.5, ESLint 10.8.0, and associated ESLint plugins/config. Application imports match declared packages: `react`, `react-dom`, `react-router-dom`, `lucide-react`, `recharts`, Vite plugins, ESLint configuration modules, and Tailwind CSS. `@types/react` / `@types/react-dom` are declared despite the app being JS/JSX, with no `.ts`/`.tsx` source observed.

### Python version reconciliation

| Source | Declared version |
|---|---|
| `Backend/.python-version` | `3.13` |
| `Backend/pyproject.toml` | `>=3.13` |
| `Backend/README.md` | Python `3.10+` at line 107 |
| Runtime observed | Python 3.14.3 |

README conflicts with project pin/constraint. `requirements.txt` itself has no Python constraint. `Frontend/package.json` declares package versions but no Node engine. Audit runtime: Node 24.8.0, npm 11.6.0.

## Code Quality and Dead Code

- `npm run lint` exits 1 with two findings: `Frontend/src/pages/AiAssistantPage.jsx:69` undefined `Shield`; `Frontend/src/auth/AuthContext.jsx:75` `react-refresh/only-export-components` because it exports hook and component from one module.
- `npm run build` exits 0 (`vite v8.2.0`, 2,409 modules transformed). The missing `Shield` remains a runtime render error that bundling does not detect.
- TODO/FIXME/HACK scan across backend/frontend text source: 0 occurrences.
- Python AST: four functions longer than 50 lines: `ClaimService.submit_and_process_claim` (92), `seed_demo_data` (56), `decision_drafting_node` (55), `create_claims_adjudication_graph` (52). Espree JSX scan: 16 functions/components >50 physical lines: UserLoginPage (110), AiAssistantPage (112), StaffLoginPage (119), OpsQueuePage (121), CaseWorkspacePage (173), ClaimDrawer (205), ShieldIllustration (53), ClientSidebar (53), PublicLayout (55), AuthProvider (59), RecommendationCard (65), DecisionActionBar (68), OpsSidebar (69), DashboardPage (82), LandingPage (96), ClaimsTable (97). Function line spans include JSX body/returned markup.
- Nesting estimates count structural control nodes, not JSX nesting. Python maximum was 9 at `agents/orchestration_agent/tools.py` (the function's sequential `if/elif` chain contributes); next was `utils/pii_masking.py` at 6. Frontend maximum was 3 at `components/ops/ClaimsTable.jsx`.
- Candidate dead React component modules: `ActivityItem.jsx`, `PolicyCard.jsx`, `DonutChart.jsx`, `Modal.jsx` (each only self/barrel references, not imported by a page). Candidate unused assets: `hero.png`, `src/assets/react.svg`, `src/assets/vite.svg`, and `public/icons.svg`. `App.css` is empty and not imported.
- `Frontend/src/auth/clientApi.js` and `opsApi.js` are unused legacy modules and target nonexistent `/api/client` and `/api/ops`. Active module is `Frontend/src/api/clientApi.js`.
- Active-but-unused API exports: `submitClaim`, `getClaimExplanation`, `postClaimExplanationQuestion`, `getOpsClaimDetail`; no page calls them. `getOpsClaimDetail` has a corresponding backend route but the CaseWorkspace uses `getClaimById` instead.
- Backend items not wired: `get_agent_config`; all `agent.yaml` files; all eight agent-specific Pydantic `state.py` classes; `PolicyDocumentLoader` and `PrecedentCaseLoader`; `LEGAL_DISCLAIMER_HEADER`, `CLAIMANT_EXPLANATION_DISCLAIMER`, `STANDARD_INSURANCE_GLOSSARY`; configured vector-store paths and default LLM model; `NotificationService.send_decision_letter`; `Policy` and `PrecedentRecord` data are not used by graph retrieval. Root `Backend/main.py` is a separate unused hello-world entrypoint.

## Hardcoded Values

- Business thresholds in Settings: `$5,000` amount and complexity `7.0`; orchestration YAML instead declares $5,000 simple cap, $10,000 high-value escalation, conflict delta 0.20. Only Settings thresholds are used.
- Intake severity: base 1; >$10,000 +4, else >$3,000 +2; diagnosis +0.8 each capped +3; procedure +0.7 each capped +3; total max10.
- Billing: four fixed CPT rates ($180/$75/$850/$65); unknown code $150; no-code estimate 80% claimed; specific 93000/S39.011A/R07.9 rule; duplicates flagged.
- Default policy clauses and three precedent samples embedded in the two vector stores. Hash vectors repeat 64 hex-derived values to dimension 1536 or 384.
- Debate score coefficients .40/.15/.10 and .95 cap; no-mismatch branch APPROVE. Payout has no deductible.
- Human review for amount >= $5,000, complexity >= 7, or DENY; decision rationale text check searches `right to request`.
- JWT defaults to known `super-secret-key-change-this-in-production`, `HS256`, 60-minute expiry. `.env.example` repeats placeholder key.
- Chat model `llama-3.1-8b-instant`, temperature .2; default Settings LLM name `gpt-4o` is not used by agents.
- UI static adjusters, fake assistant intake, mock reasoning/debate transcript, status/claim copy, and `/api/v1` local base URL. CORS origin `*`; processing time KPI fixed at 2.4 seconds.
- Seed demo identities/passwords documented in [PROJECT_MEMORY.md](PROJECT_MEMORY.md#11-how-to-run); their hashes do not verify under current login context.

## Integration Consistency: Frontend to Backend

The active API module uses base `/api/v1`. Each call is listed below; request mismatch and non-use are explicit. Backend route files: [auth](Backend/api/routes/auth.py), [claims](Backend/api/routes/claims.py), [documents](Backend/api/routes/documents.py), [explanation](Backend/api/routes/explanation.py), [ops cases](Backend/api/routes/ops_cases.py), [ops decisions](Backend/api/routes/ops_decisions.py), [analytics](Backend/api/routes/analytics.py).

| Frontend API function | Backend match | Use / mismatch |
|---|---|---|
| `loginCustomer(email,password)` | `POST /auth/login/customer` | called from AuthContext |
| `loginStaff(email,password)` | `POST /auth/login/staff` | called; org_id supplied by StaffLogin is dropped by AuthContext |
| `getClaims(token,limit)` | `GET /claims?limit=` | Dashboard/Assistant call; sends `X-Limit` header instead of query parameter |
| `getClaimById(id,token)` | `GET /claims/{id}` | CaseWorkspace calls this general claims endpoint; no owner/auth filter |
| `submitClaim(payload,token)` | `POST /claims/submit` | not called by pages |
| `postClaimChat(id,message,token)` | `POST /claims/{id}/chat` | Assistant calls |
| `getClaimExplanation(id,token)` | `GET /explanation/{id}` | not called |
| `postClaimExplanationQuestion(id,question,token)` | `POST /explanation/chat` | not called |
| `getOpsClaims(token)` | `GET /ops/cases/queue` | OpsQueue calls |
| `getOpsClaimDetail(id,token)` | `GET /ops/cases/{id}/graph-state` | not called |
| `getOpsAnalytics(token)` | `GET /analytics/kpis` | OpsQueue calls |
| `getAuditLogs(token)` | `GET /analytics/audit-logs` | OpsQueue calls |
| legacy `clientApi` family | `/api/client/*` | no matching backend prefix, module unused |
| legacy `opsApi` family | `/api/ops/*` | no matching backend prefix, module unused |

Backend endpoints not called by current pages (12):

- `POST /auth/register`.
- `POST /claims/submit`.
- `POST /documents/upload`, `POST /documents/check-completeness`.
- `GET /explanation/{claim_id}`, `POST /explanation/chat`.
- `GET /ops/cases/{claim_id}/graph-state`, `/debate-transcript`, `/audit-trail`.
- `POST /ops/decisions/{claim_id}/action`, `/approve`, `/override`.

All router endpoints are unmatched by server-side authentication. Token headers from frontend are not validated by route code. UI routes are only local guards.

### Status strings written vs filtered

| Source | Values |
|---|---|
| Claim model comment | `SUBMITTED`, `IN_REVIEW`, `DEBATING`, `PENDING_APPROVAL`, `APPROVED`, `DENIED`, `OVERRIDDEN` |
| ClaimService submit DB write | starts `IN_REVIEW`; review-needed -> `PENDING_APPROVAL`; automatic -> raw `APPROVE`, `DENY`, or `PARTIAL_APPROVE` |
| ClaimService resume DB write | `APPROVED` for APPROVE; `OVERRIDDEN` for OVERRIDE **and SEND_BACK** |
| Graph statuses | `COMPLETED_APPROVE`, `COMPLETED_DENY`, `COMPLETED_PARTIAL_APPROVE`, plus intermediate and pause statuses |
| Analytics approve query | `APPROVED`, `COMPLETED_APPROVE` |
| Analytics deny query | `DENIED`, `COMPLETED_DENY` |
| Analytics pending query | `PENDING_APPROVAL`, `PAUSED_FOR_HUMAN_REVIEW`, `IN_REVIEW` |
| Ops queue query | `PENDING_APPROVAL`, `PAUSED_FOR_HUMAN_REVIEW`, `IN_REVIEW`, `DEBATING` |

Analytics therefore misses auto-persisted `APPROVE`, `DENY`, `PARTIAL_APPROVE` and partial-completion status; graph `COMPLETED_*` statuses are not written to the Claim row by submit path.

### Role string consistency

- ORM `User.role` default/comment: `claimant`; comment lists `claimant`, `adjudicator`, `admin`.
- `UserRegisterRequest.role` default/comment: `claimant`, `adjudicator`, `admin`; route accepts caller-supplied string without allow-list.
- Seed roles: `customer`, `staff`.
- Auth routes: customer login requires `customer`; staff login accepts `staff` or `admin`.
- Frontend guards/login: `customer`, `staff`, `admin`.
- `claimant` and `adjudicator` are not accepted by login routes; seeded roles and guards diverge from model/schema comments. Registration can self-assign `admin`, though backend route protection is absent entirely.

## Security Review

- **Critical:** no JWT validation dependency in routes and no `claimant_id` filtering in `GET /claims`; `GET /claims/{id}`, chat, explanations, documents, graph state, audit, and ops actions are callable without authentication. User-supplied IDs can target other claims. JWT is created but never decoded server-side.
- **Critical:** registration accepts arbitrary roles; `admin` is accepted by staff login. Role selection is not authenticated/authorized.
- **High:** fallback JWT secret is hardcoded in `config.py` and `.env.example`; attacker-known signing key if deployed unchanged.
- **High:** PBKDF2 seed context vs bcrypt login context; isolated test raised `UnknownHashError`.
- **High:** Groq `settings.GROQ_API_KEY` is missing from Settings and `.env.example`. Local `.env` having the key name does not fix Pydantic `extra="ignore"`. Exception is not handled by `except RuntimeError` when access raises `AttributeError`.
- **Medium:** CORS uses wildcard origins, credentials, methods, and headers; restrict for deployment.
- **Medium:** frontend keeps JWT in `localStorage`; client-only decode is not server validation and is exposed to same-origin script compromise.
- **Medium:** PII masking is only applied to AuditService snapshots; ordinary DB claims/chat and outbound user chat are not sanitized. Regex masking is limited to SSN/phone/email/card patterns.
- **Medium/low:** upload handler accepts client filename and records `./uploads/{id}_{filename}` without filename/size/type validation, but it never writes or opens the path or reads file bytes. No current filesystem traversal effect is verified; adding real storage later must canonicalize names and enforce size/type.
- Auth token expiry/algorithm defaults are present, but key rotation, refresh/revocation, issuer/audience checks, and tenant enforcement are absent or UNVERIFIED.

## Reliability

- Checkpoint backend is `MemorySaver`, global singleton in process. Process restart erases thread state; DB rows do not include enough graph state to rebuild. Human resume after restart raises `ValueError` for missing checkpoint.
- Human graph pauses before `human_review_interrupt`; `resume_human_review` calls `update_state(..., as_node="human_review_interrupt")`, causing observed stream to execute `finalize_decision` directly. On test traces, action node did not run for APPROVE/OVERRIDE/SEND_BACK; graph final decision stayed original APPROVE. Service DB status maps non-approve to OVERRIDDEN, creating graph/DB divergence.
- Claim is committed before invoking graph. Graph exceptions are not caught in `submit_and_process_claim`; partial work can leave an `IN_REVIEW` Claim with no completed decision. Some audit write failures are caught/rolled back and swallowed; there is no common error-state contract.
- High-review DB path writes PENDING_APPROVAL but leaves approved_amount default 0 and does not create Decision; resumption writes neither Decision nor normal draft payout. A modified payout only changes `approved_amount`, not the structured final decision/payout record.
- Notification service logs messages only; no network delivery, retry, or queue.
- Groq calls in chat handlers catch only RuntimeError during construction; model invocation exceptions are not caught and can produce 500. Chat messages are committed only after generation, so invocation failure loses the user message.
- Document completeness endpoint does not parse documents; upload never stores bytes. No asynchronous processing/notification integration is present.

## Agent System Analysis

### Deterministic vs LLM; empty/wrong inputs

| Agent | Runtime | Inputs / timing issues |
|---|---|---|
| Orchestration | Python `@tool` rules | First invocation gets empty previous-agent fields, amount default 0 and score 0; safe initial route depends on START. It reads `agent_outputs_so_far` only in YAML, not graph code. `is_complex` does not route. Writes undeclared `conflict_flags`. |
| Intake | deterministic required-field + score tools | Required-field check uses truthiness; amount zero counts missing. Claim schema requires diagnosis? no; empty diagnoses/procedures accepted. Completeness result does not stop/escalate flow. |
| Policy | deterministic retriever and title substring | Ignores policy number and procedures; diagnosis argument to exclusion tool unused; samples not tied to submitted policy. Default HEALTH exclusion title can create false conflict. |
| Medical/Billing | deterministic lookup/rule table | Empty procedures fall back to 80% estimate; unknown CPT gets $150; no documents parsed despite YAML/README language. |
| Precedent | deterministic in-memory retrieval | Empty diagnoses means no exact code; default examples remain source; neutral .5 only when no records. ORM precedent records are not consulted. |
| Debate | deterministic list construction/scoring | Runs for any conflict, including broad exclusion title. No-mismatch branch always recommends APPROVE, even when con arguments only contain exclusions or unusual charges. |
| Drafting | deterministic branch and calculator | Usually receives fields, but `allowed_total=0` permits full claimed payout for APPROVE. Any non-DENY/non-APPROVE string falls through to payout=`allowed_total`; rationale does not include statutory appeal text. |
| Compliance | deterministic string and thresholds | DENY/PARTIAL_APPROVE will set compliance flag on generated rationale because appeal phrase absent; flag does not itself set human review except DENY threshold. High amount/complexity triggers pause. |

No worker uses `ChatGroq`, OpenAI chat, or model invocation. Actual Groq is in API chat handlers only. Agent YAML `llm_model`, temperature, prompt templates, allowed tools, retry, and schema fields are not executed. `config.get_agent_config` is unused.

### Graph scenario traces

Executed actual `claims_graph.stream` from `.venv` with `OPENAI_API_KEY` blank to prevent external embedding calls. Each stream sequence below includes orchestrator return hops. Default seeded HEALTH clauses caused Debate on the nominally simple scenario too.

1. **Simple $2,000 approval, diagnoses M54.5, CPT 99214**: `orchestration_agent -> intake_agent -> orchestration_agent -> policy_interpretation -> orchestration_agent -> medical_billing -> orchestration_agent -> precedent_agent -> orchestration_agent -> debate_agent -> orchestration_agent -> decision_drafting -> orchestration_agent -> compliance_guardrail -> orchestration_agent -> finalize_decision`. Actual graph status `COMPLETED_APPROVE`; decision `APPROVE`; approved amount `$180`. `ClaimService` would persist DB status `APPROVE`, not `COMPLETED_APPROVE`.
2. **Conflict, $1,200 with S39.011A and 93000**: same path including debate. Mismatch and exclusion conflict route to Debate; recommendation `PARTIAL_APPROVE`; actual graph status `COMPLETED_PARTIAL_APPROVE`, amount `$75`. Service persists raw status `PARTIAL_APPROVE`.
3. **High value, $6,000 with M54.5 and 99214**: runs the same workers through `compliance_guardrail`, then orchestration chooses human node and stream emits `__interrupt__`; snapshot `next=('human_review_interrupt',)`, status `ORCHESTRATED_TO_HUMAN_REVIEW_INTERRUPT`, draft `APPROVE`, graph approved amount `$180`. Service submission persists `PENDING_APPROVAL`, approved_amount remains DB default 0, and no Decision record.

Resume test seeded checkpoint state in memory and applied each action with modified payout `$999`: APPROVE, OVERRIDE, SEND_BACK each resumed `finalize_decision` only, ended graph `COMPLETED_APPROVE` with decision type APPROVE and payout `$999`; no `human_overridden`/override reason was added. Service status would be `APPROVED` for APPROVE and `OVERRIDDEN` for OVERRIDE/SEND_BACK. Thus the implemented review action is not faithfully applied.

### Decision logic edge cases

- Direct `human_review_interrupt_node` OVERRIDE code forces decision type to APPROVE. Actual service resume currently skips the node, so observed graph stays original draft instead; both the node logic and resume route require correction.
- `SEND_BACK` has no node-specific behavior and DB maps it to OVERRIDDEN.
- Paused submission leaves DB payout 0 and creates no Decision row; resume with no modified payout leaves 0 even after approval. Resume does not persist a decision or set human override metadata.
- Debate without code mismatch sets APPROVE regardless of exclusion/con evidence. Policy exclusion status routes to debate rather than deny; then mismatch-free branch approves.
- Decision Drafting uses strict `len(mismatches) > 1` for denial unless a debate recommendation exists. Single mismatch may partial approve if Debate returns partial; coverage `EXCLUDED` can be superseded by reconciliation recommendation.
- `allowed_total <= 0` on APPROVE means pay claimed amount, so missing/zero fee computation is not conservative.
- `conflict_flags` state is not declared; `agent_outputs_so_far` not updated; no errors populate `error`.
- Statistical KPI status matching excludes raw `APPROVE` and `PARTIAL_APPROVE`; fixed `average_processing_time_seconds=2.4` is not measured.

## Commands and Validation Results

- `Get-ChildItem` recursive tree: 165 files excluding dependency/build/git directories.
- `cloc`, `tokei`: unavailable; custom Python LOC/AST walk used.
- `npm list --depth=0`: completed; versions above.
- `npm run lint`: failed with two findings described under Code Quality.
- `npm run build`: passed, Vite 8.2.0, 2,409 modules transformed.
- Actual LangGraph simple/conflict/high-value and human action traces: executed; outcomes above.
- Password-context compatibility check: seed PBKDF2 hash verified with bcrypt context raises `UnknownHashError`; `settings` has no `GROQ_API_KEY` attribute.
- Python tests/coverage: none found; not run because no tests are present.

## Verified Issue Triage and First Fixes

Severity counts in this report: **2 critical, 6 high, 9 medium, 4 low (21 findings)**. The complete evidence list is in [PROJECT_MEMORY.md Known Issues](PROJECT_MEMORY.md#13-known-issues).

First five fixes, in order:

1. Enforce JWT validation and claimant/organization ownership on every protected route; prevent public admin role assignment.
2. Replace the default signing secret with required deployment configuration and align seeded-password hashing with auth verification.
3. Fix human-review resume so the actual action node runs; implement distinct APPROVE/OVERRIDE/SEND_BACK outcomes and persist final payout, decision, and override metadata atomically.
4. Declare/validate `GROQ_API_KEY` and catch both initialization and invocation failures with an explicit fallback/error contract.
5. Normalize status transitions and analytics/queue filters; add regression tests for DB status, KPI counts, and graph persistence.
