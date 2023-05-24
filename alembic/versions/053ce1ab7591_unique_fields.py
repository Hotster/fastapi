"""Unique fields

Revision ID: 053ce1ab7591
Revises: 6daacd20e9a8
Create Date: 2023-05-23 20:43:16.699810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '053ce1ab7591'
down_revision = '6daacd20e9a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'app_user', ['email'])
    op.create_unique_constraint(None, 'app_user', ['username'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'app_user', type_='unique')
    op.drop_constraint(None, 'app_user', type_='unique')
    # ### end Alembic commands ###