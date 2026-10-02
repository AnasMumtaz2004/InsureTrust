import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.enums import Role
from database.models import User, Organization
from schemas.auth import (
    UserLoginRequest,
    UserRegisterRequest,
    CreateStaffRequest,
    TokenResponse,
    UserProfileResponse,
)
from utils.security import hash_password, verify_password, create_access_token
from api.deps import get_current_user, require_role

router = APIRouter(prefix="/auth", tags=["Authentication"])

_BAD_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid email or password.",
)


@router.post("/register", response_model=UserProfileResponse)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already registered.")

    org_id = None
    if req.organization_code:
        org = db.query(Organization).filter(Organization.code == req.organization_code).first()
        if org:
            org_id = org.id

    user = User(
        id=f"USR-{uuid.uuid4().hex[:8].upper()}",
        email=email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=Role.CUSTOMER.value,
        organization_id=org_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login/customer", response_model=TokenResponse)
def login_customer(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user or user.role != Role.CUSTOMER.value or not verify_password(req.password, user.hashed_password):
        raise _BAD_CREDENTIALS

    token = create_access_token(sub=user.id, role=user.role, extra_claims={"email": user.email, "name": user.full_name})
    return TokenResponse(access_token=token, token_type="bearer", role=user.role, user_id=user.id, full_name=user.full_name)


@router.post("/login/staff", response_model=TokenResponse)
def login_staff(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.strip().lower()).first()
    if not user or user.role not in {Role.STAFF.value, Role.ADMIN.value} or not verify_password(req.password, user.hashed_password):
        raise _BAD_CREDENTIALS

    token = create_access_token(sub=user.id, role=user.role, extra_claims={"email": user.email, "name": user.full_name})
    return TokenResponse(access_token=token, token_type="bearer", role=user.role, user_id=user.id, full_name=user.full_name)


@router.post("/create-staff", response_model=UserProfileResponse)
def create_staff_user(
    req: CreateStaffRequest,
    current_user: User = Depends(require_role(Role.ADMIN)),
    db: Session = Depends(get_db),
):
    """Admin-only: create a staff or admin user."""
    email = req.email.strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User email already registered.")

    user = User(
        id=f"USR-{uuid.uuid4().hex[:8].upper()}",
        email=email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserProfileResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns the authenticated user's profile."""
    return current_user
