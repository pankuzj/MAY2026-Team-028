"""Bulk waste pickup ORM model (S2-F04, US-31).

Field shape mirrors ``Frontend/src/context/BulkPickupContext.jsx``: load
bands and category surcharges drive a computed, informational ``fee``
(assumption #1 in the plan — the service is municipality-run, no payment
processing, the frontend already displays the fee so it stays).
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class BulkPickupStatus(str, Enum):
    """Lifecycle states — must match the frontend's fixed enum exactly."""

    REQUESTED = "requested"
    SCHEDULED = "scheduled"
    COLLECTED = "collected"
    CANCELLED = "cancelled"


class BulkPickupCategory(str, Enum):
    """Waste category, drives the surcharge portion of the fee calculation."""

    GENERAL = "general"
    E_WASTE = "e_waste"
    CONSTRUCTION_DEBRIS = "construction_debris"
    SCRAP_METAL = "scrap_metal"


class BulkPickupLoadBand(str, Enum):
    """Load size, drives the base portion of the fee calculation."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


class BulkPickup(Base, TimestampMixin):
    """Citizen-requested bulk waste collection."""

    __tablename__ = "bulk_pickups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    requested_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    ward_id: Mapped[int | None] = mapped_column(ForeignKey("wards.id"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(
        String(50), default=BulkPickupCategory.GENERAL.value, nullable=False, index=True
    )
    load_band: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default=BulkPickupStatus.REQUESTED.value, nullable=False, index=True
    )
    fee: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    assigned_vehicle_id: Mapped[int | None] = mapped_column(
        ForeignKey("vehicles.id"), nullable=True, index=True
    )
    assigned_worker_id: Mapped[int | None] = mapped_column(
        ForeignKey("workers.id"), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
