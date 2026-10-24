import os,tempfile
os.environ['MOODBOARD_DATA_DIR']=tempfile.mkdtemp(prefix='moodboard-test-')
from app.db.store import metadata,engine
metadata.create_all(engine)
