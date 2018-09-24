"""subscriptions init

Revision ID: 86f1afe9c59b
Revises: 6c89942d4124
Create Date: 2018-07-19 17:03:28.410700

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '86f1afe9c59b'
down_revision = '6c89942d4124'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'is_anonymous')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('is_anonymous', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.add_column('user', sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))
    op.drop_table('subscription')
    # ### end Alembic commands ###
