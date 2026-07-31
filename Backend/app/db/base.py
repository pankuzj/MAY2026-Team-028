"""SQLAlchemy declarative base + shared metadata."""

from sqlalchemy.orm import DeclarativeBase

__all__ = ["Base"]


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
