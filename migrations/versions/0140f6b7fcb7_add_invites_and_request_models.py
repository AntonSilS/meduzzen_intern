"""Add invites and request models

Revision ID: 0140f6b7fcb7
Revises: be3e4c167d7e
Create Date: 2023-08-16 23:51:04.194623

"""
from alembic import op
import sqlalchemy as sa
from db.connect import Base


# revision identifiers, used by Alembic.
revision = '0140f6b7fcb7'
down_revision = 'be3e4c167d7e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('invitations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('sender_id', sa.Integer(), nullable=True),
    sa.Column('recipient_id', sa.Integer(), nullable=True),
    sa.Column('status_invite', sa.Enum('SENT', 'ACCEPTED', 'DECLINED', name='statusinvite'), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invitations_id'), 'invitations', ['id'], unique=False)
    op.create_index(op.f('ix_invitations_status_invite'), 'invitations', ['status_invite'], unique=False)
    op.create_table('join_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status_request', sa.Enum('SENT', 'ACCEPTED', 'DECLINED', name='statusrequest'), nullable=True),
    sa.ForeignKeyConstraint(['company_id'], ['company.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_join_requests_id'), 'join_requests', ['id'], unique=False)
    op.create_index(op.f('ix_join_requests_status_request'), 'join_requests', ['status_request'], unique=False)
    op.add_column('users', sa.Column('status_user', sa.String(length=50), nullable=True))
    op.drop_column('users', 'status')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('status', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('users', 'status_user')
    op.drop_index(op.f('ix_join_requests_status_request'), table_name='join_requests')
    op.drop_index(op.f('ix_join_requests_id'), table_name='join_requests')
    op.drop_table('join_requests')
    op.drop_index(op.f('ix_invitations_status_invite'), table_name='invitations')
    op.drop_index(op.f('ix_invitations_id'), table_name='invitations')
    op.drop_table('invitations')
    # ### end Alembic commands ###
