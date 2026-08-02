import re
from typing import Dict, Any

SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
PHONE_REGEX = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
CARD_REGEX = re.compile(r'\b(?:\d[ -]*?){13,16}\b')

def mask_pii_string(text: str) -> str:
    """Masks SSN, phone numbers, emails, and card numbers from strings."""
    if not isinstance(text, str):
        return text
    text = SSN_REGEX.sub("[MASKED_SSN]", text)
    text = PHONE_REGEX.sub("[MASKED_PHONE]", text)
    text = EMAIL_REGEX.sub("[MASKED_EMAIL]", text)
    text = CARD_REGEX.sub("[MASKED_CARD]", text)
    return text

def sanitize_dict_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively masks PII values in dictionary structures."""
    sanitized = {}
    for key, val in data.items():
        if isinstance(val, str):
            sanitized[key] = mask_pii_string(val)
        elif isinstance(val, dict):
            sanitized[key] = sanitize_dict_pii(val)
        elif isinstance(val, list):
            sanitized[key] = [
                sanitize_dict_pii(item) if isinstance(item, dict)
                else (mask_pii_string(item) if isinstance(item, str) else item)
                for item in val
            ]
        else:
            sanitized[key] = val
    return sanitized
