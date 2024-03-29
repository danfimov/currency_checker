"""Unique pair - token and source

Revision ID: 3ef8c14c50b3
Revises: 0f1688dfb6d2
Create Date: 2024-02-08 15:50:26.594454

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '3ef8c14c50b3'
down_revision: Union[str, None] = '0f1688dfb6d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq__accounts__token_source'), 'accounts', ['token', 'source'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq__accounts__token_source'), 'accounts', type_='unique')
    # ### end Alembic commands ###
