"""Add unique constraint to users.email

Revision ID: d1c2b3a4e5f6
Revises: 1f2e3d4c5b6a
Create Date: 2026-05-21 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1c2b3a4e5f6'
down_revision: Union[str, Sequence[str], None] = '1f2e3d4c5b6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona constraint UNIQUE na coluna email da tabela usuarios"""
    op.create_unique_constraint('uq_usuarios_email', 'usuarios', ['email'], schema='aican')


def downgrade() -> None:
    """Remove constraint UNIQUE da coluna email"""
    op.drop_constraint('uq_usuarios_email', 'usuarios', schema='aican')
