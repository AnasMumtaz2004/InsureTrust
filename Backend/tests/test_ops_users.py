import uuid

from database.database import SessionLocal
from database.models import Claim, Decision


def _token(client, path, email, password):
    response = client.post(path, json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_ops_users_lists_staff_with_distinct_claim_action_counts(client):
    staff_token = _token(
        client,
        "/api/v1/auth/login/staff",
        "staff@insuretrust.com",
        "staff123",
    )
    headers = {"Authorization": f"Bearer {staff_token}"}
    before_response = client.get("/api/v1/ops/users", headers=headers)
    assert before_response.status_code == 200
    before_count = next(user["claims_acted_on"] for user in before_response.json() if user["id"] == "USR-STAFF")

    claim_id = f"CLM-OPS-{uuid.uuid4().hex[:8].upper()}"
    db = SessionLocal()
    try:
        db.add(Claim(
            id=claim_id,
            claim_number=f"CN-OPS-{uuid.uuid4().hex[:8].upper()}",
            claimant_id="USR-CUSTOMER",
            policy_number="POL-OPS-TEST",
            status="IN_REVIEW",
            total_claimed_amount=100,
        ))
        db.flush()
        db.add(Decision(
            id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            claim_id=claim_id,
            decision_type="APPROVE",
            rationale="Test action count",
            approved_by="USR-STAFF",
        ))
        db.add(Decision(
            id=f"DEC-{uuid.uuid4().hex[:8].upper()}",
            claim_id=claim_id,
            decision_type="APPROVE",
            rationale="Second action on the same claim",
            approved_by="USR-STAFF",
        ))
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/ops/users", headers=headers)

    assert response.status_code == 200
    staff = next(user for user in response.json() if user["id"] == "USR-STAFF")
    assert staff["claims_acted_on"] == before_count + 1
    assert all(user["role"] in {"staff", "admin"} for user in response.json())


def test_ops_users_requires_staff_or_admin(client):
    customer_token = _token(
        client,
        "/api/v1/auth/login/customer",
        "customer@insuretrust.com",
        "customer123",
    )
    response = client.get(
        "/api/v1/ops/users",
        headers={"Authorization": f"Bearer {customer_token}"},
    )

    assert response.status_code == 403