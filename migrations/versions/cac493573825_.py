"""empty message

Revision ID: cac493573825
Revises: 
Create Date: 2021-07-31 23:30:29.818296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cac493573825'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('repl')
    op.drop_table('discussion')
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_category_name'), ['name'])

    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_tag_name'), ['name'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_user_email'), ['email'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_user_email'), type_='unique')

    with op.batch_alter_table('tag', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_tag_name'), type_='unique')

    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_category_name'), type_='unique')

    op.create_table('discussion',
    sa.Column('replier_id', sa.INTEGER(), nullable=False),
    sa.Column('replied_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['replied_id'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['replier_id'], ['comment.id'], ),
    sa.PrimaryKeyConstraint('replier_id', 'replied_id')
    )
    op.create_table('repl',
    sa.Column('replier_id', sa.INTEGER(), nullable=False),
    sa.Column('replied_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['replied_id'], ['comment.id'], ),
    sa.ForeignKeyConstraint(['replier_id'], ['comment.id'], ),
    sa.PrimaryKeyConstraint('replier_id', 'replied_id')
    )
    # ### end Alembic commands ###
