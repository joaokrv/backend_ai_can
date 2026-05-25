"""Remove coluna frequencia_semana - substituida por dias_disponiveis

Revision ID: b1c2d3e4f5a6
Revises: f8a9b0c1d2e3
Create Date: 2026-05-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1c2d3e4f5a6'
down_revision = 'f8a9b0c1d2e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('usuarios', 'frequencia_semana', schema='aican')


def downgrade() -> None:
    op.add_column(
        'usuarios',
        sa.Column('frequencia_semana', sa.String(), nullable=True),
        schema='aican',
    )
