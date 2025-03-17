"""Change parts_list to JSON type

Revision ID: 64f87188e42d
Revises: 65db55996a0b
Create Date: 2025-03-17 15:47:07.692251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64f87188e42d'
down_revision = '65db55996a0b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column(
            'parts_list',
            existing_type=sa.String(),
            type_=sa.dialects.postgresql.JSON(),
            postgresql_using='parts_list::json'
        )


def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.alter_column(
            'parts_list',
            existing_type=sa.dialects.postgresql.JSON(),
            type_=sa.String()
        )
