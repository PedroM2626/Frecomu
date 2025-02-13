"""Adiciona coluna reply_to na tabela message

Revision ID: 1071900bc575
Revises: 
Create Date: 2025-02-12 23:36:42.104497

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1071900bc575'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reply_to', sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_message_reply_to", "message", ["reply_to"], ["id"])


    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint("fk_message_reply_to", type_="foreignkey")
        batch_op.drop_column('reply_to')


    # ### end Alembic commands ###
