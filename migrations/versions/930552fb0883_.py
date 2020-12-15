"""empty message

Revision ID: 930552fb0883
Revises: 81f55f9c685c
Create Date: 2020-12-15 11:45:27.624867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '930552fb0883'
down_revision = '81f55f9c685c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.alter_column('artist', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=False)
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('artist', 'state',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'seeking_venue',
               existing_type=sa.BOOLEAN(),
               nullable=True)
    op.alter_column('artist', 'phone',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.alter_column('artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'facebook_link',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.alter_column('artist', 'city',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
