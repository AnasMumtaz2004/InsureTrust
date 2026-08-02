# Medical/Billing Document Agent (`medical_billing_agent`)

## Purpose
The Medical/Billing Document Agent audits CPT procedure codes against ICD-10 diagnostic codes, calculates allowed reimbursement amounts per standardized fee schedules, and flags unbundled or clinically unnecessary charges.

## Shared Graph State Slice
- **Reads**: `diagnosis_codes`, `procedure_codes`, `claimed_amount`.
- **Writes**: `medical_findings`, `code_mismatches`, `unusual_charges`, `allowed_total`, `billing_status`.

## Owned Tools
- `validate_cpt_icd_compatibility`: Checks medical necessity compatibility between CPT and ICD-10 codes.
- `calculate_fee_schedule_allowed`: Computes total allowed dollar amount based on fee schedule bounds.
- `detect_unbundling_or_duplicate`: Identifies duplicate procedure submissions or unbundled codes.

## Known Edge Cases & Limitations
- Custom unlisted CPT codes (e.g. 99499) fall back to an 80% default allowance estimate.

## Example Trace
```json
// Input State:
{
  "diagnosis_codes": ["S39.011A"],
  "procedure_codes": ["93000"],
  "claimed_amount": 250.00
}

// Node Output:
{
  "billing_status": "MISMATCH_FLAGGED",
  "code_mismatches": [
    "CPT 93000 (Electrocardiogram) lacks medical necessity for diagnosis S39.011A (Lumbar strain)..."
  ],
  "allowed_total": 75.00
}
```
