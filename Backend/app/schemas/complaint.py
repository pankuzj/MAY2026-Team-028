"""Pydantic DTOs for complaints and complaint history."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ComplaintStatus(str, Enum):
    """Complaint lifecycle values exposed through the API."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class ComplaintBase(BaseModel):
    """Shared complaint fields."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    ward_id: int | None = None
    category: str | None = Field(default=None, max_length=100)
    priority: str | None = Field(default=None, max_length=50)
    address: str | None = Field(default=None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    photo_url: str | None = Field(default=None, max_length=2048)


class ComplaintCreate(ComplaintBase):
    """Payload for creating a complaint."""

    reported_by_user_id: int | None = None


class ComplaintSubmit(BaseModel):
    """Payload coming directly from the citizen report form."""

    location: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    hazard: str | None = Field(default=None, max_length=100)
    photo: str | None = Field(default=None, max_length=2048)
    coords: dict[str, float] | None = None
    ward_id: int | None = None


class ComplaintUpdate(BaseModel):
    """Payload for updating a complaint."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)
    ward_id: int | None = None
    category: str | None = Field(default=None, max_length=100)
    priority: str | None = Field(default=None, max_length=50)
    status: ComplaintStatus | None = None
    address: str | None = Field(default=None, max_length=255)
    latitude: float | None = None
    longitude: float | None = None
    photo_url: str | None = Field(default=None, max_length=2048)
    resolved_at: datetime | None = None
    cancelled_at: datetime | None = None


class ComplaintRead(ComplaintBase):
    """Complaint response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    reported_by_user_id: int
    status: ComplaintStatus
    resolved_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ComplaintFilter(BaseModel):
    """Optional list filters for complaints."""

    search: str | None = Field(default=None, max_length=255)
    status: ComplaintStatus | None = None
    ward_id: int | None = None
    reported_by_user_id: int | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    created_from: datetime | None = None
    created_to: datetime | None = None


class ComplaintStatusHistoryRead(BaseModel):
    """Complaint status audit trail response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: int
    from_status: str
    to_status: str
    changed_by_user_id: int
    notes: str | None = None
    created_at: datetime
