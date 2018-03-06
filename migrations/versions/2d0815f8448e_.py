"""empty message

Revision ID: 2d0815f8448e
Revises: 
Create Date: 2017-02-07 15:53:57.931449

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2d0815f8448e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('entries')
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=256),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password',
               existing_type=sa.VARCHAR(length=256),
               nullable=False)
    op.create_table('entries',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('userid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('title', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('link', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('body', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('category', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('image_url', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('tags', postgresql.ARRAY(TEXT()), autoincrement=False, nullable=True),
    sa.Column('likes', sa.INTEGER(), server_default=sa.text(u'0'), autoincrement=False, nullable=True),
    sa.Column('views', sa.INTEGER(), server_default=sa.text(u'0'), autoincrement=False, nullable=True),
    sa.Column('published', sa.BOOLEAN(), server_default=sa.text(u'true'), autoincrement=False, nullable=True),
    sa.Column('modified', postgresql.TIMESTAMP(), server_default=sa.text(u'now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'entries_pkey')
    )
    # ### end Alembic commands ###
