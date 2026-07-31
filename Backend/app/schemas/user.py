"""Pydantic schemas for User entity."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base fields for user schemas."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.CITIZEN
    phone: Optional[str] = None
    ward_id: Optional[int] = None


class UserCreate(UserBase):
    """Payload for user registration or creation."""

    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    """Payload for updating user details."""

    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = None
    ward_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
