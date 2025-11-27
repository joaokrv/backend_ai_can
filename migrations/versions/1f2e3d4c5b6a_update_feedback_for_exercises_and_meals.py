"""update_feedback_for_exercises_and_meals

Revision ID: 1f2e3d4c5b6a
Revises: a0747ea43014
Create Date: 2025-11-26 21:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '1f2e3d4c5b6a'
down_revision: Union[str, Sequence[str], None] = 'a0747ea43014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Atualiza tabela feedbacks para suportar exercícios E refeições."""
    
    op.add_column('feedbacks', 
        sa.Column('tipo', sa.String(length=20), nullable=True),  
        schema='aican'
    )
    op.add_column('feedbacks', 
        sa.Column('item_nome', sa.String(length=255), nullable=True), 
        schema='aican'
    )
    op.add_column('feedbacks', 
        sa.Column('created_at', sa.DateTime(), nullable=True), 
        schema='aican'
    )
    
    op.execute("""
        UPDATE aican.feedbacks 
        SET tipo = 'exercicio',
            created_at = NOW()
        WHERE tipo IS NULL
    """)
    
    op.execute("""
        UPDATE aican.feedbacks f
        SET item_nome = ce.nome
        FROM aican.catalogo_exercicios ce
        WHERE f.exercicio_id = ce.id 
        AND f.item_nome IS NULL
    """)
    
    op.alter_column('feedbacks', 'tipo',
        existing_type=sa.String(length=20),
        nullable=False,
        schema='aican'
    )
    op.alter_column('feedbacks', 'item_nome',
        existing_type=sa.String(length=255),
        nullable=False,
        schema='aican'
    )
    op.alter_column('feedbacks', 'created_at',
        existing_type=sa.DateTime(),
        nullable=False,
        schema='aican'
    )
    
    op.create_index(op.f('ix_aican_feedbacks_tipo'), 'feedbacks', ['tipo'], unique=False, schema='aican')
    op.create_index(op.f('ix_aican_feedbacks_item_nome'), 'feedbacks', ['item_nome'], unique=False, schema='aican')
    op.create_index(op.f('ix_aican_feedbacks_usuario_id'), 'feedbacks', ['usuario_id'], unique=False, schema='aican')
    
    op.drop_constraint('feedbacks_exercicio_id_fkey', 'feedbacks', schema='aican', type_='foreignkey')
    op.drop_column('feedbacks', 'exercicio_id', schema='aican')


def downgrade() -> None:
    """Reverte alterações na tabela feedbacks."""
    
    op.add_column('feedbacks',
        sa.Column('exercicio_id', sa.INTEGER(), nullable=True),
        schema='aican'
    )
    
    op.execute("""
        UPDATE aican.feedbacks f
        SET exercicio_id = ce.id
        FROM aican.catalogo_exercicios ce
        WHERE f.item_nome = ce.nome 
        AND f.tipo = 'exercicio'
    """)
    
    op.create_foreign_key(
        'feedbacks_exercicio_id_fkey',
        'feedbacks', 'catalogo_exercicios',
        ['exercicio_id'], ['id'],
        source_schema='aican',
        referent_schema='aican'
    )
    
    op.drop_index(op.f('ix_aican_feedbacks_usuario_id'), table_name='feedbacks', schema='aican')
    op.drop_index(op.f('ix_aican_feedbacks_item_nome'), table_name='feedbacks', schema='aican')
    op.drop_index(op.f('ix_aican_feedbacks_tipo'), table_name='feedbacks', schema='aican')
    
    op.drop_column('feedbacks', 'created_at', schema='aican')
    op.drop_column('feedbacks', 'item_nome', schema='aican')
    op.drop_column('feedbacks', 'tipo', schema='aican')
