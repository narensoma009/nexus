"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    op.create_table(
        "accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_table(
        "portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )
    op.create_table(
        "sub_portfolios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )
    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("portfolios.id"), nullable=True),
        sa.Column("sub_portfolio_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sub_portfolios.id"), nullable=True),
        sa.Column("parent_team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id"), nullable=True),
    )
    op.create_table(
        "resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("seniority", sa.String(50), nullable=False),
        sa.Column("skills", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entra_oid", sa.String(255), unique=True, nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resources.id"), nullable=True),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_table(
        "programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="on_track"),
        sa.Column("start_date", sa.DateTime, nullable=True),
        sa.Column("end_date", sa.DateTime, nullable=True),
    )
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("programs.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="on_track"),
    )
    op.create_table(
        "workstreams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="on_track"),
    )
    op.create_table(
        "resource_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resources.id"), nullable=False),
        sa.Column("workstream_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workstreams.id"), nullable=False),
        sa.Column("role", sa.String(255), nullable=False),
        sa.Column("allocation_pct", sa.Integer, nullable=False),
        sa.Column("start_date", sa.DateTime, nullable=True),
        sa.Column("end_date", sa.DateTime, nullable=True),
    )
    op.create_table(
        "ai_tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("vendor", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("rollout_date", sa.DateTime, nullable=True),
        sa.Column("target_user_count", sa.Integer, nullable=True),
    )
    op.create_table(
        "ai_tool_licenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_tools.id"), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resources.id"), nullable=False),
        sa.Column("assigned_date", sa.DateTime, nullable=False),
        sa.Column("adoption_stage", sa.String(50), nullable=False, server_default="piloting"),
    )
    op.create_table(
        "ai_tool_usages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tool_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_tools.id"), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resources.id"), nullable=False),
        sa.Column("recorded_date", sa.DateTime, nullable=False),
        sa.Column("sessions", sa.Integer, nullable=False, server_default="0"),
        sa.Column("active_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("source", sa.String(50), nullable=False, server_default="manual"),
    )
    op.create_table(
        "ppt_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tags", sa.String(500), nullable=True),
        sa.Column("slide_count", sa.Integer, nullable=False),
        sa.Column("blob_path", sa.String(500), nullable=False),
        sa.Column("placeholder_map", sa.Text, nullable=False),
        sa.Column("uploaded_by", sa.String(255), nullable=False),
        sa.Column("uploaded_at", sa.DateTime, nullable=False),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
    )
    op.create_table(
        "document_embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )


def downgrade() -> None:
    for t in [
        "document_embeddings", "ppt_templates", "ai_tool_usages", "ai_tool_licenses",
        "ai_tools", "resource_assignments", "workstreams", "projects", "programs",
        "user_roles", "resources", "teams", "sub_portfolios", "portfolios", "accounts",
    ]:
        op.drop_table(t)
