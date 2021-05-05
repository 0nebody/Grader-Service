"""initial

Revision ID: 128484503600
Revises: a1791b1371ed
Create Date: 2021-05-05 11:44:00.045511

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '128484503600'
down_revision = 'a1791b1371ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.alter_column('score',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('submission', schema=None) as batch_op:
        batch_op.alter_column('score',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
