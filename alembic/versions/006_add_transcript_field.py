"""Add transcript JSONB column to interview_sessions.

Revision ID: 006
Revises: a0fb3355c61a
Create Date: 2026-03-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "006"
down_revision: Union[str, None] = "a0fb3355c61a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "interview_sessions",
        sa.Column("transcript", JSONB, nullable=True, server_default="[]"),
    )


def downgrade() -> None:
    op.drop_column("interview_sessions", "transcript")
