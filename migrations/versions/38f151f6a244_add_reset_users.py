"""add reset users

Revision ID: 38f151f6a244
Revises: f31dbb7a4110
Create Date: 2024-04-03 19:29:29.825392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38f151f6a244'
down_revision: Union[str, None] = 'f31dbb7a4110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reseter_need',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('number', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('number')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reseter_need')
    # ### end Alembic commands ###
