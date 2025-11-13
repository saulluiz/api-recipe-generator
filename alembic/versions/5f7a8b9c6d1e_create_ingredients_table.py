"""create ingredients table

Revision ID: 5f7a8b9c6d1e
Revises: 3ee02a555bd4
Create Date: 2025-11-12 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5f7a8b9c6d1e'
down_revision = '3ee02a555bd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela ingredients
    op.create_table(
        'ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('quantity', sa.String(length=50), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índice no user_id para melhor performance
    op.create_index(op.f('ix_ingredients_user_id'), 'ingredients', ['user_id'], unique=False)


def downgrade() -> None:
    # Remover índice
    op.drop_index(op.f('ix_ingredients_user_id'), table_name='ingredients')
    
    # Remover tabela
    op.drop_table('ingredients')
