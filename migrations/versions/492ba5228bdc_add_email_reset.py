"""add email reset

Revision ID: 492ba5228bdc
Revises: 5d14b82c0c06
Create Date: 2024-04-20 16:52:02.118179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '492ba5228bdc'
down_revision: Union[str, None] = '5d14b82c0c06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('reseter_need', sa.Column('email', sa.String(), nullable=False))
    op.create_unique_constraint(None, 'reseter_need', ['email'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'reseter_need', type_='unique')
    op.drop_column('reseter_need', 'email')
    # ### end Alembic commands ###
