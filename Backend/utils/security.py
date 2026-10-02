"""Shared password hashing and JWT token utilities.

Uses pbkdf2_sha256 (no bcrypt) to avoid compatibility issues with
recent bcrypt releases.  All auth routes and the database seeder
import from here to keep one CryptContext.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

# Lazy import to break the circular dependency:
# config -> (module-level Settings()) -> database.database -> utils.security -> config
# We import settings inside the functions that need it.

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    sub: str,
    role: str,
    *,
    extra_claims: dict | None = None,
) -> str:
    """Create a signed JWT with timezone-aware exp and iat."""
    from config import settings

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": sub,
        "role": role,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT.  Raises ``jose.JWTError`` on any failure."""
    from config import settings

    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
