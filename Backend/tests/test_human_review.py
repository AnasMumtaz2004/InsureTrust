"""
Tests for the human-review resume flow.

Scenario
--------
1. A customer submits a $6,000 claim -> pauses with status PENDING_APPROVAL,
   approved_amount > 0 from the draft, and a Decision row with compliance_status=PENDING_REVIEW.
2. As staff:
   - APPROVE          -> status=APPROVED, payout equals the draft.
   - OVERRIDE payout  -> status=OVERRIDDEN, human_overridden=True, approved_amount=999.
   - OVERRIDE no fields -> 422.
   - SEND_BACK        -> status=SENT_BACK, payout unchanged.
   - Acting twice on same claim -> 409.
   - Acting on a non-paused claim -> 409.
3. Customer token on decision route -> 403.
"""

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _customer_token(client) -> str:
    res = client.post(
        "/api/v1/auth/login/customer",
        json={"email": "customer@insuretrust.com", "password": "customer123"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _staff_token(client) -> str:
    res = client.post(
        "/api/v1/auth/login/staff",
        json={"email": "staff@insuretrust.com", "password": "staff123"},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _submit_high_value_claim(client, customer_token: str) -> dict:
    """Submit a $6,000 claim that should pause for human review."""
    res = client.post(
        "/api/v1/claims/submit",
        json={
            "policy_number": "POL-HE-2023-001",
            "incident_date": "2026-01-15",
            "claimed_amount": 6000.0,
            "diagnosis_codes": ["M54.5"],
            "procedure_codes": ["99214"],
            "description": "High-value claim requiring human review.",
        },
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert res.status_code == 201, f"Submit failed: {res.text}"
    return res.json()


def _act(client, staff_token: str, claim_id: str, body: dict):
    return client.post(
        f"/api/v1/ops/decisions/{claim_id}/action",
        json=body,
        headers={"Authorization": f"Bearer {staff_token}"},
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHumanReviewFlow:

    def test_submit_pauses_with_pending_approval(self, client):
        """$6,000 claim pauses with PENDING_APPROVAL, approved_amount > 0, Decision row exists."""
        from database.database import SessionLocal
        from database.models import Claim, Decision

        cust_tok = _customer_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        # DB claim
        db = SessionLocal()
        try:
            db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
            assert db_claim is not None
            assert db_claim.status == "PENDING_APPROVAL", (
                f"Expected PENDING_APPROVAL, got {db_claim.status}"
            )
            assert db_claim.approved_amount > 0, (
                f"approved_amount should be > 0 from draft, got {db_claim.approved_amount}"
            )

            # Decision row with PENDING_REVIEW
            dec = (
                db.query(Decision)
                .filter(Decision.claim_id == claim_id)
                .order_by(Decision.created_at.desc())
                .first()
            )
            assert dec is not None, "Decision row should exist after submit"
            assert dec.compliance_status == "PENDING_REVIEW", (
                f"Expected PENDING_REVIEW, got {dec.compliance_status}"
            )
        finally:
            db.close()

    def test_approve_sets_approved_with_draft_payout(self, client):
        """APPROVE -> APPROVED; payout == draft approved_amount."""
        from database.database import SessionLocal
        from database.models import Claim, Decision

        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        # Get the draft amount before acting
        db = SessionLocal()
        try:
            db_claim_before = db.query(Claim).filter(Claim.id == claim_id).first()
            draft_amount = db_claim_before.approved_amount
        finally:
            db.close()

        res = _act(client, staff_tok, claim_id, {
            "action": "APPROVE",
            "adjudicator_notes": "Looks good, approved.",
        })
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "APPROVED"

        db = SessionLocal()
        try:
            db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
            assert db_claim.status == "APPROVED"
            # Payout should match the draft (may vary slightly due to float)
            assert db_claim.approved_amount == pytest.approx(draft_amount, abs=0.01)

            # Decision row updated
            dec = (
                db.query(Decision)
                .filter(Decision.claim_id == claim_id)
                .order_by(Decision.created_at.desc())
                .first()
            )
            assert dec is not None
            assert dec.compliance_status == "PASSED"
            assert dec.approved_by is not None
            assert dec.human_overridden is False
        finally:
            db.close()

    def test_override_with_payout_999(self, client):
        """OVERRIDE payout 999 -> OVERRIDDEN, human_overridden=True, approved_amount=999."""
        from database.database import SessionLocal
        from database.models import Claim, Decision

        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        res = _act(client, staff_tok, claim_id, {
            "action": "OVERRIDE",
            "adjudicator_notes": "Adjusting payout after review.",
            "modified_payout": 999.0,
        })
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "OVERRIDDEN"

        db = SessionLocal()
        try:
            db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
            assert db_claim.status == "OVERRIDDEN"
            assert db_claim.approved_amount == pytest.approx(999.0, abs=0.01)

            dec = (
                db.query(Decision)
                .filter(Decision.claim_id == claim_id)
                .order_by(Decision.created_at.desc())
                .first()
            )
            assert dec is not None
            assert dec.human_overridden is True
            assert dec.compliance_status == "PASSED"
        finally:
            db.close()

    def test_override_with_no_payout_or_type_returns_422(self, client):
        """OVERRIDE with neither modified_payout nor decision_type -> 422."""
        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        # Act without modified_payout or decision_type
        res = _act(client, staff_tok, claim_id, {
            "action": "OVERRIDE",
            "adjudicator_notes": "Missing required fields.",
        })
        assert res.status_code == 422, (
            f"Expected 422 for missing override fields, got {res.status_code}: {res.text}"
        )

    def test_send_back_sets_sent_back_status(self, client):
        """SEND_BACK -> SENT_BACK; payout unchanged from draft."""
        from database.database import SessionLocal
        from database.models import Claim, Decision

        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        db = SessionLocal()
        try:
            draft_amount = db.query(Claim).filter(Claim.id == claim_id).first().approved_amount
        finally:
            db.close()

        res = _act(client, staff_tok, claim_id, {
            "action": "SEND_BACK",
            "adjudicator_notes": "Needs more documentation before we can approve.",
        })
        assert res.status_code == 200, res.text
        assert res.json()["status"] == "SENT_BACK"

        db = SessionLocal()
        try:
            db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
            assert db_claim.status == "SENT_BACK"
            # Payout should be unchanged (= draft)
            assert db_claim.approved_amount == pytest.approx(draft_amount, abs=0.01)

            dec = (
                db.query(Decision)
                .filter(Decision.claim_id == claim_id)
                .order_by(Decision.created_at.desc())
                .first()
            )
            assert dec is not None
            assert dec.compliance_status == "SENT_BACK"
        finally:
            db.close()

    def test_acting_twice_on_same_claim_returns_409(self, client):
        """Acting twice on the same claim (already finalized) -> 409."""
        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        # First action
        res1 = _act(client, staff_tok, claim_id, {
            "action": "APPROVE",
            "adjudicator_notes": "First approval.",
        })
        assert res1.status_code == 200, res1.text

        # Second action on already-finalized claim
        res2 = _act(client, staff_tok, claim_id, {
            "action": "APPROVE",
            "adjudicator_notes": "Second approval attempt.",
        })
        assert res2.status_code == 409, (
            f"Expected 409 for double-act, got {res2.status_code}: {res2.text}"
        )

    def test_acting_on_non_paused_claim_returns_409(self, client):
        """Acting on a claim that never paused (auto-approved) -> 409."""
        cust_tok = _customer_token(client)
        staff_tok = _staff_token(client)

        # Submit a low-value claim that will not pause
        res = client.post(
            "/api/v1/claims/submit",
            json={
                "policy_number": "POL-HE-2023-001",
                "incident_date": "2026-01-15",
                "claimed_amount": 100.0,   # below $5,000 threshold
                "diagnosis_codes": ["M54.5"],
                "procedure_codes": ["99214"],
                "description": "Minor claim, auto-processed.",
            },
            headers={"Authorization": f"Bearer {cust_tok}"},
        )
        assert res.status_code == 201, res.text
        claim_id = res.json()["id"]

        act_res = _act(client, staff_tok, claim_id, {
            "action": "APPROVE",
            "adjudicator_notes": "Trying to approve a non-paused claim.",
        })
        assert act_res.status_code == 409, (
            f"Expected 409 for non-paused claim, got {act_res.status_code}: {act_res.text}"
        )

    def test_customer_token_on_decision_route_returns_403(self, client):
        """Customer token on decision route -> 403."""
        cust_tok = _customer_token(client)
        data = _submit_high_value_claim(client, cust_tok)
        claim_id = data["id"]

        res = _act(client, cust_tok, claim_id, {
            "action": "APPROVE",
            "adjudicator_notes": "Trying to self-approve.",
        })
        assert res.status_code == 403, (
            f"Expected 403 for customer acting on decision, got {res.status_code}: {res.text}"
        )
