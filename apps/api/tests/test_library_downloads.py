import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import store
from app.providers.mock import MockProvider,fixture_bytes
from app.providers.unsplash import UnsplashProvider
from app.providers.pixabay import PixabayProvider
from app.providers.openverse import OpenverseProvider
from app.providers.registry import PROVIDERS
from app.pipeline.license_filter import policy
from app.routers import assets as asset_router
from app.core.config import DATA


def client():return TestClient(app,headers={'X-Moodboard-Request':'1'})
def stored(a):
    store.put('image_assets',a.id,a.model_dump());return a


def test_library_tags_persistence_and_delete_preserves_favorites():
    c=client();a=stored(policy.apply(MockProvider().normalize({'id':8})))
    tag=c.post('/api/library/tags',json={'name':'  冷色 材质  '});assert tag.status_code==201
    id=tag.json()['id']
    assert c.post('/api/library/tags',json={'name':'冷色 材质'}).status_code==409
    assert c.put('/api/library/favorites/'+a.id,json={'tag_ids':[id]}).status_code==200
    before=store.get('favorites',a.id)['saved_at']
    assert c.put('/api/library/favorites/'+a.id,json={'tag_ids':[id,id]}).status_code==200
    assert store.get('favorites',a.id)['saved_at']==before
    assert c.patch('/api/library/tags/'+id,json={'name':'金属'}).status_code==200
    reopened=client().get('/api/library').json()
    f=next(f for f in reopened['favorites'] if f['asset_id']==a.id)
    assert f['tag_ids']==[id] and f['asset']['creator_name']
    assert c.delete('/api/library/tags/'+id).status_code==200
    assert store.get('favorites',a.id)['tag_ids']==[]
    assert c.delete('/api/library/favorites/'+a.id).status_code==200
    assert store.get('image_assets',a.id) is not None


def test_unknown_tags_and_empty_names_rejected():
    c=client();a=stored(policy.apply(MockProvider().normalize({'id':9})))
    assert c.post('/api/library/tags',json={'name':'   '}).status_code==422
    assert c.put('/api/library/favorites/'+a.id,json={'tag_ids':['missing']}).status_code==422
    assert c.put('/api/library/favorites/not-real',json={}).status_code==404


def unsplash():
    return UnsplashProvider().normalize({'id':'manual-download-test','urls':{'full':'https://images.unsplash.com/photo-manual?ixid=retained','small':'https://images.unsplash.com/photo-manual?w=400&ixid=retained'},'links':{'html':'https://unsplash.com/photos/manual-download-test','download_location':'https://api.unsplash.com/photos/manual-download-test/download?ixid=retained'},'user':{'name':'Test Photographer','links':{'html':'https://unsplash.com/@test'}}})


def test_unsplash_download_independent_of_export_and_not_cached(monkeypatch):
    a=stored(unsplash());checked=policy.apply(a)
    assert checked.allowed_download and not checked.allowed_export and not checked.allowed_store
    events=[];urls=[]
    async def track(a):events.append(a.id)
    async def fetch(url):urls.append(url);return fixture_bytes(3)
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',track)
    monkeypatch.setattr(asset_router,'fetch_download',fetch)
    cache_before={p.name for p in (DATA/'cache').glob('*')}
    c=client()
    for _ in range(2):
        r=c.post('/api/assets/'+a.id+'/download')
        assert r.status_code==200 and r.content.startswith(b'\x89PNG')
        assert 'attachment' in r.headers['content-disposition']
        record=store.get('download_records',r.headers['x-download-record'])
        assert record['creator_name']=='Test Photographer' and record['license_url']
    assert len(events)==2 and len(urls)==2 and 'ixid=retained' in urls[0]
    assert cache_before=={p.name for p in (DATA/'cache').glob('*')}


def test_unknown_license_blocks_download_before_fetch(monkeypatch):
    a=stored(OpenverseProvider().normalize({'id':'unverified-download','license':'cc0','thumbnail':'https://api.openverse.org/v1/images/test/thumb/','url':'https://example.org/photo.jpg'}))
    async def forbidden(*args):pytest.fail('Unknown source rights must block download')
    monkeypatch.setattr(asset_router,'fetch_download',forbidden)
    assert client().post('/api/assets/'+a.id+'/download').status_code==403


def test_favorite_event_only_on_initial_selection(monkeypatch):
    a=stored(unsplash());store.remove('favorites',a.id);events=[]
    async def track(a):events.append(a.id)
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',track)
    c=client()
    assert c.put('/api/library/favorites/'+a.id,json={}).status_code==200
    assert c.put('/api/library/favorites/'+a.id,json={}).status_code==200
    assert len(events)==1


def test_pixabay_saved_reference_does_not_permanently_hotlink():
    a=stored(PixabayProvider().normalize({'id':4444,'tags':'texture','previewURL':'https://cdn.pixabay.com/photo/preview.jpg','largeImageURL':'https://pixabay.com/get/photo.jpg','pageURL':'https://pixabay.com/photos/4444/'}))
    c=client();assert c.put('/api/library/favorites/'+a.id,json={}).status_code==200
    favorite=next(f for f in c.get('/api/library').json()['favorites'] if f['asset_id']==a.id)
    assert favorite['asset']['allowed_download'] and not favorite['asset']['display_url']


def test_local_demo_download():
    a=stored(policy.apply(MockProvider().normalize({'id':10})))
    response=client().post('/api/assets/'+a.id+'/download')
    assert response.status_code==200 and response.headers['content-type'].startswith('image/png')
