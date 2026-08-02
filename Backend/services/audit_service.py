import uuid
import datetime
from typing import Dict, Any
from sqlalchemy.orm import Session
from database.models import AuditLog
from utils.pii_masking import sanitize_dict_pii
from utils.logger import logger

class AuditService:
    """Writes immutable step-by-step state audit entries into AuditLog DB table."""

    def __init__(self, db: Session):
        self.db = db

    def log_step(self, claim_id: str, agent_name: str, action: str, snapshot: Dict[str, Any]):
        try:
            sanitized_snapshot = sanitize_dict_pii(snapshot)
            log_entry = AuditLog(
                id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
                claim_id=claim_id,
                agent_name=agent_name,
                action=action,
                state_snapshot=sanitized_snapshot,
                timestamp=datetime.datetime.utcnow()
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to record audit log for claim {claim_id}: {e}")
            self.db.rollback()
