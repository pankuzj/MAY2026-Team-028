"""SQLAlchemy ORM models — the persistence shape of each entity."""

from app.models.user import User, UserRole

__all__ = ["User", "UserRole"]
