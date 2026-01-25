"""add practice topics table and session prompt"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa

revision = "0002_topics_prompt"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

_DEFAULT_PROMPT = "You are a patient English tutor guiding the learner."


def upgrade() -> None:
    op.create_table(
        "practice_topics",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False, unique=True),
        sa.Column("label", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
    )

    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("topic_code", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("system_prompt", sa.Text(), nullable=True))

    connection = op.get_bind()
    legacy_id = uuid.uuid4().hex
    connection.execute(
        sa.text(
            "INSERT INTO practice_topics (id, code, label, description) "
            "VALUES (:id, :code, :label, :description)"
        ),
        {
            "id": legacy_id,
            "code": "legacy",
            "label": "Legacy Topic",
            "description": "Migrated sessions without structured topics.",
        },
    )
    connection.execute(
        sa.text("UPDATE sessions SET topic_code = :code WHERE topic_code IS NULL"),
        {"code": "legacy"},
    )
    connection.execute(
        sa.text(
            "UPDATE sessions SET system_prompt = :prompt || ' Theme: ' || COALESCE(topic, 'General English') "
            "WHERE system_prompt IS NULL"
        ),
        {"prompt": _DEFAULT_PROMPT},
    )

    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.drop_column("topic")
        batch_op.alter_column("topic_code", existing_type=sa.String(length=32), nullable=False)
        batch_op.alter_column("system_prompt", existing_type=sa.Text(), nullable=False)
        batch_op.create_foreign_key(
            "fk_sessions_topic_code",
            "practice_topics",
            ["topic_code"],
            ["code"],
        )


def downgrade() -> None:
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("topic", sa.String(length=128), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE sessions SET topic = COALESCE(topic_code, 'general')")
    )

    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.drop_constraint("fk_sessions_topic_code", type_="foreignkey")
        batch_op.drop_column("topic_code")
        batch_op.drop_column("system_prompt")
        batch_op.alter_column("topic", existing_type=sa.String(length=128), nullable=False)

    op.drop_table("practice_topics")
