from fastapi import APIRouter,HTTPException
from app.schemas.models import SearchRequest
from app.providers.registry import PROVIDERS
from app.jobs.queue import queue
from app.pipeline.retrieval import retrieve
from app.db import store
router=APIRouter(prefix='/api')
@router.get('/providers')
def providers():
    from app.ai.llm.credential_manager import credentials
    return [{'id':n,'enabled':(store.get('settings','provider:'+n) or {}).get('enabled',n not in ('mock','pixabay','unsplash')),'analysis_enabled':(store.get('settings','provider:'+n) or {}).get('analysis_enabled',False),'configured':bool(credentials.get('image:'+n)) if n in ('pixabay','unsplash') else True,'status':'reference-only' if n in ('pixabay','unsplash','openverse') else 'demo' if n=='mock' else 'available','diagnostics':store.get('settings','diagnostics:'+n),'policy':p.get_usage_policy()} for n,p in PROVIDERS.items()]
@router.post('/providers/{name}/health')
async def check(name:str):
    if name not in PROVIDERS:raise HTTPException(404)
    return await PROVIDERS[name].health_check()
@router.post('/search')
async def search(req:SearchRequest):
    if not req.providers:raise HTTPException(422,'至少选择一个来源')
    return {'job_id':queue.start(lambda progress:retrieve(req,progress))}
@router.get('/jobs/{id}')
def get_job(id:str):
    j=store.get('background_jobs',id)
    if not j:raise HTTPException(404)
    return j
@router.post('/jobs/{id}/cancel')
def cancel(id:str):
    j=queue.cancel(id)
    if not j:raise HTTPException(404)
    return j

from pydantic import BaseModel,SecretStr,Field
from app.schemas.models import SearchIntent,ImageAsset
class ProviderSettings(BaseModel):
    enabled:bool
    api_key:SecretStr|None=None
    analysis_enabled:bool|None=None
    analysis_rights_confirmed:bool=False
@router.put('/providers/{name}/settings')
def configure_provider(name:str,r:ProviderSettings):
    if name not in PROVIDERS:raise HTTPException(404)
    if r.api_key is not None:
        from app.ai.llm.credential_manager import credentials
        try:credentials.save('image:'+name,r.api_key.get_secret_value())
        except ValueError as e:raise HTTPException(400,str(e))
    cfg=store.get('settings','provider:'+name) or {}
    if r.analysis_enabled is not None:
        if name!='unsplash':raise HTTPException(422,'该来源不支持此授权设置')
        if r.analysis_enabled and not r.analysis_rights_confirmed and not (cfg.get('analysis_authorization') or {}).get('rights_confirmed'):
            raise HTTPException(422,'请确认授权涵盖本地图片编码与排序')
        cfg['analysis_enabled']=r.analysis_enabled
        if r.analysis_enabled and r.analysis_rights_confirmed:
            import time
            cfg['analysis_authorization']={'rights_confirmed':True,'scope':'local_inference_only','verification_method':'user declaration, not independent verification','confirmed_at':time.time()}
    cfg['enabled']=r.enabled
    store.put('settings','provider:'+name,cfg)
    return {'saved':True}


class RankRequest(BaseModel):
    asset_ids:list[str]=Field(min_length=1,max_length=200)
    intent:SearchIntent
    preference:str='semantic'
    commercial:bool=True

@router.post('/search/rank')
async def rank_candidates(req:RankRequest):
    from app.pipeline.license_filter import policy
    from app.pipeline.visual import rank_assets
    if req.preference not in ('semantic','color','diversity'):raise HTTPException(422,'不支持的排序偏好')
    assets=[]
    for aid in dict.fromkeys(req.asset_ids):
        raw=store.get('image_assets',aid)
        if not raw:raise HTTPException(422,'素材不存在')
        assets.append(policy.apply(ImageAsset(**raw),req.commercial))
    if not any(a.allowed_temporary_analysis for a in assets):
        raise HTTPException(422,'当前素材尚未获准本地分析，请使用自有素材或配置对应分析授权')
    async def work(progress):
        ranked,vectors,stats=await rank_assets([a.model_dump() for a in assets],req.intent,progress,req.preference,True,req.commercial)
        ranked=sorted(ranked,key=lambda a:a.final_score,reverse=True)
        processed={a.id for a in ranked}
        # Keep references and failed-image cards visible, following scored candidates.
        remaining=[a for a in assets if a.id not in processed and a.id not in stats.get('excluded_asset_ids',[])]
        return {'assets':[a.model_dump() for a in ranked+remaining],'stats':stats,'unranked_count':len(remaining)}
    return {'job_id':queue.start(work)}
