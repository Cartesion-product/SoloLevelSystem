"""Initial schema - all core tables.

Revision ID: 001
Revises:
Create Date: 2026-02-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("settings", postgresql.JSONB(), server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- resumes ---
    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(255)),
        sa.Column("template_type", sa.String(50)),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("raw_file_url", sa.Text()),
        sa.Column("parsed_data", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index(
        "idx_resume_default",
        "resumes",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    # --- target_jobs ---
    op.create_table(
        "target_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("company_name", sa.String(255)),
        sa.Column("position_name", sa.String(255), nullable=False),
        sa.Column("jd_text", sa.Text(), nullable=False),
        sa.Column("parsed_requirements", postgresql.JSONB()),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- skill_tree ---
    op.create_table(
        "skill_tree",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("skill_name", sa.String(255), nullable=False),
        sa.Column("parent_skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skill_tree.id")),
        sa.Column("proficiency_score", sa.SmallInteger(), server_default=sa.text("0")),
        sa.Column("evaluation_comment", sa.Text()),
        sa.Column("source_type", sa.String(50), server_default=sa.text("'resume_claimed'")),
        sa.Column("focus_status", sa.String(50), server_default=sa.text("'dormant'")),
        sa.Column("assess_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("last_assessed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("idx_skill_user", "skill_tree", ["user_id"])
    op.create_index("idx_skill_gap", "skill_tree", ["user_id", "source_type"])
    op.create_index("idx_skill_focus", "skill_tree", ["user_id", "focus_status"])

    # --- interview_sessions ---
    op.create_table(
        "interview_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("target_jobs.id")),
        sa.Column("session_type", sa.String(50), nullable=False, server_default=sa.text("'simulated'")),
        sa.Column("status", sa.String(50), server_default=sa.text("'in_progress'")),
        sa.Column("summary", postgresql.JSONB()),
        sa.Column("question_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("duration_seconds", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime()),
    )

    # --- quest_log ---
    op.create_table(
        "quest_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interview_sessions.id")),
        sa.Column("target_skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skill_tree.id")),
        sa.Column("quest_title", sa.String(255), nullable=False),
        sa.Column("quest_detail", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), server_default=sa.text("'generated'")),
        sa.Column("verification_method", sa.String(50)),
        sa.Column("due_date", sa.Date()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime()),
    )

    # --- user_psychology_profile ---
    op.create_table(
        "user_psychology_profile",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("personality_tags", postgresql.JSONB(), server_default=sa.text("'[]'")),
        sa.Column("confidence_score", sa.Float(), server_default=sa.text("0.5")),
        sa.Column("resilience_score", sa.Float(), server_default=sa.text("0.5")),
        sa.Column("preferred_style", sa.String(50), server_default=sa.text("'balanced'")),
        sa.Column("daily_motivation", sa.Text()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- mood_log ---
    op.create_table(
        "mood_log",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("interview_sessions.id")),
        sa.Column("detected_mood", sa.String(50)),
        sa.Column("trigger_event", sa.Text()),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # --- knowledge_documents ---
    op.create_table(
        "knowledge_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("doc_name", sa.String(255), nullable=False),
        sa.Column("doc_type", sa.String(50)),
        sa.Column("file_url", sa.Text()),
        sa.Column("chunk_count", sa.Integer(), server_default=sa.text("0")),
        sa.Column("status", sa.String(50), server_default=sa.text("'processing'")),
        sa.Column("domain_tags", postgresql.ARRAY(sa.Text())),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("knowledge_documents")
    op.drop_table("mood_log")
    op.drop_table("user_psychology_profile")
    op.drop_table("quest_log")
    op.drop_table("interview_sessions")
    op.drop_index("idx_skill_focus", table_name="skill_tree")
    op.drop_index("idx_skill_gap", table_name="skill_tree")
    op.drop_index("idx_skill_user", table_name="skill_tree")
    op.drop_table("skill_tree")
    op.drop_table("target_jobs")
    op.drop_index("idx_resume_default", table_name="resumes")
    op.drop_table("resumes")
    op.drop_table("users")
