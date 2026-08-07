"""Add persisted assistance requests to tasks."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column(
            "assistance_requested", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.add_column("tasks", sa.Column("assistance_notes", sa.Text(), nullable=True))
    op.alter_column("tasks", "assistance_requested", server_default=None)


def downgrade() -> None:
    op.drop_column("tasks", "assistance_notes")
    op.drop_column("tasks", "assistance_requested")
