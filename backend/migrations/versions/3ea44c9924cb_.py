"""GWP Tables

Revision ID: 3ea44c9924cb
Revises: 9810f01535bb
Create Date: 2023-02-07 14:01:15.243844

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3ea44c9924cb'
down_revision = '9810f01535bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gift_with_purchases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('mid', sa.BigInteger(), nullable=True),
    sa.Column('method', sa.SmallInteger(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('force_remove', sa.SmallInteger(), nullable=True),
    sa.Column('secret_number', sa.Integer(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('gift_with_purchases', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_gift_with_purchases_store_id'), ['store_id'], unique=False)

    op.create_table('gift_with_purchase_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('target', sa.SmallInteger(), nullable=True, comment='1: Target, 2: Pre requirements'),
    sa.Column('pid', sa.BigInteger(), nullable=True),
    sa.Column('vid', sa.BigInteger(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.Column('handle', sa.String(length=255), nullable=True),
    sa.Column('image', sa.String(length=512), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['gift_with_purchases.id'], ),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('gift_with_purchase_items', schema=None) as batch_op:
        batch_op.create_index('store_parent_id', ['store_id', 'parent_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('gift_with_purchase_items', schema=None) as batch_op:
        batch_op.drop_index('store_parent_id')

    op.drop_table('gift_with_purchase_items')
    with op.batch_alter_table('gift_with_purchases', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_gift_with_purchases_store_id'))

    op.drop_table('gift_with_purchases')
    # ### end Alembic commands ###