import asyncio
import hashlib
import re
import time
import numpy as np
import imagehash
from app.ai.embeddings.siglip2 import provider
from app.pipeline.color_analysis import analyze
from app.pipeline.ranking import score
from app.pipeline.deduplication import duplicate
from app.pipeline.license_filter import policy
from app.routers.assets import image_bytes
from app.security.images import decode
from app.db import store
from app.schemas.models import ImageAsset


async def rank_assets(raw_assets,intent,progress,preference='semantic',use_vision=True,commercial=True):
    start=time.perf_counter()
    assets=[];vectors={};warnings=[];excluded=[];text_vector=None
    permitted=[policy.apply(ImageAsset(**raw),commercial) for raw in raw_assets]
    if use_vision and any(a.allowed_temporary_analysis for a in permitted):
        try:
            text=' '.join([intent.subject,*intent.style_keywords,*intent.materials,*intent.mood_keywords,*intent.color_keywords])
            text_vector=(await asyncio.to_thread(provider.encode_texts,[text]))[0]
        except Exception as e:
            warnings.append('视觉模型不可用，采用元数据排序：'+type(e).__name__)
    analyzed=0;cache_hits=0;downloaded_bytes=0
    for i,a in enumerate(permitted):
        im=None;data=None
        try:
            if not a.allowed_temporary_analysis:continue
            # Analysis never creates an image-file cache, including for sources that permit storage.
            data=await image_bytes(a,cache=False,commercial=commercial)
            downloaded_bytes+=len(data)
            im=decode(data)
            if min(im.size)<96:
                excluded.append(a.id);continue
            a.width,a.height=im.size
            a.content_hash=hashlib.sha256(data).hexdigest()
            a.perceptual_hash=str(imagehash.phash(im))
            features=analyze(im,intent.target_palette)
            for k in ('palette_score','quality_score','composition_score'):setattr(a,k,features[k])
            words=set(re.findall(r'\w+',(' '.join(intent.search_queries)).lower()))
            metadata=(a.title+' '+a.description+' '+a.query_origin).lower()
            a.semantic_score=min(1,sum(w in metadata for w in words)/max(1,len(words)))
            if text_vector is not None:
                key=hashlib.sha256(f'{a.content_hash}:{provider.model_id}:{provider.revision}:{provider.preprocess}'.encode()).hexdigest()
                # A temporary-analysis grant does not implicitly grant persistent vector storage.
                cached=store.get('embeddings',key) if a.allowed_store else None
                if cached and len(cached['vector'])==provider.dimension and cached['model']==provider.model_id and cached['revision']==provider.revision:
                    v=np.array(cached['vector'],dtype=np.float32);cache_hits+=1
                else:
                    v=(await asyncio.to_thread(provider.encode_images,[im]))[0]
                    if a.allowed_store:
                        store.put('embeddings',key,{'model':provider.model_id,'revision':provider.revision,'preprocess':provider.preprocess,'dimension':provider.dimension,'vector':v.tolist()})
                vectors[a.id]=v
                a.semantic_score=float(np.clip((float(v@text_vector)+.05)/.4,0,1))
                a.embedding_model_id=provider.model_id;a.embedding_model_revision=provider.revision
                a.embedding_vector_reference=key if a.allowed_store else None
            a.final_score=score(a,preference)
            analyzed+=1
            if any(duplicate(a,b,vectors) for b in assets):excluded.append(a.id)
            else:assets.append(a)
            store.put('image_assets',a.id,a.model_dump())
        except asyncio.CancelledError:raise
        except Exception as e:
            warnings.append(a.id+': '+(str(e) if isinstance(e,ValueError) else type(e).__name__))
        finally:
            if im is not None:im.close()
            data=None
            progress(progress=10+int(70*(i+1)/max(1,len(permitted))))
    return assets,vectors,{
        'seconds':time.perf_counter()-start,'warnings':warnings,
        'ranking_mode':'siglip2' if vectors else 'metadata',
        'device':provider.device,'model_id':provider.model_id,'model_revision':provider.revision,
        'input_count':len(raw_assets),'analyzed_count':analyzed,'unique_count':len(assets),
        'excluded_asset_ids':excluded,'embedding_cache_hits':cache_hits,
        'image_storage':'memory_only','analysis_image_files_written':0,
        'image_bytes_read':downloaded_bytes,
    }
