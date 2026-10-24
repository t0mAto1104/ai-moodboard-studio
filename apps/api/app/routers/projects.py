import uuid,time,copy
from typing import Literal
from pydantic import BaseModel,Field
from fastapi import APIRouter,HTTPException
from app.db import store
from app.schemas.models import SearchIntent,LayoutItem,ImageAsset
from app.jobs.queue import queue
from app.pipeline.visual import rank_assets
from app.pipeline.selection import select_mmr
from app.layout.engine import layout,validate_items
router=APIRouter(prefix='/api/projects')
class ProjectCreate(BaseModel):
    name:str=Field(default='Untitled board',min_length=1,max_length=100)
    prompt:str=''
    intent:SearchIntent
    asset_ids:list[str]=Field(default=[],max_length=200)
    ratio:Literal['16:9','4:3','1:1','A4']='16:9'
    layout_style:Literal['editorial','material','collage']='editorial'
    commercial:bool=True
class ProjectPatch(BaseModel):
    name:str|None=Field(default=None,min_length=1,max_length=100)
    items:list[LayoutItem]|None=None
    asset_ids:list[str]|None=Field(default=None,max_length=200)
    ratio:Literal['16:9','4:3','1:1','A4']|None=None
    layout_style:Literal['editorial','material','collage']|None=None
class Generate(BaseModel):
    preference:Literal['semantic','color','diversity']='semantic'
    use_vision:bool=True
    relayout_only:bool=False

def project(id):
    p=store.get('projects',id)
    if not p:raise HTTPException(404,'项目不存在')
    return p

def save(p):
    p['updated_at']=time.time();store.put('projects',p['id'],p)
    for aid in p['asset_ids']:store.put('project_assets',p['id']+':'+aid,{'project_id':p['id'],'asset_id':aid})
    for item in p['items']:store.put('layout_items',p['id']+':'+item['id'],{'project_id':p['id'],**item})
    return p
@router.post('')
def create(r:ProjectCreate):
    if any(not store.get('image_assets',id) for id in r.asset_ids):raise HTTPException(422,'素材不存在')
    return save({'id':str(uuid.uuid4()),**r.model_dump(),'items':[],'created_at':time.time(),'stats':{}})
@router.get('')
def listing():return [{**p,'assets':[a for aid in p['asset_ids'] if (a:=store.get('image_assets',aid))]} for p in store.all_rows('projects')]
@router.get('/{id}')
def get(id:str):
    p=project(id);return {**p,'assets':[a for aid in p['asset_ids'] if (a:=store.get('image_assets',aid))]}
@router.patch('/{id}')
async def patch(id:str,r:ProjectPatch):
    p=project(id);old_items=copy.deepcopy(p['items']);changes=r.model_dump(exclude_none=True);items=changes.pop('items',p['items']);p.update(changes)
    if any(not store.get('image_assets',a) for a in p['asset_ids']):raise HTTPException(422,'素材不存在')
    try:p['items']=validate_items(items,p['ratio'],p['asset_ids'])
    except ValueError as e:raise HTTPException(422,str(e))
    try:await track_references(p['items'],old_items)
    except ValueError as e:raise HTTPException(502,str(e))
    return save(p)
@router.delete('/{id}')
def delete(id:str):project(id);store.remove('projects',id);return {'deleted':True}
@router.post('/{id}/duplicate')
async def duplicate(id:str):
    p=copy.deepcopy(project(id));p['id']=str(uuid.uuid4());p['name']=(p['name'][:95]+' copy')
    try:await track_references(p['items'],[])
    except ValueError as e:raise HTTPException(502,str(e))
    return save(p)
@router.post('/{id}/generate')
async def generate(id:str,r:Generate):
    p=copy.deepcopy(project(id))
    async def work(progress):
        assets=[ImageAsset(**a) for aid in p['asset_ids'] if (a:=store.get('image_assets',aid))]
        if r.relayout_only:
            from app.pipeline.license_filter import policy
            ids = list(dict.fromkeys(item['asset_id'] for item in p['items'] if item['kind']=='image'))
            by_id = {a.id: policy.apply(a, p['commercial']) for a in assets}
            selected = [by_id[aid] for aid in ids if aid in by_id and (by_id[aid].allowed_transform or by_id[aid].allowed_reference_board)]
            stats={'ranking_mode':'existing'}
        else:
            from app.pipeline.license_filter import policy
            permitted=[policy.apply(a,p['commercial']) for a in assets]
            references=[a for a in permitted if a.allowed_reference_board and not a.allowed_temporary_analysis]
            analyzable=[a for a in permitted if a.allowed_temporary_analysis]
            assets,v,stats=await rank_assets([a.model_dump() for a in analyzable],SearchIntent(**p['intent']),progress,r.preference,r.use_vision and bool(analyzable),p['commercial'])
            selected=select_mmr(assets,v,p['intent']['target_image_count'],r.preference)
            selected += references[:max(0,p['intent']['target_image_count']-len(selected))]
            if references:stats['reference_count']=sum(a.allowed_reference_board for a in selected)
            if not analyzable and references:stats['ranking_mode']='provider_order_reference' 
        if not selected:raise ValueError('没有可分析与编辑的素材。请更换来源或使用演示素材。')
        old_items=p['items']
        p['items']=layout(selected,p['layout_style'],p['ratio'],p['intent']['target_palette']);p['stats']=stats
        await track_references(p['items'],old_items)
        save(p);return {'project_id':p['id'],'stats':stats}
    return {'job_id':queue.start(work)}


async def track_references(items,old_items):
    from app.providers.registry import PROVIDERS
    from app.providers.base import ProviderError
    old={item.get('asset_id') for item in old_items}
    for aid in dict.fromkeys(item.get('asset_id') for item in items if item.get('asset_id')):
        if aid in old:continue
        raw=store.get('image_assets',aid)
        if raw and raw['provider']=='unsplash':
            try:await PROVIDERS['unsplash'].track_selection(ImageAsset(**raw))
            except ProviderError as e:raise ValueError('Unsplash 选择事件上报失败：'+str(e))
