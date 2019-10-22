"""empty message

Revision ID: b97e078db5fc
Revises: 98d04fe73be7
Create Date: 2017-11-23 16:31:09.476423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b97e078db5fc'
down_revision = '98d04fe73be7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('input_loose', sa.Column('time_cut', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('input_loose', 'time_cut')
    # ### end Alembic commands ###