import uuid
from datetime import datetime
from sqlalchemy import Column, create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from database.enums import ClaimStatus, map_decision_to_status

# Create engine (SQLite default with connect_args for multithreading in dev)
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_columns(connection, table_name, columns):
    """Add missing nullable SQLAlchemy columns to an existing table."""
    inspector = inspect(connection)
    if not inspector.has_table(table_name):
        return

    existing = {column["name"] for column in inspector.get_columns(table_name)}
    preparer = connection.dialect.identifier_preparer
    quoted_table = preparer.quote(table_name)
    for column in columns:
        if not isinstance(column, Column) or not column.nullable or column.name in existing:
            continue
        quoted_column = preparer.quote(column.name)
        column_type = column.type.compile(dialect=connection.dialect)
        connection.execute(text(
            f"ALTER TABLE {quoted_table} ADD COLUMN {quoted_column} {column_type}"
        ))
        existing.add(column.name)


def migrate_legacy_claim_statuses(connection):
    """Convert historical graph and decision values into ClaimStatus values."""
    if not inspect(connection).has_table("claims"):
        return

    legacy_statuses = {
        "PAUSED_FOR_HUMAN_REVIEW": ClaimStatus.PENDING_APPROVAL,
        "DEBATING": ClaimStatus.IN_REVIEW,
    }
    rows = connection.execute(text("SELECT id, status FROM claims")).all()
    for claim_id, status in rows:
        target = legacy_statuses.get(status)
        if target is None and isinstance(status, str) and status.startswith("COMPLETED_"):
            target = map_decision_to_status(status.removeprefix("COMPLETED_"))
        elif target is None and status in {"APPROVE", "PARTIAL_APPROVE", "DENY"}:
            target = map_decision_to_status(status)
        if target is not None:
            connection.execute(
                text("UPDATE claims SET status = :status WHERE id = :claim_id"),
                {"status": target.value, "claim_id": claim_id},
            )

def seed_demo_data():
    from database.models import Organization, User, Policy, Claim
    from utils.security import hash_password

    Session = SessionLocal()
    try:
        if Session.query(Organization).count() == 0:
            org = Organization(id="ORG-1001", name="InsureTrust Demo", code="INSURETRUST")
            Session.add(org)
            Session.flush()

            customer = User(
                id="USR-CUSTOMER",
                email="customer@insuretrust.com",
                hashed_password=hash_password("customer123"),
                full_name="Alicia Brown",
                role="customer",
                organization_id=org.id,
            )
            staff = User(
                id="USR-STAFF",
                email="staff@insuretrust.com",
                hashed_password=hash_password("staff123"),
                full_name="Diana Lewis",
                role="staff",
                organization_id=org.id,
            )
            Session.add_all([customer, staff])
            Session.flush()

            # Seed admin user if ADMIN_EMAIL and ADMIN_PASSWORD are configured
            if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
                admin = User(
                    id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                    email=settings.ADMIN_EMAIL.strip().lower(),
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    full_name="Admin",
                    role="admin",
                    organization_id=org.id,
                )
                Session.add(admin)
                Session.flush()

            policy = Policy(
                id="POL-1001",
                policy_number="POL-HE-2023-001",
                product_line="HEALTH",
                effective_date=datetime.utcnow(),
                expiration_date=datetime.utcnow(),
                coverage_details={"deductible": 500, "coverage_limit": 10000},
            )
            Session.add(policy)
            Session.flush()

            claim = Claim(
                id="CLM-DEMO-001",
                claim_number="CN-20260802-0001",
                claimant_id=customer.id,
                policy_number=policy.policy_number,
                status="IN_REVIEW",
                complexity_score=4.2,
                total_claimed_amount=4200.0,
                approved_amount=3500.0,
            )
            Session.add(claim)
            Session.commit()
        else:
            # Even when the org already exists, ensure admin user is seeded
            if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
                existing_admin = Session.query(User).filter(
                    User.email == settings.ADMIN_EMAIL.strip().lower(),
                    User.role == "admin",
                ).first()
                if not existing_admin:
                    admin = User(
                        id=f"USR-{uuid.uuid4().hex[:8].upper()}",
                        email=settings.ADMIN_EMAIL.strip().lower(),
                        hashed_password=hash_password(settings.ADMIN_PASSWORD),
                        full_name="Admin",
                        role="admin",
                    )
                    Session.add(admin)
            Session.commit()
    finally:
        Session.close()


def init_db():
    """Utility to create tables on startup."""
    from database.models import Claim

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        ensure_columns(connection, "claims", [Claim.__table__.c.completed_at])
        migrate_legacy_claim_statuses(connection)
    seed_demo_data()
