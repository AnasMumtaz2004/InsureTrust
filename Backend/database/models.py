import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.database import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="claimant")  # "claimant", "adjudicator", "admin"
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, index=True)
    claim_number = Column(String, unique=True, index=True, nullable=False)
    claimant_id = Column(String, ForeignKey("users.id"), nullable=False)
    policy_number = Column(String, nullable=False)
    status = Column(String, default="SUBMITTED")  # SUBMITTED, IN_REVIEW, DEBATING, PENDING_APPROVAL, APPROVED, DENIED, OVERRIDDEN
    complexity_score = Column(Float, nullable=True)
    total_claimed_amount = Column(Float, default=0.0)
    approved_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    documents = relationship("Document", back_populates="claim", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="claim", cascade="all, delete-orphan")
    debate_transcripts = relationship("DebateTranscript", back_populates="claim", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="claim", cascade="all, delete-orphan")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String, primary_key=True, index=True)
    policy_number = Column(String, unique=True, index=True, nullable=False)
    product_line = Column(String, nullable=False)  # "HEALTH", "AUTO", "PROPERTY"
    effective_date = Column(DateTime, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    coverage_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    document_name = Column(String, nullable=False)
    document_type = Column(String, nullable=False)  # "MEDICAL_BILL", "CLINICAL_NOTE", "RECEIPT", "POLICY_DOC"
    storage_path = Column(String, nullable=False)
    processed_status = Column(String, default="PENDING")
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    claim = relationship("Claim", back_populates="documents")

class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    decision_type = Column(String, nullable=False)  # "APPROVE", "DENY", "PARTIAL_APPROVE"
    rationale = Column(Text, nullable=False)
    itemized_payout = Column(JSON, nullable=True)
    compliance_status = Column(String, default="PASSED")
    approved_by = Column(String, nullable=True)  # User ID or "AUTO_SYSTEM"
    human_overridden = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    claim = relationship("Claim", back_populates="decisions")

class DebateTranscript(Base):
    __tablename__ = "debate_transcripts"

    id = Column(String, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    pro_approval_arguments = Column(JSON, nullable=True)
    pro_denial_arguments = Column(JSON, nullable=True)
    reconciliation_summary = Column(Text, nullable=True)
    confidence_delta = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    claim = relationship("Claim", back_populates="debate_transcripts")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    claim_id = Column(String, ForeignKey("claims.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    state_snapshot = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    claim = relationship("Claim", back_populates="audit_logs")

class PrecedentRecord(Base):
    __tablename__ = "precedent_records"

    id = Column(String, primary_key=True, index=True)
    precedent_code = Column(String, unique=True, index=True, nullable=False)
    diagnosis_code = Column(String, index=True, nullable=True)
    procedure_code = Column(String, index=True, nullable=True)
    decision_outcome = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    vector_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
