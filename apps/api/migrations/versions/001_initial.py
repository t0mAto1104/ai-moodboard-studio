"""Initial entity store, with versioned schema."""
from alembic import op
import sqlalchemy as sa
revision='001'
down_revision=None
NAMES=('projects','image_assets','project_assets','search_sessions','search_queries','provider_responses_cache','embeddings','layout_items','background_jobs','export_records','settings','llm_usage')
def upgrade():
    for name in NAMES:op.create_table(name,sa.Column('id',sa.String,primary_key=True),sa.Column('payload',sa.JSON,nullable=False),sa.Column('updated_at',sa.Float,nullable=False))
def downgrade():
    for name in reversed(NAMES):op.drop_table(name)
