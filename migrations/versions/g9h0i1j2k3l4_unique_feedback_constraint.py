"""Add UNIQUE constraint to feedback (usuario_id, tipo, item_nome).

Revision ID: g9h0i1j2k3l4
Revises: f8a9b0c1d2e3
Create Date: 2026-05-22 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "g9h0i1j2k3l4"
down_revision = "f8a9b0c1d2e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Deletar duplicatas: manter apenas a linha mais recente por (usuario_id, tipo, item_nome)
    op.execute("""
        DELETE FROM aican.feedbacks f
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM aican.feedbacks
            GROUP BY usuario_id, tipo, item_nome
        )
    """)
    
    # Adicionar UNIQUE constraint
    op.create_unique_constraint(
        "uq_feedback_user_tipo_item",
        "feedbacks",
        ["usuario_id", "tipo", "item_nome"],
        schema="aican"
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_feedback_user_tipo_item",
        "feedbacks",
        schema="aican"
    )
