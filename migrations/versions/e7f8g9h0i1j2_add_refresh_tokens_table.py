"""Add refresh_tokens table

Revision ID: e7f8g9h0i1j2
Revises: d1c2b3a4e5f6
Create Date: 2026-05-21 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f8g9h0i1j2'
down_revision: Union[str, Sequence[str], None] = 'd1c2b3a4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria tabela refresh_tokens com índices apropriados"""
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('family_id', sa.String(length=36), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['aican.usuarios.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token_hash', name='uq_refresh_tokens_token_hash'),
        schema='aican',
    )
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'], schema='aican')
    op.create_index('ix_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'], schema='aican')
    op.create_index('ix_refresh_tokens_family_id', 'refresh_tokens', ['family_id'], schema='aican')
    op.create_index('ix_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'], schema='aican')


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_expires_at', table_name='refresh_tokens', schema='aican')
    op.drop_index('ix_refresh_tokens_family_id', table_name='refresh_tokens', schema='aican')
    op.drop_index('ix_refresh_tokens_token_hash', table_name='refresh_tokens', schema='aican')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens', schema='aican')
    op.drop_table('refresh_tokens', schema='aican')
