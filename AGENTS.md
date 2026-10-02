# InsureTrust Agent Guide

## Stack
- Backend: Python 3.13+; FastAPI, LangGraph, LangChain tool wrappers, SQLAlchemy, SQLite by default.
- Frontend: React 19, React Router 7, Vite 8, Tailwind 4; npm scripts are in `Frontend/package.json`.
- Backend dependencies are in `Backend/requirements.txt`; `Backend/pyproject.toml` currently has no dependencies.

## Run
```powershell
cd Backend
.\.venv\Scripts\Activate.ps1
uvicorn api.main:app --reload --port 8000
```
```powershell
cd Frontend
npm run dev
```
API base defaults to `http://127.0.0.1:8000/api/v1`; override with `VITE_API_BASE_URL`. Do not overwrite an existing `Backend/.env`.

## Architecture Rule
**The Orchestration Agent is the sole router.** Workers return state updates to `graph/main_graph.py`, which sends each worker back to orchestration. `determine_next_agent` controls the route; do not add worker-to-worker routing. The graph uses `MemorySaver` and pauses before `human_review_interrupt`.

## Where Things Live
- `Backend/agents/<agent>/`: `agent.yaml`, `graph.py`, `state.py`, `tools.py`, `README.md` plus `__init__.py`.
- `Backend/graph/`: shared state, master graph, checkpointer.
- `Backend/api/routes/`: FastAPI route handlers and schemas under `Backend/schemas/`.
- `Backend/services/`: claim lifecycle, audit writes, log-only notifications.
- `Backend/database/`: SQLAlchemy models, session setup, demo seed.
- `Backend/rag/`: in-memory stores, retrievers, hash-vector fallback and token-overlap reranker.
- `Frontend/src/App.jsx`: routes/guards; `pages/`, `components/`, `auth/`, and `api/clientApi.js` contain UI/API code.

## Adding an Agent
1. Add the five documented files under `Backend/agents/<name>/` (the existing packages also have `__init__.py`).
2. Define shared-state fields and deterministic or model-backed tool behavior explicitly; return only the state patch and set `last_completed_agent`.
3. Register the node and worker-to-orchestrator edge in `Backend/graph/main_graph.py`.
4. Add its actual route to `determine_next_agent` and the conditional edge map. Keep orchestration as the only router.
5. Test the route sequence and persisted status. `agent.yaml` prompts/models are currently not loaded or invoked.

## Top Gotchas
1. No API route validates JWTs or filters claims by claimant/organization. Frontend guards are not authorization.
2. Seed hashes use PBKDF2; login verifies bcrypt. Seeded demo logins fail.
3. `GROQ_API_KEY` is read by chat routes but missing from `Settings`; adding it to `.env` alone does not define `settings.GROQ_API_KEY`.
4. Human resume currently marks `human_review_interrupt` complete and skips the action node; all actions finalize the original draft. Paused submissions also lack DB payout/Decision rows.
5. Auto decisions persist `APPROVE`/`DENY`/`PARTIAL_APPROVE`, but analytics filters other status strings. `getClaims` sends `X-Limit` although backend expects `?limit=`.

See `PROJECT_MEMORY.md` for architecture/state/API details and `PROJECT_ANALYTICS.md` for measured checks, issue evidence, and graph traces.
