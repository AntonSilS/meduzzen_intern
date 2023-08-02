"""change name coloumn password

Revision ID: caeba61d551b
Revises: 67bf796321aa
Create Date: 2023-07-30 23:11:05.958175

"""
from alembic import op
import sqlalchemy as sa
from db.connect import Base


# revision identifiers, used by Alembic.
revision = 'caeba61d551b'
down_revision = '67bf796321aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('password', sa.String(), nullable=False))
    op.drop_constraint('users_username_key', 'users', type_='unique')
    op.drop_column('users', 'hash_password')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('hash_password', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    op.drop_column('users', 'password')
    # ### end Alembic commands ###