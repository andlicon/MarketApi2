"""empty message

Revision ID: 99a765f9778f
Revises: 7c9f52b33a88
Create Date: 2023-09-18 11:16:03.499208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99a765f9778f'
down_revision = '7c9f52b33a88'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('amount')

    with op.batch_alter_table('product_order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product_order', schema=None) as batch_op:
        batch_op.drop_column('amount')

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('amount', sa.INTEGER(), autoincrement=False, nullable=False))

    # ### end Alembic commands ###