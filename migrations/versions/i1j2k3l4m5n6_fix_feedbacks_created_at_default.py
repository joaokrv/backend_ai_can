"""Fix feedbacks.created_at: add DEFAULT now() and merge branch heads.

Revision ID: i1j2k3l4m5n6
Revises: b1c2d3e4f5a6, h0i1j2k3l4m5
Create Date: 2026-05-25 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "i1j2k3l4m5n6"
down_revision = ("b1c2d3e4f5a6", "h0i1j2k3l4m5")
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Preencher NULLs existentes antes de setar NOT NULL + DEFAULT
    op.execute("UPDATE aican.feedbacks SET created_at = now() WHERE created_at IS NULL")

    # Setar DEFAULT no banco (era ausente apesar de server_default no model)
    op.execute("ALTER TABLE aican.feedbacks ALTER COLUMN created_at SET DEFAULT now()")

    # Garantir NOT NULL (ja deve estar, mas idempotente)
    op.execute("ALTER TABLE aican.feedbacks ALTER COLUMN created_at SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE aican.feedbacks ALTER COLUMN created_at DROP DEFAULT")
