# Orchestration Agent (`orchestration_agent`)

## Purpose
The **Orchestration Agent** is the single routing authority across the Claims Adjudication Platform. It evaluates claim complexity, detects cross-agent evidence conflicts, assesses escalation requirements, and decides which worker agent runs next at every step.

> **Architecture Rule**: The Orchestration Agent is the only agent with authority to route between agents. All other agents are workers that report back to it.

## Shared Graph State Slice
- **Reads**: `claim_id`, `claimed_amount`, `complexity_score`, `coverage_status`, `code_mismatches`, `exclusion_triggers`, `human_review_required`, `last_completed_agent`, `agent_outputs_so_far`.
- **Writes**: `next_agent`, `workflow_path`, `escalation_required`, `escalation_reason`, `workflow_reasoning`, `status`.

## Owned Tools
- `evaluate_claim_complexity`: Evaluates monetary amount and clinical code count against complexity thresholds.
- `detect_conflict`: Detects contradictions between policy coverage terms and medical billing codes.
- `assess_escalation_need`: Determines if high dollar limits or high complexity trigger human review.
- `determine_next_agent`: Selects the single authoritative next worker agent in the graph sequence.

## Example Routing Trace
```
1. Workflow Initialized -> routed to Intake Agent.
2. Intake Agent completed -> routed to Policy Interpretation Agent.
3. Policy Interpretation Agent completed -> routed to Medical Billing Agent.
4. Medical Billing audit completed -> routed to Precedent Agent.
5. Precedent Agent completed: Policy Agent and Medical Agent outputs conflicted -> routed to Debate Agent.
6. Debate Agent resolved conflict -> routed to Decision Drafting Agent.
7. Decision Drafting Agent completed -> routed to Compliance Guardrail Agent.
8. Compliance Guardrail Agent flagged escalation requirement ($7,500 >= $5,000) -> routed to Human Review Interrupt.
```
