"""daily practice tracking and streaks"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0003_daily_practice_streak"
down_revision = "0002_topics_prompt"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sessions",
        sa.Column("active_seconds", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "sessions",
        sa.Column("last_interaction_at", sa.DateTime(timezone=True), nullable=True),
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE sessions "
            "SET active_seconds = CASE "
            "WHEN ended_at IS NOT NULL THEN "
            "CAST(((julianday(ended_at) - julianday(started_at)) * 86400) AS INTEGER) "
            "ELSE 0 END"
        )
    )

    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.alter_column("active_seconds", server_default=None)

    op.create_table(
        "daily_practices",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("session_id", sa.String(length=36), sa.ForeignKey("sessions.id"), nullable=True),
        sa.Column("messages_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minutes_estimated", sa.Numeric(6, 2), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
        sa.UniqueConstraint("user_id", "date", name="uq_daily_practice_user_date"),
    )

    op.create_table(
        "user_streaks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("current_streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_practice_date", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("(datetime('now'))"),
        ),
    )


def downgrade() -> None:
    op.drop_table("user_streaks")
    op.drop_table("daily_practices")

    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.drop_column("last_interaction_at")
        batch_op.drop_column("active_seconds")
