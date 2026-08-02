# Intake & Classification Agent (`intake_agent`)

## Purpose
The Intake & Classification Agent serves as the gateway node for incoming insurance claims. It validates field completeness, calculates a multi-factorial complexity score (1.0 - 10.0), and routes simple vs. complex claims through conditional graph branches.

## Shared Graph State Slice
- **Reads**: `claim_id`, `policy_number`, `claimed_amount`, `diagnosis_codes`, `procedure_codes`, `description`.
- **Writes**: `is_complete`, `missing_fields`, `complexity_score`, `is_complex`, `status`.

## Owned Tools
- `validate_claim_fields`: Verifies presence of essential claim fields.
- `calculate_severity_score`: Computes severity based on financial amount and code count.

## Known Edge Cases & Limitations
- If `claimed_amount` is missing or negative, defaults complexity score to high (10.0) and flags field as missing.
- Does not validate OCR quality of raw PDF uploads directly; delegates doc parsing status to `documents.py` service.

## Example Trace
```json
// Input State:
{
  "claim_id": "CLM-88210",
  "claimed_amount": 6200.00,
  "diagnosis_codes": ["M54.5", "S39.011A"],
  "procedure_codes": ["99214"]
}

// Node Output:
{
  "is_complete": true,
  "missing_fields": [],
  "complexity_score": 7.4,
  "is_complex": true,
  "status": "INTAKE_CLASSIFIED"
}
```
