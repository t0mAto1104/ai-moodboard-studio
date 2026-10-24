"""Saved inspiration, custom tags and manual download audit records."""
from alembic import op
import sqlalchemy as sa
revision='002'
down_revision='001'
NAMES=('library_tags','favorites','download_records')
def upgrade():
    for name in NAMES:
        op.create_table(name,sa.Column('id',sa.String,primary_key=True),sa.Column('payload',sa.JSON,nullable=False),sa.Column('updated_at',sa.Float,nullable=False))
def downgrade():
    for name in reversed(NAMES):op.drop_table(name)
