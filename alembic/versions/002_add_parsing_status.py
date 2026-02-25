"""Add parsing_status to resumes table.

Revision ID: 002
Revises: 001
Create Date: 2026-02-08
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "resumes",
        sa.Column("parsing_status", sa.String(50), server_default=sa.text("'completed'")),
    )


def downgrade() -> None:
    op.drop_column("resumes", "parsing_status")
