"""Initial database

Revision ID: 9810f01535bb
Revises: 
Create Date: 2023-01-12 13:50:47.080227

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9810f01535bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=100), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=True),
    sa.Column('scopes', sa.Text(), nullable=False),
    sa.Column('token', sa.String(length=64), nullable=False),
    sa.Column('extra', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_stores_key'), ['key'], unique=False)

    op.create_table('discount_codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('code_id', sa.BigInteger(), nullable=True),
    sa.Column('code_stamp', sa.SmallInteger(), nullable=True, comment='0: Product, 1: Order, 2: Shipping'),
    sa.Column('code_type', sa.SmallInteger(), nullable=True, comment='0: Manually, 1: Automatic'),
    sa.Column('code_name', sa.String(length=255), nullable=True),
    sa.Column('method', sa.SmallInteger(), nullable=True, comment='Percentage: 1, Fixed: 0'),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('combination', sa.SmallInteger(), nullable=True, comment='Calculate by code_stamp'),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('extra', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('discount_codes', schema=None) as batch_op:
        batch_op.create_index('store_code_id', ['store_id', 'code_id'], unique=False)

    op.create_table('store_themes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('theme_id', sa.BigInteger(), nullable=True),
    sa.Column('theme_name', sa.String(length=128), nullable=True),
    sa.Column('published', sa.SmallInteger(), nullable=True),
    sa.Column('version', sa.String(length=32), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('store_themes', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_store_themes_store_id'), ['store_id'], unique=False)

    op.create_table('webhooks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('store_id', sa.Integer(), nullable=True),
    sa.Column('webhook_id', sa.BigInteger(), nullable=True, comment='Webhook ID'),
    sa.Column('target', sa.String(length=24), nullable=True, comment='Action Target'),
    sa.Column('action', sa.String(length=24), nullable=True, comment='Action'),
    sa.Column('data', sa.Text(length=64000), nullable=True, comment='JSON string -> 64kb medium text for MYSQL/MariaDB'),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('webhooks', schema=None) as batch_op:
        batch_op.create_index('store_webhook', ['store_id', 'webhook_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('webhooks', schema=None) as batch_op:
        batch_op.drop_index('store_webhook')

    op.drop_table('webhooks')
    with op.batch_alter_table('store_themes', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_store_themes_store_id'))

    op.drop_table('store_themes')
    with op.batch_alter_table('discount_codes', schema=None) as batch_op:
        batch_op.drop_index('store_code_id')

    op.drop_table('discount_codes')
    with op.batch_alter_table('stores', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_stores_key'))

    op.drop_table('stores')
    # ### end Alembic commands ###