from fastapi import APIRouter,Request,HTTPException
from pydantic import BaseModel,Field
import asyncio
from app.core.config import DATA,model_directory,MODEL_ID,REVISION,DESKTOP
from app.ai.embeddings.siglip2 import provider
from app.db import store
router=APIRouter(prefix='/api/system')
@router.get('')
def system(request:Request):
    import platform
    return {'platform':platform.platform(),'model':MODEL_ID,'revision':REVISION,'model_available':(model_directory()/'model.safetensors').is_file(),'model_dir':str(model_directory()),'desktop':DESKTOP,'folder_picker_available':hasattr(request.app.state,'select_model_folder'),'device':provider.device,'cache_dir':str(DATA/'cache'),'cache_bytes':sum(p.stat().st_size for p in (DATA/'cache').glob('*.img')),'llm':'cloud-optional; no local LLM','embedding_options':[{'id':MODEL_ID,'status':'available'},{'id':'Qwen/Qwen3-VL-Embedding-2B','status':'not_installed_optional'}]}
@router.post('/cache/clear')
def clear():
    count=0
    for p in (DATA/'cache').glob('*.img'):p.unlink();count+=1
    return {'removed':count}


class ModelDirectoryRequest(BaseModel):
    path:str=Field(min_length=1,max_length=4096)

async def select_model_path(path):
    try:directory=await asyncio.to_thread(provider.select_directory,path)
    except (ValueError,OSError) as e:raise HTTPException(422,str(e))
    return {'path':str(directory),'model_available':True,'restart_required':False}

@router.put('/model/directory')
async def set_model_directory(req:ModelDirectoryRequest):
    return await select_model_path(req.path)

@router.post('/model/select')
async def choose_model_directory(request:Request):
    picker=getattr(request.app.state,'select_model_folder',None)
    if picker is None:raise HTTPException(409,'请手动填写模型目录；原生文件选择器仅在安装版中可用')
    path=await asyncio.to_thread(picker)
    if not path:return {'cancelled':True}
    return await select_model_path(path)
