"""add User new fields

Revision ID: 3b7cf7d82ca9
Revises: fbe9c3ef196b
Create Date: 2023-07-24 19:31:38.533119

"""
from alembic import op
import sqlalchemy as sa
from db.connect import Base


# revision identifiers, used by Alembic.
revision = '3b7cf7d82ca9'
down_revision = 'fbe9c3ef196b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
