"""change status for user default value

Revision ID: e109265ff840
Revises: 94ee88eb5d45
Create Date: 2023-07-27 15:07:49.821808

"""
from alembic import op
import sqlalchemy as sa
from db.connect import Base


# revision identifiers, used by Alembic.
revision = 'e109265ff840'
down_revision = 'fbe9c3ef196b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'hash_password',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'hash_password',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###
