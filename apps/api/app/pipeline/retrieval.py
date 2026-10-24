import asyncio,uuid,time
from app.providers.registry import PROVIDERS
from app.providers.base import ProviderError
from app.pipeline.license_filter import policy
from app.db import store
async def retrieve(req,progress):
    errors=[];assets={};session=str(uuid.uuid4());done=0
    async def one(name,q):
        nonlocal done
        try:
            p=PROVIDERS.get(name)
            if not p:raise ProviderError('尚未配置或暂不支持')
            cfg=store.get('settings','provider:'+name) or {}
            if cfg.get('enabled') is False:raise ProviderError('来源已在设置中禁用')
            for a in await p.search(q,{},req.page,req.per_page):
                a.query_origin=q;a=policy.apply(a,req.commercial);assets[a.id]=a.model_dump()
        except Exception as e:errors.append({'provider':name,'error':str(e) if isinstance(e,ProviderError) else '搜索响应异常'})
        done+=1;progress(progress=int(done/(len(req.providers)*len(req.queries))*100))
    await asyncio.gather(*(one(n,q) for n in req.providers for q in dict.fromkeys(req.queries)))
    for id,a in assets.items():store.put('image_assets',id,a)
    store.put('search_sessions',session,{'id':session,'request':req.model_dump(),'asset_ids':list(assets),'errors':errors,'created_at':time.time()})
    for i,q in enumerate(req.queries):store.put('search_queries',session+':'+str(i),{'session_id':session,'query':q})
    return {'session_id':session,'assets':list(assets.values()),'errors':errors}
