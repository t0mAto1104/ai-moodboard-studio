import time
import uuid
from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field,field_validator
from sqlalchemy import select,delete,update
from app.db import store
from app.schemas.models import ImageAsset
from app.pipeline.license_filter import policy
router=APIRouter(prefix='/api/library')

class TagInput(BaseModel):
    name:str=Field(min_length=1,max_length=40)
    @field_validator('name')
    @classmethod
    def clean(cls,value):
        value=' '.join(value.split())
        if not value:raise ValueError('请输入标签名称')
        return value

class FavoriteInput(BaseModel):
    tag_ids:list[str]=Field(default_factory=list,max_length=20)


def checked_tags(ids):
    ids=list(dict.fromkeys(ids))
    if any(not store.get('library_tags',id) for id in ids):raise HTTPException(422,'标签不存在')
    return ids


def tag_name_available(name,except_id=None):
    if any(t['id']!=except_id and t['name'].casefold()==name.casefold() for t in store.all_rows('library_tags')):
        raise HTTPException(409,'标签已存在')


@router.get('')
def library():
    rows=[]
    for item in store.all_rows('favorites'):
        raw=store.get('image_assets',item['asset_id'])
        if not raw:continue
        asset=policy.apply(ImageAsset(**raw))
        # Pixabay allows temporary result previews, not permanent remote-image embedding.
        if asset.provider=='pixabay':asset.display_url=''
        rows.append({**item,'asset':asset.model_dump()})
    return {'tags':sorted(store.all_rows('library_tags'),key=lambda t:t['created_at']),'favorites':rows}


@router.post('/tags',status_code=201)
def create_tag(req:TagInput):
    if len(store.all_rows('library_tags'))>=100:raise HTTPException(422,'最多 100 个标签')
    tag_name_available(req.name)
    tag={'id':str(uuid.uuid4()),'name':req.name,'created_at':time.time()}
    store.put('library_tags',tag['id'],tag)
    return tag


@router.patch('/tags/{id}')
def rename_tag(id:str,req:TagInput):
    tag=store.get('library_tags',id)
    if not tag:raise HTTPException(404,'标签不存在')
    tag_name_available(req.name,id);tag['name']=req.name;store.put('library_tags',id,tag)
    return tag


@router.delete('/tags/{id}')
def delete_tag(id:str):
    if not store.get('library_tags',id):raise HTTPException(404,'标签不存在')
    with store.engine.begin() as connection:
        tags=store.TABLES['library_tags'];favorites=store.TABLES['favorites']
        connection.execute(delete(tags).where(tags.c.id==id))
        for key,payload in connection.execute(select(favorites.c.id,favorites.c.payload)).all():
            if id in payload['tag_ids']:
                payload={**payload,'tag_ids':[t for t in payload['tag_ids'] if t!=id]}
                connection.execute(update(favorites).where(favorites.c.id==key).values(payload=payload,updated_at=time.time()))
    return {'deleted':True}


@router.put('/favorites/{asset_id}')
async def favorite(asset_id:str,req:FavoriteInput):
    raw=store.get('image_assets',asset_id)
    if not raw:raise HTTPException(404,'素材不存在')
    a=policy.apply(ImageAsset(**raw))
    if not a.allowed_display:raise HTTPException(403,'该素材不允许展示收藏')
    existing=store.get('favorites',asset_id)
    tags=checked_tags(req.tag_ids)
    if not existing and a.provider=='unsplash':
        from app.providers.registry import PROVIDERS
        from app.providers.base import ProviderError
        try:await PROVIDERS['unsplash'].track_selection(a)
        except ProviderError as e:raise HTTPException(502,'收藏事件上报失败：'+str(e))
    item={'asset_id':asset_id,'tag_ids':tags,'saved_at':existing['saved_at'] if existing else time.time()}
    store.put('favorites',asset_id,item)
    return item


@router.delete('/favorites/{asset_id}')
def unfavorite(asset_id:str):
    store.remove('favorites',asset_id)
    return {'removed':True}
