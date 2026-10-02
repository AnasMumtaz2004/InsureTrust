from schemas.claims import ClaimIntakeExtractedFields, ClaimIntakeStructuredResponse


def _customer_token(client):
    response = client.post(
        "/api/v1/auth/login/customer",
        json={"email": "customer@insuretrust.com", "password": "customer123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_intake_chat_extracts_fields_with_structured_llm(client, monkeypatch):
    from services import llm_service

    class StructuredModel:
        def invoke(self, prompt):
            assert "POL-HE-2023-001" in prompt
            return ClaimIntakeStructuredResponse(
                reply="What date did the incident happen?",
                extracted_fields=ClaimIntakeExtractedFields(
                    policy_number="POL-HE-2023-001",
                    claimed_amount=1250.0,
                    description="Medical treatment after a fall",
                    diagnosis_codes=["M54.5"],
                ),
            )

    class MockLLM:
        def with_structured_output(self, schema):
            assert schema is ClaimIntakeStructuredResponse
            return StructuredModel()

    monkeypatch.setattr(llm_service, "get_chat_llm", lambda: MockLLM())
    response = client.post(
        "/api/v1/claims/intake-chat",
        json={"conversation": [{"role": "user", "content": "Policy POL-HE-2023-001; $1250 for treatment after a fall"}]},
        headers={"Authorization": f"Bearer {_customer_token(client)}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "reply": "What date did the incident happen?",
        "extracted_fields": {
            "policy_number": "POL-HE-2023-001",
            "claimed_amount": 1250.0,
            "description": "Medical treatment after a fall",
            "diagnosis_codes": ["M54.5"],
        },
        "missing_fields": ["incident_date"],
    }


def test_intake_chat_falls_back_when_llm_unavailable(client, monkeypatch):
    from services import llm_service

    def unavailable_llm():
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(llm_service, "get_chat_llm", unavailable_llm)
    response = client.post(
        "/api/v1/claims/intake-chat",
        json={"conversation": [{"role": "user", "content": "I need to file a claim"}]},
        headers={"Authorization": f"Bearer {_customer_token(client)}"},
    )

    assert response.status_code == 200
    assert response.json()["extracted_fields"] == {}
    assert response.json()["missing_fields"] == [
        "policy_number", "incident_date", "claimed_amount", "description"
    ]
    assert response.json()["reply"]