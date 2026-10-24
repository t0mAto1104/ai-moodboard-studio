from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from app.ai.llm.provider_manager import manager,LLMSettings
from app.ai.llm.model_registry import registry
from app.db import store
router=APIRouter(prefix='/api')
class Prompt(BaseModel):prompt:str=Field(min_length=1,max_length=3000)
@router.post('/intent/parse')
async def parse(p:Prompt):
    intent,mode,warning=await manager.parse(p.prompt);return {'intent':intent.model_dump(),'mode':mode,'warning':warning}
@router.get('/llm/settings')
def settings():return manager.public_settings()
@router.put('/llm/settings')
def save(s:LLMSettings):
    try:return manager.save(s)
    except ValueError as e:raise HTTPException(400,str(e))
@router.get('/llm/models')
async def models():return await registry.list(manager.settings())
@router.post('/llm/test')
async def test():
    try:
        i,mode,w=await manager.parse('minimal ceramic design',force=True);return {'status':'ok','mode':mode}
    except ValueError as e:raise HTTPException(400,str(e))
@router.get('/llm/usage')
def usage():return store.all_rows('llm_usage')
