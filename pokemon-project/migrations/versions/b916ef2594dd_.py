"""empty message

Revision ID: b916ef2594dd
Revises: 
Create Date: 2023-08-07 23:09:49.801100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b916ef2594dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('pokemon',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('rank', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('type_1', sa.Text(), nullable=False),
    sa.Column('type_2', sa.Text(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=False),
    sa.Column('hp', sa.Integer(), nullable=False),
    sa.Column('attack', sa.Integer(), nullable=False),
    sa.Column('defense', sa.Integer(), nullable=False),
    sa.Column('sp_atk', sa.Integer(), nullable=False),
    sa.Column('sp_def', sa.Integer(), nullable=False),
    sa.Column('speed', sa.Integer(), nullable=False),
    sa.Column('generation', sa.Integer(), nullable=False),
    sa.Column('legendary', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('pokemon')
    # ### end Alembic commands ###
