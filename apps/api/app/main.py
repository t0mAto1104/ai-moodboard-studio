from fastapi import FastAPI
from sqlalchemy import text
from app.db.store import engine
import logging
for logger in ('httpx','httpcore','LiteLLM','LiteLLM Router','LiteLLM Proxy'):logging.getLogger(logger).setLevel(logging.CRITICAL)
from contextlib import asynccontextmanager
from app.jobs.queue import queue
@asynccontextmanager
async def lifespan(app):
    queue.recover()
    yield
    await queue.shutdown()
app=FastAPI(title='AI Mood Board Studio',version='0.1.0',lifespan=lifespan)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    return JSONResponse(status_code=422,content={'detail':[{'loc':list(e['loc']),'msg':e['msg'],'type':e['type']} for e in exc.errors()]})
@app.get('/api/health')
def health():
    with engine.connect() as c:c.execute(text('SELECT 1'))
    return {'status':'ok','database':'ok','version':'0.1.0'}
from app.security.local import LocalOnlyMiddleware
from app.routers.search import router as search_router
app.add_middleware(LocalOnlyMiddleware)
app.include_router(search_router)
from app.routers.assets import router as assets_router
app.include_router(assets_router)
from app.routers.llm import router as llm_router
app.include_router(llm_router)
from app.routers.projects import router as projects_router
from app.routers.exports import router as exports_router
from app.routers.system import router as system_router
app.include_router(projects_router)
app.include_router(exports_router)
app.include_router(system_router)
from app.routers.library import router as library_router
app.include_router(library_router)
from fastapi.staticfiles import StaticFiles
from app.core.config import ROOT
if (ROOT/'apps/web/dist').exists():app.mount('/',StaticFiles(directory=ROOT/'apps/web/dist',html=True),name='web')
