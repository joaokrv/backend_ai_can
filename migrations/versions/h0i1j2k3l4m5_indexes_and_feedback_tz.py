"""Add composite indexes and convert feedback.created_at to TIMESTAMPTZ.

Revision ID: h0i1j2k3l4m5
Revises: g9h0i1j2k3l4
Create Date: 2026-05-22 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "h0i1j2k3l4m5"
down_revision = "g9h0i1j2k3l4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Indices compostos para queries WHERE usuario_id AND created_at (stats temporais, paginacao)
    op.create_index("ix_planos_usuario_created", "planos", ["usuario_id", "created_at"], schema="aican")
    op.create_index("ix_feedbacks_usuario_created", "feedbacks", ["usuario_id", "created_at"], schema="aican")
    
    # Converter feedback.created_at para TIMESTAMPTZ (consistencia com planos)
    op.execute("""
        ALTER TABLE aican.feedbacks 
        ALTER COLUMN created_at TYPE TIMESTAMPTZ 
        USING created_at AT TIME ZONE 'UTC'
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE aican.feedbacks 
        ALTER COLUMN created_at TYPE TIMESTAMP
    """)
    op.drop_index("ix_feedbacks_usuario_created", "feedbacks", schema="aican")
    op.drop_index("ix_planos_usuario_created", "planos", schema="aican")
