"""empty message

Revision ID: 4d87b349b7de
Revises: 
Create Date: 2017-11-21 14:04:44.771669

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4d87b349b7de'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('input_loose',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('input_loose_id', sa.String(length=50), nullable=False),
    sa.Column('user_id', sa.String(length=40), nullable=False),
    sa.Column('code_number', sa.String(length=40), nullable=False),
    sa.Column('check_color', sa.String(length=40), nullable=False),
    sa.Column('feel', sa.String(length=40), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.Column('head', sa.String(length=40), nullable=False),
    sa.Column('middle', sa.String(length=40), nullable=False),
    sa.Column('tail', sa.String(length=40), nullable=False),
    sa.Column('speed', sa.Integer(), nullable=True),
    sa.Column('length', sa.Integer(), nullable=True),
    sa.Column('materials_count', sa.Integer(), nullable=False),
    sa.Column('act_count', sa.Integer(), nullable=False),
    sa.Column('width_cut', sa.Integer(), nullable=False),
    sa.Column('first_length', sa.String(length=40), nullable=False),
    sa.Column('second_length', sa.String(length=40), nullable=False),
    sa.Column('third_length', sa.String(length=40), nullable=False),
    sa.Column('loose_time', sa.DateTime(), nullable=True),
    sa.Column('loose_date', sa.DateTime(), nullable=True),
    sa.Column('looser', sa.String(length=40), nullable=False),
    sa.Column('extend', postgresql.JSONB(astext_type=Text()), nullable=True),
    sa.PrimaryKeyConstraint('input_loose_id'),
    sa.UniqueConstraint('code_number')
    )
    op.create_table('loose_info',
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('loose_info_id', sa.String(length=50), nullable=False),
    sa.Column('code_number', sa.String(length=40), nullable=False),
    sa.Column('user_id', sa.String(length=40), nullable=False),
    sa.Column('order_num', sa.String(length=40), nullable=False),
    sa.Column('cloth_num', sa.String(length=40), nullable=False),
    sa.Column('species_name', sa.String(length=40), nullable=False),
    sa.Column('color_num', sa.String(length=40), nullable=False),
    sa.Column('color_name', sa.String(length=40), nullable=False),
    sa.Column('count', sa.Integer(), nullable=False),
    sa.Column('produ_line', sa.String(length=40), nullable=False),
    sa.Column('door', sa.String(length=40), nullable=False),
    sa.Column('cyli_num', sa.String(length=40), nullable=False),
    sa.Column('wegiht', sa.Integer(), nullable=False),
    sa.Column('volu_num', sa.String(length=40), nullable=False),
    sa.Column('loose', sa.Boolean(), nullable=False),
    sa.Column('extend', postgresql.JSONB(astext_type=Text()), nullable=True),
    sa.PrimaryKeyConstraint('loose_info_id'),
    sa.UniqueConstraint('code_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('loose_info')
    op.drop_table('input_loose')
    # ### end Alembic commands ###
