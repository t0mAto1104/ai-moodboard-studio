import hashlib
from fastapi import APIRouter,HTTPException,Response
from app.db import store
from app.schemas.models import ImageAsset
from app.pipeline.license_filter import policy
from app.security.images import fetch_image
from app.providers.mock import fixture_bytes
from app.core.config import DATA
router=APIRouter(prefix='/api/assets')
async def image_bytes(a,cache=True,commercial=True):
    a=policy.apply(a,commercial)
    if not a.allowed_temporary_analysis:raise ValueError('许可不允许下载或分析')
    if a.provider=='mock':return fixture_bytes(a.provider_asset_id)
    if a.provider=='upload':
        from uuid import UUID
        source=DATA/'uploads'/(str(UUID(a.provider_asset_id))+'.img')
        return source.read_bytes()
    path=DATA/'cache'/(hashlib.sha256(a.id.encode()).hexdigest()+'.img')
    if cache and a.allowed_store and path.exists():return path.read_bytes()
    url=a.image_url
    if a.provider=='unsplash':
        # Keep the API-provided URL/ixid; request only an analysis-sized rendition.
        from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
        parts=urlsplit(url);params=dict(parse_qsl(parts.query))
        params.update(w='512',h='512',fit='max',fm='jpg')
        url=urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(params),parts.fragment))
    data=await fetch_image(url)
    if cache and a.allowed_store:path.write_bytes(data)
    return data
@router.get('/{id}/image')
async def image(id:str):
    raw=store.get('image_assets',id)
    if not raw:raise HTTPException(404)
    if raw['provider']=='unsplash':raise HTTPException(403,'Unsplash 展示使用官方图片链接')
    try:data=await image_bytes(ImageAsset(**raw))
    except ValueError as e:raise HTTPException(403,str(e))
    return Response(data,media_type='image/png' if data.startswith(b'\x89PNG') else 'image/jpeg',headers={'Cache-Control':'no-store'})

from fastapi import UploadFile,File,Form
from app.security.images import decode,MAX_BYTES
import uuid
@router.post('/upload')
async def upload(file:UploadFile=File(...),rights_confirmed:bool=Form(False)):
    if not rights_confirmed:raise HTTPException(400,'请确认拥有复制、修改与导出权利')
    data=await file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise HTTPException(413,'文件超过 12MB')
    try:im=decode(data)
    except Exception:raise HTTPException(422,'无效或不安全的图片')
    id='upload:'+str(uuid.uuid4());a=ImageAsset(id=id,provider='upload',provider_asset_id=id.split(':')[1],title=(file.filename or 'Uploaded image')[:120],creator_name='User supplied',width=im.width,height=im.height,license_type='user-owned',license_evidence={'source_verified':True,'rights_confirmed':True,'verification_method':'user declaration, not independent verification'},attribution_text='User supplied: '+(file.filename or 'image'))
    a=policy.apply(a);path=DATA/'cache'/(hashlib.sha256(a.id.encode()).hexdigest()+'.img');path.write_bytes(data)
    # Uploaded source is persistent, not a disposable remote cache.
    sources=DATA/'uploads';sources.mkdir(exist_ok=True);source=sources/(a.provider_asset_id+'.img');source.write_bytes(data);a.local_file_path=str(source)
    store.put('image_assets',id,a.model_dump());return a.model_dump()


import asyncio,time,re
from app.security.images import fetch_download
from app.providers.base import ProviderError
from app.providers.registry import PROVIDERS
DOWNLOADS=asyncio.Semaphore(2)

@router.post('/{id}/download')
async def download_asset(id:str):
    raw=store.get('image_assets',id)
    if not raw:raise HTTPException(404,'素材不存在')
    a=policy.apply(ImageAsset(**raw))
    if not a.allowed_download:raise HTTPException(403,a.download_reason)
    async with DOWNLOADS:
        try:
            if a.provider=='unsplash':await PROVIDERS['unsplash'].track_selection(a)
            if a.provider=='mock':data=fixture_bytes(a.provider_asset_id)
            elif a.provider=='upload':data=await image_bytes(a,cache=False)
            else:data=await fetch_download(a.download_url or a.image_url)
        except (ValueError,ProviderError) as e:raise HTTPException(502,str(e))
        except Exception:raise HTTPException(502,'图片下载暂不可用，请稍后重试或查看来源')
    ext='png' if data.startswith(b'\x89PNG') else 'webp' if data.startswith(b'RIFF') else 'jpg'
    filename=re.sub(r'[^A-Za-z0-9_-]','_',a.provider+'-'+a.provider_asset_id)[:100]+'.'+ext
    record={'id':str(uuid.uuid4()),'asset_id':a.id,'provider':a.provider,'creator_name':a.creator_name,'source_page_url':a.source_page_url,'license_type':a.license_type,'license_url':a.license_url,'attribution_text':a.attribution_text,'bytes':len(data),'filename':filename,'created_at':time.time()}
    store.put('download_records',record['id'],record)
    return Response(data,media_type={'png':'image/png','webp':'image/webp','jpg':'image/jpeg'}[ext],headers={'Content-Disposition':f'attachment; filename="{filename}"','Cache-Control':'no-store','X-Download-Record':record['id']})
