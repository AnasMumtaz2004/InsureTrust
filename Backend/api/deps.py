"""FastAPI authentication and authorization dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from database.database import get_db
from database.enums import Role
from database.models import Claim, User
from utils.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)

_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """Extract and verify the bearer token, then load the user from the DB.

    Returns the ``User`` ORM object.  The *database* role is authoritative,
    not the token's ``role`` claim.
    """
    if creds is None:
        raise _CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(creds.credentials)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise _CREDENTIALS_EXCEPTION
    except JWTError:
        raise _CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _CREDENTIALS_EXCEPTION
    return user


def require_role(*roles: Role | str):
    """Dependency factory: returns a dependency that 403s if the user's role
    is not one of the allowed *roles*.
    """
    allowed = {r.value if isinstance(r, Role) else r for r in roles}

    def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )
        return current_user

    return _guard


def assert_claim_access(user: User, claim: Claim) -> None:
    """Raise 404 if a customer tries to access a claim they don't own.

    Staff and admin always pass.  Using 404 instead of 403 prevents
    ID enumeration.
    """
    if user.role in {Role.STAFF.value, Role.ADMIN.value}:
        return
    if claim.claimant_id != user.id:
        raise HTTPException(status_code=404, detail="Claim not found.")
