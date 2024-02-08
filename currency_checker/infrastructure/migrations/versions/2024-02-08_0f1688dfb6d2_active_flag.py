"""Flag that account active

Revision ID: 0f1688dfb6d2
Revises: 0e6800259bd9
Create Date: 2024-02-08 15:43:52.654381

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '0f1688dfb6d2'
down_revision: Union[str, None] = '0e6800259bd9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('accounts', sa.Column('active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts', 'active')
    # ### end Alembic commands ###