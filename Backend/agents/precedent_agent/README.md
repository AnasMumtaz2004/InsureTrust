# Precedent Agent (`precedent_agent`)

## Purpose
The Precedent Agent queries the historical claim database via RAG infrastructure to retrieve past adjudication decisions with matching ICD-10/CPT codes, computing historical approval rates to support consistent decisioning.

## Shared Graph State Slice
- **Reads**: `description`, `diagnosis_codes`, `procedure_codes`.
- **Writes**: `precedent_cases`, `historical_approval_rate`, `precedent_summary`.

## Owned Tools
- `retrieve_similar_precedents`: Invokes `rag/retrievers/precedent_retriever.py`.
- `calculate_historical_approval_rate`: Computes historical approval ratio.

## Known Edge Cases & Limitations
- If no past precedent exists for rare ICD-10 codes, approval rate defaults to neutral 0.50.

## Example Trace
```json
// Input State:
{
  "description": "Physical therapy for low back pain",
  "diagnosis_codes": ["M54.5"]
}

// Node Output:
{
  "historical_approval_rate": 0.67,
  "precedent_summary": "Retrieved 3 precedent cases with 67% historical approval consensus.",
  "precedent_cases": [
    {"precedent_code": "PREC-2025-0892", "decision_outcome": "APPROVED"}
  ]
}
```
