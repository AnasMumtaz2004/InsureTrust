# Claims Adjudication Platform Backend

A production-grade, audit-ready Multi-Agent Claims Adjudication Platform backend built with **Python**, **FastAPI**, **LangChain**, and **LangGraph**.

---

## Centralized Routing Architecture

> **CORE ARCHITECTURE MANDATE**:
> **The Orchestration Agent is the only agent with authority to route between agents. All other agents are workers that report back to it.**

The system features **8 dedicated autonomous sub-agents** wired together in a thin master LangGraph composition orchestrator (`graph/main_graph.py`). All routing, complexity assessment, conflict detection, and escalation decisions are centrally governed by the **Orchestration Agent** (`agents/orchestration_agent/`).

```
                          ┌───────────────────────────┐
                          │    Orchestration Agent    │ ◄─── Workers Report Back
                          │ (Single Routing Authority)│
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────────────┼───────────────────────────┐
           ▼                            ▼                           ▼
   ┌───────────────┐           ┌──────────────────┐        ┌────────────────┐
   │ Intake Agent  │           │ Policy Interp.   │        │ Medical/Billing│
   └───────┬───────┘           └────────┬─────────┘        └───────┬────────┘
           │                            │                          │
           └────────────────────────────┼──────────────────────────┘
                                        ▼
                                ┌───────────────┐
                                │Precedent Agent│
                                └───────┬───────┘
                                        ▼
                             (Conflict Detected?)
                              /                \
                             YES                NO
                            /                     \
             ┌─────────────────────┐       ┌────────────────────┐
             │    Debate Agent     │       │ Decision Drafting  │
             └──────────┬──────────┘       └─────────┬──────────┘
                        └────────────────────────────┤
                                                     ▼
                                           ┌──────────────────┐
                                           │Compliance Guard. │
                                           └─────────┬────────┘
                                                     ▼
                                      (Escalation / Human Review?)
                                       /                        \
                                     YES                         NO
                                     /                             \
                       [PAUSE FOR HUMAN ADJUDICATOR]      [FINALIZE DECISION]
```

---

## Project Structure (All 8 Agents)

```
backend/
├── agents/
│   ├── orchestration_agent/           # Agent 8 — SINGLE ROUTING AUTHORITY (evaluates complexity, conflicts, escalation)
│   │   ├── agent.yaml                 # Config: thresholds, escalation rules, eligible next steps, past-tense reasoning
│   │   ├── graph.py                   # Subgraph node & authoritative route_next_agent routing logic
│   │   ├── state.py                   # Pydantic state slice (reads complexity/conflicts, writes next_agent)
│   │   ├── tools.py                   # evaluate_complexity, detect_conflict, assess_escalation, determine_next
│   │   └── README.md                  # Routing authority documentation and trace
│   │
│   ├── intake_agent/                  # Agent 1 — validates claim completeness and severity index
│   ├── policy_interpretation_agent/    # Agent 2 — extracts and interprets relevant policy clauses
│   ├── medical_billing_agent/          # Agent 3 — audits CPT/ICD coding and fee schedules
│   ├── precedent_agent/                # Agent 4 — retrieves historical claim precedents (RAG)
│   ├── debate_agent/                   # Agent 5 — pro/con adversarial debate + reconciliation
│   ├── decision_drafting_agent/         # Agent 6 — synthesizes final recommendations & citations
│   └── compliance_guardrail_agent/      # Agent 7 — checks statutory mandates & human review thresholds
│
├── graph/
│   ├── main_graph.py                   # Thin composition StateGraph wiring all 8 subgraphs (NO inline routing decisions)
│   ├── shared_state.py                 # Global ClaimAdjudicationState schema shared across graph
│   └── checkpoints.py                  # LangGraph checkpointer config for thread state & interrupts
│
├── rag/
│   ├── ingestion/                      # Policy & Precedent chunkers and embedding wrappers
│   ├── vectorstore/                    # Policy and Precedent vector store clients
│   ├── retrievers/                     # LangChain policy and precedent retriever wrappers
│   ├── reranker.py                     # Post-retrieval cross-encoder reranking
│   └── README.md                       # RAG pipeline overview
│
├── api/
│   ├── main.py                         # FastAPI application entrypoint
│   └── routes/                         # Claims, Documents, Explanation, Operations, Auth, Analytics
│
├── database/
│   ├── database.py                     # SQLAlchemy engine and session factory
│   └── models.py                       # Claim, Policy, Document, Decision, Debate, Audit ORM models
│
├── schemas/                            # Pydantic request/response schemas per route
├── services/                           # Claim business logic, Notification, and Audit services
├── prompts/shared/                     # Shared legal disclaimers and insurance glossary
├── utils/                              # Structured logger and PII masking utilities
├── config.py                           # Application configuration settings
└── requirements.txt
```

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.10+ installed

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch FastAPI Dev Server
```bash
uvicorn api.main:app --reload --port 8000
```
Access interactive OpenAPI documentation at: `http://localhost:8000/docs`

