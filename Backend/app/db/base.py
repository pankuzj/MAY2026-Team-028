"""SQLAlchemy declarative base + shared metadata.

Task S1-F03. Two things live here:

* ``Base`` — the declarative base every model inherits from. Its ``.metadata``
  is the single registry of tables that Alembic autogenerate compares against
  the live database.
* ``TimestampMixin`` — ``created_at`` / ``updated_at``, added by mixin so the
  columns are declared once instead of on all sixteen tables.

**Import rule:** ``app/db/base_models.py`` (not this file) imports every model
module. Alembic imports that one, which populates ``Base.metadata``. Keeping the
imports out of ``base.py`` avoids a circular import — models import ``Base`` from
here, so this module must not import models.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

__all__ = ["Base", "TimestampMixin", "utcnow"]

# Explicit naming convention for every constraint and index.
#
# Why this matters more than it looks: without it, databases auto-name
# constraints, and the names differ between PostgreSQL and SQLite. Alembic then
# generates migrations containing `op.drop_constraint(None, ...)`, which fails on
# downgrade. Setting the convention up front means every constraint has a
# predictable name we can reference in a migration by hand.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


def utcnow() -> datetime:
    """Timezone-aware current UTC time.

    Used as the Python-side default. ``datetime.utcnow()`` is deprecated in 3.12
    and — worse — returns a *naive* datetime, which silently compares wrong
    against aware values. Plan assumption 8: all timestamps are UTC.
    """
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` to a model.

    Defaults are set on both sides: ``server_default``/``onupdate`` so rows
    written by raw SQL or a seed script still get stamped, and the Python
    ``default`` so the value is available on the instance before a flush.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        server_default=func.now(),
        nullable=False,
        doc="Row creation time (UTC).",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        server_default=func.now(),
        nullable=False,
        doc="Last modification time (UTC).",
    )
