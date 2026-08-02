from typing import List, Dict, Any

class PrecedentCaseLoader:
    """Loads and chunks historical adjudicated claim records for precedent-based RAG matching."""

    def load_precedent_records(self, raw_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for case in raw_cases:
            precedent_id = case.get("precedent_code", f"PREC-{case.get('id', '001')}")
            content = (
                f"Precedent Case Code: {precedent_id}\n"
                f"Diagnosis Code: {case.get('diagnosis_code', 'N/A')}\n"
                f"Procedure Code: {case.get('procedure_code', 'N/A')}\n"
                f"Outcome: {case.get('decision_outcome', 'DENIED')}\n"
                f"Summary: {case.get('summary', '')}"
            )

            chunks.append({
                "id": precedent_id,
                "precedent_code": precedent_id,
                "content": content,
                "metadata": {
                    "diagnosis_code": case.get("diagnosis_code"),
                    "procedure_code": case.get("procedure_code"),
                    "decision_outcome": case.get("decision_outcome")
                }
            })
        return chunks
