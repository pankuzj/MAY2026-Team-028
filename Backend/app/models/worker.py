"""Worker ORM model."""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkerStatus(str, Enum):
    """Operational availability states for crew members."""

    AVAILABLE = "available"
    ASSIGNED = "assigned"
    OFF_DUTY = "off_duty"
    UNAVAILABLE = "unavailable"


class Worker(Base):
    """Assignable cleanup crew member."""

    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_code: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    role_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=WorkerStatus.AVAILABLE.value, nullable=False, index=True
    )
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
