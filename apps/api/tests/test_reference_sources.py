import time
import httpx
import pytest
from fastapi.testclient import TestClient
from app.db import store
from app.main import app
from app.providers.unsplash import UnsplashProvider
from app.pipeline.license_filter import policy
from app.providers.registry import PROVIDERS
from app.ai.llm.rule_based_parser import RuleBasedIntentParser

def photo(id='ref_test'):
    return {'id':id,'urls':{'small':'https://images.unsplash.com/photo-'+id+'?ixid=preserved'},'user':{'name':'Test Artist','links':{'html':'https://unsplash.com/@artist'}},'links':{'html':'https://unsplash.com/photos/'+id,'download_location':'https://api.unsplash.com/photos/'+id+'/download?ixid=preserved'},'width':1200,'height':800}

def test_stock_license_allows_export_without_granting_ml_or_storage():
    asset=policy.apply(UnsplashProvider().normalize(photo()))
    assert asset.display_url.endswith('ixid=preserved')
    assert asset.allowed_reference_board and not asset.allowed_store and not asset.allowed_temporary_analysis and asset.allowed_export
    assert 'utm_source=' in asset.creator_url
    asset.thumbnail_url='https://127.0.0.1/private'
    asset=policy.apply(asset)
    assert not asset.display_url and not asset.allowed_reference_board

@pytest.mark.asyncio
async def test_selection_events_not_cached(monkeypatch):
    requests=[]
    def handle(request):
        requests.append(request)
        return httpx.Response(200,json={'url':'https://images.unsplash.com/photo-ref'})
    provider=UnsplashProvider(httpx.MockTransport(handle));provider.interval=0
    monkeypatch.setattr(provider,'headers',lambda:{'Authorization':'Client-ID fake-test'})
    asset=provider.normalize(photo('track_test'))
    await provider.track_selection(asset)
    await provider.track_selection(asset)
    assert len(requests)==2 and all(r.url.params['ixid']=='preserved' for r in requests)
    asset.license_evidence['download_location']='https://evil.example/photos/track_test/download'
    with pytest.raises(Exception,match='地址无效'):await provider.track_selection(asset)

def test_reference_board_save_reopen_and_export(monkeypatch):
    from app.routers import projects
    calls=[]
    async def track(asset):calls.append(asset.id)
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',track)
    rows=[policy.apply(UnsplashProvider().normalize(photo('board_ref_'+str(i)))) for i in range(2)]
    for a in rows:store.put('image_assets',a.id,a.model_dump())
    def forbidden(*a):pytest.fail('Reference images must never go through pixel analysis')
    # The pipeline receives no analyzable references and must not request a visual model.
    from app.ai.embeddings.siglip2 import provider
    monkeypatch.setattr(provider,'encode_texts',forbidden)
    with TestClient(app,headers={'X-Moodboard-Request':'1'}) as client:
        def job(path,body):
            response=client.post(path,json=body);assert response.status_code==200,response.text
            id=response.json()['job_id']
            for _ in range(100):
                j=client.get('/api/jobs/'+id).json()
                if j['status'] in ('completed','failed'):return j
                time.sleep(.01)
            pytest.fail('job timed out')
        intent=RuleBasedIntentParser().parse('kitty').model_dump();intent['target_image_count']=2
        p=client.post('/api/projects',json={'name':'Reference board test','intent':intent,'asset_ids':[a.id for a in rows]}).json()
        id=p['id'];base='/api/projects/'+id
        j=job(base+'/generate',{'use_vision':True})
        assert j['status']=='completed',j
        assert j['result']['stats']['ranking_mode']=='provider_order_reference'
        assert calls==[a.id for a in rows]
        reopened=client.get(base).json()
        assert len(reopened['items'])==2 and reopened['assets'][0]['display_url']
        assert client.patch(base,json={'items':reopened['items']}).status_code==200
        assert job(base+'/generate',{'relayout_only':True})['status']=='completed'
        assert len(calls)==2
        from app.providers.mock import fixture_bytes
        from app.routers import assets as asset_router
        async def fetch(url):return fixture_bytes(1)
        monkeypatch.setattr(asset_router,'fetch_image',fetch)
        exported=job(base+'/export',{'format':'png'})
        assert exported['status']=='completed',exported
        assert len(calls)==4
