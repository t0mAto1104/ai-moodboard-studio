import time
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, JSON, select, delete
from app.core.config import DATA
engine = create_engine('sqlite:///' + str(DATA / 'studio.sqlite'), connect_args={'check_same_thread': False})
metadata = MetaData()
TABLES = {name: Table(name, metadata, Column('id', String, primary_key=True), Column('payload', JSON, nullable=False), Column('updated_at', Float, nullable=False)) for name in ('projects','image_assets','project_assets','search_sessions','search_queries','provider_responses_cache','embeddings','layout_items','background_jobs','export_records','settings','llm_usage','library_tags','favorites','download_records')}
def put(table, key, payload):
    with engine.begin() as c:
        c.execute(delete(TABLES[table]).where(TABLES[table].c.id == key))
        c.execute(TABLES[table].insert().values(id=key, payload=payload, updated_at=time.time()))
def get(table, key):
    with engine.connect() as c:
        row=c.execute(select(TABLES[table].c.payload).where(TABLES[table].c.id==key)).first()
        return row[0] if row else None
def all_rows(table):
    with engine.connect() as c:
        return [r[0] for r in c.execute(select(TABLES[table].c.payload).order_by(TABLES[table].c.updated_at.desc()))]
def remove(table,key):
    with engine.begin() as c:c.execute(delete(TABLES[table]).where(TABLES[table].c.id==key))
