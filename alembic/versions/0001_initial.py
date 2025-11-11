"""initial schema for english ia"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    llm_provider_enum = sa.Enum("simple_mock", "ollama", "openai", name="llmprovider")
    session_status_enum = sa.Enum("active", "finished", name="sessionstatus")
    message_role_enum = sa.Enum("user", "assistant", name="messagerole")
    error_category_enum = sa.Enum("grammar", "vocab", "fluency", name="errorcategory")
    quiz_type_enum = sa.Enum("mcq", "cloze", name="quiztype")
    cefr_enum = sa.Enum("A2", "B1", "B2", "C1", name="cefrlevel")

    llm_provider_enum.create(op.get_bind(), checkfirst=True)
    session_status_enum.create(op.get_bind(), checkfirst=True)
    message_role_enum.create(op.get_bind(), checkfirst=True)
    error_category_enum.create(op.get_bind(), checkfirst=True)
    quiz_type_enum.create(op.get_bind(), checkfirst=True)
    cefr_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("nickname", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("llm_provider", llm_provider_enum, nullable=False),
        sa.Column("llm_model", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic", sa.String(length=128), nullable=False),
        sa.Column("status", session_status_enum, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("role", message_role_enum, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "error_spans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("message_id", sa.String(length=36), sa.ForeignKey("messages.id"), nullable=False),
        sa.Column("start", sa.Integer(), nullable=False),
        sa.Column("end", sa.Integer(), nullable=False),
        sa.Column("category", error_category_enum, nullable=False),
        sa.Column("user_text", sa.Text(), nullable=False),
        sa.Column("corrected_text", sa.Text(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
    )

    op.create_table(
        "quizzes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("session_id", sa.String(length=36), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("type", quiz_type_enum, nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("choices_json", sa.Text(), nullable=False),
        sa.Column("answer", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("quiz_id", sa.String(length=36), sa.ForeignKey("quizzes.id"), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "flashcards",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("source_error_id", sa.String(length=36), sa.ForeignKey("error_spans.id")),
        sa.Column("ease", sa.Numeric(3, 2), nullable=False),
        sa.Column("interval", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_id", sa.String(length=36), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("words", sa.Integer(), nullable=False),
        sa.Column("errors", sa.Integer(), nullable=False),
        sa.Column("accuracy_pct", sa.Numeric(5, 2), nullable=False),
        sa.Column("cefr_estimate", cefr_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("metric_snapshots")
    op.drop_table("flashcards")
    op.drop_table("quiz_attempts")
    op.drop_table("quizzes")
    op.drop_table("error_spans")
    op.drop_table("messages")
    op.drop_table("sessions")
    op.drop_table("settings")
    op.drop_table("users")
    sa.Enum(name="cefrlevel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="quiztype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="errorcategory").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="messagerole").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sessionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="llmprovider").drop(op.get_bind(), checkfirst=True)
