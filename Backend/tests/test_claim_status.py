from datetime import datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import Column, DateTime, String, create_engine, text
from sqlalchemy.orm import Session

from api.routes.analytics import get_platform_kpis
from api.routes.ops_cases import get_operations_queue
from database.database import ensure_columns, migrate_legacy_claim_statuses
from database.enums import ClaimStatus, map_decision_to_status
from database.models import Base, Claim, Decision, User
from services import claim_service


@pytest.mark.parametrize(
    ("decision_type", "expected_status"),
    [
        ("APPROVE", ClaimStatus.APPROVED),
        ("PARTIAL_APPROVE", ClaimStatus.PARTIAL_APPROVED),
        ("DENY", ClaimStatus.DENIED),
    ],
)
def test_map_decision_to_status(decision_type, expected_status):
    assert map_decision_to_status(decision_type) is expected_status


@pytest.mark.parametrize(
    ("decision_type", "expected_status"),
    [
        ("APPROVE", ClaimStatus.APPROVED.value),
        ("PARTIAL_APPROVE", ClaimStatus.PARTIAL_APPROVED.value),
        ("DENY", ClaimStatus.DENIED.value),
    ],
)
def test_submission_persists_normalized_decision_status(
    db_session, monkeypatch, decision_type, expected_status
):
    class CompletedGraph:
        @staticmethod
        def stream(_state, _config):
            return iter(())

        @staticmethod
        def get_state(_config):
            return SimpleNamespace(values={
                "final_decision": {"decision_type": decision_type},
                "approved_amount": 75.0,
            })

    monkeypatch.setattr(claim_service, "claims_graph", CompletedGraph())
    result = claim_service.ClaimService(db_session).submit_and_process_claim({
        "claimant_id": "USR-CUSTOMER",
        "policy_number": "POL-TEST",
        "claimed_amount": 100.0,
    })
    claim = db_session.query(Claim).filter(Claim.id == result["claim_id"]).one()

    assert claim.status == expected_status
    assert claim.completed_at is not None


def _make_claim(claim_id, status, created_at=None, completed_at=None):
    return Claim(
        id=claim_id,
        claim_number=f"CN-{claim_id}",
        claimant_id="USR-CUSTOMER",
        policy_number="POL-TEST",
        status=status,
        total_claimed_amount=100.0,
        created_at=created_at or datetime.utcnow(),
        completed_at=completed_at,
    )


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        yield db
    engine.dispose()


def test_kpis_count_mixed_statuses_and_real_durations(db_session):
    now = datetime.utcnow()
    statuses = [
        ClaimStatus.APPROVED,
        ClaimStatus.PARTIAL_APPROVED,
        ClaimStatus.DENIED,
        ClaimStatus.PENDING_APPROVAL,
        ClaimStatus.IN_REVIEW,
        ClaimStatus.OVERRIDDEN,
        ClaimStatus.PROCESSING_FAILED,
        ClaimStatus.SENT_BACK,
    ]
    claims = []
    for index, status in enumerate(statuses):
        duration = (index + 1) * 10
        completed_at = now if status in {
            ClaimStatus.APPROVED,
            ClaimStatus.PARTIAL_APPROVED,
            ClaimStatus.DENIED,
            ClaimStatus.OVERRIDDEN,
            ClaimStatus.SENT_BACK,
        } else None
        created_at = now - timedelta(seconds=duration) if completed_at else now
        claim = _make_claim(f"CLM-{index}", status.value, created_at, completed_at)
        claims.append(claim)
        db_session.add(claim)
    db_session.flush()
    terminal_statuses = {
        ClaimStatus.APPROVED,
        ClaimStatus.PARTIAL_APPROVED,
        ClaimStatus.DENIED,
        ClaimStatus.OVERRIDDEN,
        ClaimStatus.SENT_BACK,
    }
    db_session.add_all([
        Decision(
            id=f"DEC-{index}",
            claim_id=f"CLM-{index}",
            decision_type="APPROVE",
            rationale="Reviewed",
            compliance_status="SENT_BACK" if claim.status == ClaimStatus.SENT_BACK.value else "PASSED",
            human_overridden=claim.status == ClaimStatus.OVERRIDDEN.value,
        )
        for index, claim in enumerate(claims)
        if ClaimStatus(claim.status) in terminal_statuses
    ])
    db_session.flush()

    kpis = get_platform_kpis(db_session, User(id="staff", role="staff"))

    assert kpis["total_claims_processed"] == 8
    assert kpis["approved_claims"] == 2
    assert kpis["partial_approved_claims"] == 1
    assert kpis["denied_claims"] == 1
    assert kpis["pending_human_review"] == 2
    assert kpis["failed_claims"] == 1
    assert kpis["sent_back_claims"] == 1
    assert kpis["human_override_rate"] == 0.2
    assert kpis["average_processing_time_seconds"] == 40


def test_kpis_average_is_null_without_completed_timestamps(db_session):
    db_session.add(_make_claim("CLM-NULL-TIME", ClaimStatus.APPROVED.value))
    db_session.flush()

    kpis = get_platform_kpis(db_session, User(id="staff", role="staff"))

    assert kpis["average_processing_time_seconds"] is None


def test_queue_includes_only_actionable_statuses(db_session, monkeypatch):
    queue_statuses = {
        ClaimStatus.PENDING_APPROVAL,
        ClaimStatus.IN_REVIEW,
        ClaimStatus.SENT_BACK,
        ClaimStatus.PROCESSING_FAILED,
    }
    all_statuses = list(ClaimStatus)
    db_session.add_all([
        _make_claim(f"CLM-{status.value}", status.value)
        for status in all_statuses
    ])
    db_session.flush()

    class EmptyGraph:
        @staticmethod
        def get_state(_config):
            return SimpleNamespace(values={})

    monkeypatch.setattr("api.routes.ops_cases.claims_graph", EmptyGraph())
    queue = get_operations_queue(db_session, User(id="staff", role="staff"))

    assert {item.status for item in queue} == {status.value for status in queue_statuses}


def test_legacy_status_migration_and_nullable_column_helper():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE claims (id VARCHAR PRIMARY KEY, status VARCHAR)"))
        legacy_values = [
            ("approve", "APPROVE"),
            ("deny", "DENY"),
            ("partial", "PARTIAL_APPROVE"),
            ("completed-approve", "COMPLETED_APPROVE"),
            ("completed-deny", "COMPLETED_DENY"),
            ("completed-partial", "COMPLETED_PARTIAL_APPROVE"),
            ("paused", "PAUSED_FOR_HUMAN_REVIEW"),
        ]
        connection.execute(
            text("INSERT INTO claims (id, status) VALUES (:id, :status)"),
            [{"id": claim_id, "status": status} for claim_id, status in legacy_values],
        )

        ensure_columns(connection, "claims", [Column("completed_at", DateTime, nullable=True)])
        migrate_legacy_claim_statuses(connection)
        rows = connection.execute(text("SELECT id, status FROM claims")).all()
        columns = {column["name"] for column in __import__("sqlalchemy").inspect(connection).get_columns("claims")}

    engine.dispose()
    assert dict(rows) == {
        "approve": "APPROVED",
        "deny": "DENIED",
        "partial": "PARTIAL_APPROVED",
        "completed-approve": "APPROVED",
        "completed-deny": "DENIED",
        "completed-partial": "PARTIAL_APPROVED",
        "paused": "PENDING_APPROVAL",
    }
    assert "completed_at" in columns