from alembic import context
from app.db.store import engine, metadata
with engine.begin() as connection:
    context.configure(connection=connection, target_metadata=metadata)
    with context.begin_transaction():context.run_migrations()
