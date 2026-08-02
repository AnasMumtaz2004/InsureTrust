from typing import List, Dict, Any

class PolicyDocumentLoader:
    """Parses and chunks policy wording documents per product line into structured clause documents."""

    def load_and_chunk_policy(self, raw_text: str, policy_number: str, product_line: str) -> List[Dict[str, Any]]:
        chunks = []
        sections = raw_text.split("\n\nSECTION ")

        for idx, sec in enumerate(sections):
            lines = sec.strip().split("\n")
            title = lines[0] if lines else f"Clause {idx + 1}"
            body = "\n".join(lines[1:]) if len(lines) > 1 else sec

            chunks.append({
                "id": f"{policy_number}_SEC_{idx + 1}",
                "policy_number": policy_number,
                "product_line": product_line,
                "clause_title": title,
                "content": body.strip(),
                "metadata": {
                    "policy_number": policy_number,
                    "product_line": product_line,
                    "section_index": idx + 1
                }
            })
        return chunks
