"""Foundation Block A — Expansão de modelos, sanitizers e macros

Revision ID: f8a9b0c1d2e3
Revises: e7f8g9h0i1j2
Create Date: 2026-05-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'f8a9b0c1d2e3'
down_revision = 'e7f8g9h0i1j2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adicionar 9 novas colunas ao usuarios
    op.add_column('usuarios', sa.Column('sexo', sa.String(2), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('dias_disponiveis', postgresql.ARRAY(sa.String(10)), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('duracao_sessao', sa.Integer(), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('restricoes_alimentares', postgresql.ARRAY(sa.String(30)), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('lesoes_cuidados', sa.Text(), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('nivel_experiencia', sa.String(20), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('onboarding_completo', sa.Boolean(), server_default='false', nullable=False), schema='aican')
    op.add_column('usuarios', sa.Column('aceite_termos_at', sa.DateTime(timezone=True), nullable=True), schema='aican')
    op.add_column('usuarios', sa.Column('aceite_termos_versao', sa.String(10), nullable=True), schema='aican')

    # 2. Alterações em planos: FK + status + explicacao_ia + created_at com timezone
    # Primeiro, alterar usuario_id para NOT NULL
    op.alter_column('planos', 'usuario_id',
               existing_type=sa.INTEGER(),
               nullable=False,
               schema='aican')

    # Criar FK explícita com CASCADE
    op.create_foreign_key(
        'fk_planos_usuario_id',
        'planos', 'usuarios',
        ['usuario_id'], ['id'],
        ondelete='CASCADE',
        source_schema='aican', referent_schema='aican',
    )

    # Adicionar novas colunas em planos
    op.add_column('planos', sa.Column('status', sa.String(20), server_default='ativo', nullable=False), schema='aican')
    op.add_column('planos', sa.Column('explicacao_ia', sa.Text(), nullable=True), schema='aican')
    # Nota: created_at já existe no modelo desde a criação da tabela, apenas atualizamos se necessário
    # op.add_column('planos', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), schema='aican')

    # Criar índice em status
    op.create_index('ix_planos_status', 'planos', ['status'], schema='aican')

    # 3. Adicionar macros em plano_refeicoes e catalogo_refeicoes
    for tabela in ['plano_refeicoes', 'catalogo_refeicoes']:
        op.add_column(tabela, sa.Column('calorias', sa.Integer(), nullable=True), schema='aican')
        op.add_column(tabela, sa.Column('proteina_g', sa.Float(), nullable=True), schema='aican')
        op.add_column(tabela, sa.Column('carboidrato_g', sa.Float(), nullable=True), schema='aican')
        op.add_column(tabela, sa.Column('gordura_g', sa.Float(), nullable=True), schema='aican')
        op.add_column(tabela, sa.Column('macros_estimados', sa.Boolean(), server_default='true', nullable=False), schema='aican')


def downgrade() -> None:
    # Reverter em ordem inversa

    # 1. Remover colunas de macros
    for tabela in ['plano_refeicoes', 'catalogo_refeicoes']:
        op.drop_column(tabela, 'macros_estimados', schema='aican')
        op.drop_column(tabela, 'gordura_g', schema='aican')
        op.drop_column(tabela, 'carboidrato_g', schema='aican')
        op.drop_column(tabela, 'proteina_g', schema='aican')
        op.drop_column(tabela, 'calorias', schema='aican')

    # 2. Remover índice e colunas de planos
    op.drop_index('ix_planos_status', schema='aican')
    # Não removemos created_at pois não foi adicionado nesta migration
    op.drop_column('planos', 'explicacao_ia', schema='aican')
    op.drop_column('planos', 'status', schema='aican')

    # Remover FK
    op.drop_constraint('fk_planos_usuario_id', 'planos', schema='aican', type_='foreignkey')

    # Revert usuario_id to nullable
    op.alter_column('planos', 'usuario_id',
               existing_type=sa.INTEGER(),
               nullable=True,
               schema='aican')

    # 3. Remover colunas de usuarios
    op.drop_column('usuarios', 'aceite_termos_versao', schema='aican')
    op.drop_column('usuarios', 'aceite_termos_at', schema='aican')
    op.drop_column('usuarios', 'onboarding_completo', schema='aican')
    op.drop_column('usuarios', 'nivel_experiencia', schema='aican')
    op.drop_column('usuarios', 'lesoes_cuidados', schema='aican')
    op.drop_column('usuarios', 'restricoes_alimentares', schema='aican')
    op.drop_column('usuarios', 'duracao_sessao', schema='aican')
    op.drop_column('usuarios', 'dias_disponiveis', schema='aican')
    op.drop_column('usuarios', 'sexo', schema='aican')
