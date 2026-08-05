import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from passlib.context import CryptContext
from config import settings

# Create engine (SQLite default with connect_args for multithreading in dev)
engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_db():
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_demo_data():
    from database.models import Organization, User, Policy, Claim

    Session = SessionLocal()
    try:
        if Session.query(Organization).count() == 0:
            org = Organization(id="ORG-1001", name="InsureTrust Demo", code="INSURETRUST")
            Session.add(org)
            Session.flush()

            customer = User(
                id="USR-CUSTOMER",
                email="customer@insuretrust.com",
                hashed_password=pwd_context.hash("customer123"),
                full_name="Alicia Brown",
                role="customer",
                organization_id=org.id,
            )
            staff = User(
                id="USR-STAFF",
                email="staff@insuretrust.com",
                hashed_password=pwd_context.hash("staff123"),
                full_name="Diana Lewis",
                role="staff",
                organization_id=org.id,
            )
            Session.add_all([customer, staff])
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
            Session.commit()
    finally:
        Session.close()


def init_db():
    """Utility to create tables on startup."""
    Base.metadata.create_all(bind=engine)
    seed_demo_data()
