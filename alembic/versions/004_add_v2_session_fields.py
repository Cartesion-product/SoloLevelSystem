"""Add mode and target_company columns to interview_sessions for v2.

Revision ID: 004
Revises: 003
Create Date: 2026-02-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("interview_sessions", sa.Column("mode", sa.String(50), nullable=True))
    op.add_column("interview_sessions", sa.Column("target_company", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("interview_sessions", "target_company")
    op.drop_column("interview_sessions", "mode")
