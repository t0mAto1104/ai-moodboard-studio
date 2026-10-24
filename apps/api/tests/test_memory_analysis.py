import numpy as np
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import store
from app.pipeline.license_filter import policy
from app.providers.unsplash import UnsplashProvider
from app.providers.mock import fixture_bytes
from app.ai.llm.rule_based_parser import RuleBasedIntentParser
from app.pipeline.visual import rank_assets
from app.routers import assets as asset_router
from app.ai.embeddings.siglip2 import provider


def asset():
    return UnsplashProvider().normalize({'id':'memory-test','urls':{'small':'https://images.unsplash.com/photo-a?ixid=original','regular':'https://images.unsplash.com/photo-a?ixid=original&w=1080'},'links':{'html':'https://unsplash.com/photos/memory-test'},'user':{'name':'Test'}})


@pytest.fixture
def grant(monkeypatch):
    original=store.get
    settings={'enabled':True,'analysis_enabled':True,'analysis_authorization':{'rights_confirmed':True,'scope':'local_inference_only'}}
    monkeypatch.setattr(store,'get',lambda table,key:settings if table=='settings' and key=='provider:unsplash' else original(table,key))
    return settings


def test_analysis_grant_is_narrow(grant):
    a=policy.apply(asset())
    assert a.allowed_temporary_analysis and a.copyright_review_status=='user_authorized_analysis'
    assert not a.allowed_store and not a.allowed_transform and not a.allowed_export
    grant['analysis_enabled']=False
    assert not policy.apply(a).allowed_temporary_analysis


@pytest.mark.asyncio
async def test_image_data_stays_in_memory(grant,monkeypatch,tmp_path):
    (tmp_path/'cache').mkdir();monkeypatch.setattr(asset_router,'DATA',tmp_path)
    urls=[]
    async def fetch(url):urls.append(url);return fixture_bytes(1)
    monkeypatch.setattr(asset_router,'fetch_image',fetch)
    data=await asset_router.image_bytes(asset(),cache=False)
    assert data and list((tmp_path/'cache').iterdir())==[]
    from urllib.parse import urlparse,parse_qs
    params=parse_qs(urlparse(urls[0]).query)
    assert params['ixid']==['original'] and params['w']==['512'] and params['h']==['512']


@pytest.mark.asyncio
async def test_temporary_analysis_does_not_persist_vectors(grant,monkeypatch,tmp_path):
    (tmp_path/'cache').mkdir();monkeypatch.setattr(asset_router,'DATA',tmp_path)
    async def fetch(url):return fixture_bytes(2)
    monkeypatch.setattr(asset_router,'fetch_image',fetch)
    vector=np.zeros((1,768),dtype=np.float32);vector[0,0]=1
    monkeypatch.setattr(provider,'encode_texts',lambda texts:vector)
    monkeypatch.setattr(provider,'encode_images',lambda images:vector)
    before=len(store.all_rows('embeddings'))
    rows,vectors,stats=await rank_assets([asset().model_dump()],RuleBasedIntentParser().parse('cat'),lambda **kw:None)
    assert stats['ranking_mode']=='siglip2' and stats['image_storage']=='memory_only'
    assert stats['analyzed_count']==1 and vectors['unsplash:memory-test'].shape==(768,)
    assert rows[0].embedding_vector_reference is None
    assert len(store.all_rows('embeddings'))==before and not list((tmp_path/'cache').iterdir())


def test_enabling_requires_authorization_declaration():
    old=store.get('settings','provider:unsplash')
    store.remove('settings','provider:unsplash')
    try:
        client=TestClient(app,headers={'X-Moodboard-Request':'1'})
        assert client.put('/api/providers/unsplash/settings',json={'enabled':True,'analysis_enabled':True}).status_code==422
        assert client.put('/api/providers/unsplash/settings',json={'enabled':True,'analysis_enabled':True,'analysis_rights_confirmed':True}).status_code==200
        assert policy.apply(asset()).allowed_temporary_analysis
        assert client.put('/api/providers/unsplash/settings',json={'enabled':True,'analysis_enabled':False}).status_code==200
        assert not policy.apply(asset()).allowed_temporary_analysis
    finally:
        if old:store.put('settings','provider:unsplash',old)
        else:store.remove('settings','provider:unsplash')
