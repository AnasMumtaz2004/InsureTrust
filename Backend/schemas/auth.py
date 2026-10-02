from pydantic import BaseModel, field_validator
from typing import Optional

from database.enums import Role


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserRegisterRequest(BaseModel):
    """Public registration — always creates a customer."""
    email: str
    password: str
    full_name: str
    organization_code: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

    model_config = {"extra": "ignore"}


class CreateStaffRequest(BaseModel):
    """Admin-only endpoint to create staff or admin users."""
    email: str
    password: str
    full_name: str
    role: Role  # must be "staff" or "admin"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

    @field_validator("role")
    @classmethod
    def role_must_be_staff_or_admin(cls, v: Role) -> Role:
        if v not in {Role.STAFF, Role.ADMIN}:
            raise ValueError("Role must be 'staff' or 'admin'.")
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
    full_name: str


class UserProfileResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    organization_id: Optional[str] = None

    class Config:
        from_attributes = True