---

## How to Add a New Agent (5-File Standard Template)

Each agent in the system MUST strictly follow the per-agent 5-file folder structure inside `agents/<new_agent_name>/`:

```
agents/<new_agent_name>/
├── agent.yaml        # Full agent config: name, role description, LLM model + temperature,
│                     # system prompt, task-specific prompt templates, allowed tools list,
│                     # schema references, retry/timeout config, few-shot examples.
├── graph.py          # LangGraph subgraph/node function — how it executes, updates state,
│                     # and returns its output slice into shared state.
├── state.py           # Pydantic model(s) for this agent's slice of shared graph state.
├── tools.py          # LangChain tool functions this agent calls (implementation + @tool decorator).
└── README.md         # Human-readable doc: purpose, inputs/outputs, tools owned, edge cases,
                      # and an example run trace.
```

### Step-by-Step Instructions:

1. **Create the Folder**:
   `mkdir -p agents/fraud_detection_agent`

2. **Add `agent.yaml`**:
   Specify LLM prompts, model settings, and tool list. **Never hardcode prompts in code.**

3. **Add `state.py`**:
   Define `FraudState(BaseModel)` declaring what fields this agent reads and writes.

4. **Add `tools.py`**:
   Define `@tool` decorated functions used by this agent. If RAG is required, wrap the appropriate retriever from `rag/retrievers/`.

5. **Add `graph.py`**:
   Implement `fraud_detection_node(state: Dict[str, Any]) -> Dict[str, Any]` that calls tools, tags `"last_completed_agent": "fraud_detection_agent"`, and returns updated keys.

6. **Add `README.md`**:
   Document purpose, inputs, outputs, owned tools, and an example run trace snippet.

7. **Wire into `graph/main_graph.py` & `orchestration_agent`**:
   Register node in `graph/main_graph.py`, add edge back to `orchestration_agent`, and update `agents/orchestration_agent/agent.yaml` and `tools.py` to add the new worker as an eligible next step.

---

## API Quick Reference

- **POST `/api/v1/claims/submit`**: Submit a new claim for adjudication.
- **GET `/api/v1/claims/{claim_id}`**: Retrieve full claim details & state.
- **GET `/api/v1/ops/cases/queue`**: Back-office queue of pending/paused claims.
- **POST `/api/v1/ops/decisions/{claim_id}/approve`**: Approve paused human-in-the-loop claim.
- **POST `/api/v1/ops/decisions/{claim_id}/override`**: Override claim decision with modified payout.
- **GET `/api/v1/explanation/{claim_id}`**: Claimant-facing explanation.
- **POST `/api/v1/explanation/chat`**: Interactive Q&A chat about claim decision.
- **GET `/api/v1/analytics/kpis`**: Platform operation metrics & audit rates.
