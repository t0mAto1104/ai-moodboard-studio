from typing import Literal
from pydantic import BaseModel
from fastapi import APIRouter,HTTPException
from fastapi.responses import FileResponse
from app.routers.projects import project
from app.exports.render import export_project
from app.jobs.queue import queue
from app.db import store
from app.core.config import DATA
router=APIRouter(prefix='/api')
class ExportRequest(BaseModel):format:Literal['png','pdf']='png'
@router.post('/projects/{id}/export')
async def export(id:str,r:ExportRequest):
    p=project(id)
    async def work(progress):
        progress(progress=10);return await export_project(p,r.format)
    return {'job_id':queue.start(work)}
@router.get('/exports/{id}')
def download(id:str):
    e=store.get('export_records',id)
    if not e:raise HTTPException(404)
    return FileResponse(DATA/'exports'/e['filename'],filename='moodboard-'+e['format']+'.zip')
