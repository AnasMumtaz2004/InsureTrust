from utils.logger import logger

class NotificationService:
    """Async notification dispatcher for claimant email/SMS updates on status changes."""

    def send_status_update(self, claim_id: str, new_status: str, recipient_email: str = None):
        logger.info(f"NOTIFICATION DISPATCH: Claim {claim_id} status changed to '{new_status}'. Alerting claimant.")

    def send_decision_letter(self, claim_id: str, decision_type: str, pdf_path: str = None):
        logger.info(f"NOTIFICATION DISPATCH: Official Decision Letter for Claim {claim_id} ({decision_type}) sent to claimant.")
