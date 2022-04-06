"""initial

Revision ID: a1791b1371ed
Revises: 
Create Date: 2021-05-05 11:42:24.126371

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.schema import UniqueConstraint

# revision identifiers, used by Alembic.
revision = 'a1791b1371ed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('lecture',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('code', sa.String(length=255), nullable=True, unique=True),
                    sa.Column('state', sa.Enum('active', 'complete'), nullable=False),
                    sa.Column('deleted', sa.Enum('active', 'deleted'), server_default='active', nullable=False),

                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('user',
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.PrimaryKeyConstraint('name')
                    )
    op.create_table('assignment',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('type', sa.Enum("user", "group"), nullable=False, server_default="user"),
                    sa.Column('lectid', sa.Integer(), nullable=True),
                    sa.Column('duedate', sa.DateTime(), nullable=True),
                    sa.Column('automatic_grading', sa.Enum('unassisted', 'auto', 'full_auto'),
                              server_default='unassisted', nullable=False),
                    sa.Column('points', sa.Integer(), nullable=False),
                    sa.Column('status', sa.Enum('created', 'pushed', 'released', 'fetching', 'fetched', 'complete'),
                              nullable=True),
                    sa.Column('deleted', sa.Enum('active', 'deleted'), server_default='active', nullable=False),
                    sa.Column('properties', sa.Text(), nullable=True, unique=False),

                    sa.ForeignKeyConstraint(['lectid'], ['lecture.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    UniqueConstraint('name', 'lectid', 'deleted', name='u_name_in_lect')
                    )
    op.create_table('takepart',
                    sa.Column('username', sa.String(length=255), nullable=False),
                    sa.Column('lectid', sa.Integer(), nullable=False),
                    sa.Column('role', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['lectid'], ['lecture.id'], ),
                    sa.ForeignKeyConstraint(['username'], ['user.name'], ),
                    sa.PrimaryKeyConstraint('username', 'lectid')
                    )

    op.create_table('group',
                    sa.Column('name', sa.String(length=255), nullable=False),
                    sa.Column('lectid', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['lectid'], ['lecture.id'], ),
                    sa.PrimaryKeyConstraint('name','lectid')
                    )
    op.create_table('partof',
                    sa.Column('username', sa.String(length=255), nullable=False),
                    sa.Column('groupname', sa.String(length=255), nullable=False),
                    sa.ForeignKeyConstraint(['groupname'], ['group.name'], ),
                    sa.ForeignKeyConstraint(['username'], ['user.name'], ),
                    sa.PrimaryKeyConstraint('username', 'groupname')
                    )

    op.create_table('submission',
                    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
                    sa.Column('date', sa.DateTime(), nullable=True),
                    sa.Column('auto_status', sa.Enum('pending', 'not_graded', 'automatically_graded', 'grading_failed'),
                              nullable=False),
                    sa.Column('manual_status', sa.Enum('not_graded', 'manually_graded', 'being_edited'),
                              nullable=False),
                    sa.Column('score', sa.Integer(), nullable=True),
                    sa.Column('assignid', sa.Integer(), nullable=True),
                    sa.Column('username', sa.String(length=255), nullable=True),
                    sa.Column('commit_hash', sa.String(length=40), nullable=False),
                    sa.Column('properties', sa.Text(), nullable=True, unique=False),
                    sa.Column('feedback_available', sa.Boolean(), nullable=False, server_default="false"),
                    sa.Column('logs', sa.Text(), nullable=True),
                    sa.ForeignKeyConstraint(['assignid'], ['assignment.id'], ),
                    sa.ForeignKeyConstraint(['username'], ['user.name'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submission')
    op.drop_table('takepart')
    op.drop_table('assignment')
    op.drop_table('user')
    op.drop_table('lecture')
    op.drop_table('group')
    # ### end Alembic commands ###
