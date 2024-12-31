"""add content column to posts table

Revision ID: ba489e5cb396
Revises: cc92a926f70c
Create Date: 2024-12-29 10:54:34.413179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba489e5cb396'
down_revision: Union[str, None] = 'cc92a926f70c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # op.create_table('posts',sa.Column('id',sa.Integer(),nullable=False,primary_key=True),
    #                 sa.Column('title',sa.String(),nullable=False))
    op.add_column('posts',sa.Column('content',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
