"""add field email

Revision ID: fe664b9dad82
Revises: 01cbbb8a438c
Create Date: 2024-04-04 15:40:22.168862

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe664b9dad82'
down_revision: Union[str, None] = '01cbbb8a438c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reseter_need', sa.Column('username', sa.String(), nullable=False))
    op.drop_constraint('reseter_need_number_key', 'reseter_need', type_='unique')
    op.create_unique_constraint(None, 'reseter_need', ['username'])
    op.drop_column('reseter_need', 'number')
    op.add_column('users', sa.Column('email', sa.String(), nullable=False))
    op.drop_constraint('users_number_key', 'users', type_='unique')
    op.create_unique_constraint(None, 'users', ['email'])
    op.drop_column('users', 'number')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'users', type_='unique')
    op.create_unique_constraint('users_number_key', 'users', ['number'])
    op.drop_column('users', 'email')
    op.add_column('reseter_need', sa.Column('number', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'reseter_need', type_='unique')
    op.create_unique_constraint('reseter_need_number_key', 'reseter_need', ['number'])
    op.drop_column('reseter_need', 'username')
    # ### end Alembic commands ###