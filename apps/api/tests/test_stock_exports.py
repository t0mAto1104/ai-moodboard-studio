import io,json,zipfile
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import store
from app.core.config import DATA
from app.pipeline.license_filter import policy
from app.providers.unsplash import UnsplashProvider
from app.providers.pixabay import PixabayProvider
from app.providers.mock import fixture_bytes
from app.providers.registry import PROVIDERS
from app.exports.render import export_project
from app.layout.engine import layout
from app.routers import assets as asset_router

def stock(provider,index=0):
    if provider=='unsplash':
        id='export-'+str(index)
        return UnsplashProvider().normalize({'id':id,'urls':{'small':'https://images.unsplash.com/photo-test?w=400&ixid=keep','regular':'https://images.unsplash.com/photo-test?w=1080&ixid=keep'},'links':{'html':'https://unsplash.com/photos/'+id,'download_location':'https://api.unsplash.com/photos/'+id+'/download?ixid=keep'},'user':{'name':'Export Artist','links':{'html':'https://unsplash.com/@artist'}}})
    return PixabayProvider().normalize({'id':9100+index,'user':'Export Artist','user_id':55,'pageURL':'https://pixabay.com/photos/test-'+str(9100+index)+'/','previewURL':'https://cdn.pixabay.com/photo/test-small.jpg','webformatURL':'https://pixabay.com/get/test.jpg'})

@pytest.mark.parametrize('provider',['unsplash','pixabay'])
@pytest.mark.asyncio
async def test_stock_png_pdf_no_ml_or_export_image_cache(provider,monkeypatch):
    rows=[stock(provider,i) for i in range(2)]
    for a in rows:store.put('image_assets',a.id,a.model_dump())
    events=[];urls=[]
    async def track(a):events.append(a.id)
    async def fetch(url):urls.append(url);return fixture_bytes(len(urls))
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',track)
    monkeypatch.setattr(asset_router,'fetch_image',fetch)
    p={'id':'stock-export','ratio':'16:9','commercial':True,'asset_ids':[a.id for a in rows],'items':layout(rows)}
    before=set((DATA/'cache').iterdir())
    for fmt in ('png','pdf'):
        result=await export_project(p,fmt)
        with zipfile.ZipFile(DATA/'exports'/(result['id']+'.zip')) as archive:
            assert archive.read('moodboard.'+fmt).startswith(b'\x89PNG' if fmt=='png' else b'%PDF-')
            manifest=json.loads(archive.read('license-manifest.json'))
            assert len(manifest)==2 and all(m['author']=='Export Artist' and m['source'] and m['license_url'] for m in manifest)
            assert 'Export Artist' in archive.read('attribution.txt').decode()
            assert all(m['evidence']['export_basis']=='official-stock-license-v1' for m in manifest)
    assert len(urls)==4 and set((DATA/'cache').iterdir())==before
    assert len(events)==(4 if provider=='unsplash' else 0)
    for a in rows:
        checked=policy.apply(a)
        assert checked.allowed_export and checked.allowed_transform and not checked.allowed_temporary_analysis

def test_existing_unsplash_project_permissions_recomputed():
    a=stock('unsplash');a.license_type='Unsplash API research-only'
    a.allowed_export=False;a.license_evidence={'source_verified':False,'download_location':'https://api.unsplash.com/photos/export-0/download'}
    store.put('image_assets',a.id,a.model_dump())
    store.put('projects','legacy-stock',{'id':'legacy-stock','commercial':True,'asset_ids':[a.id],'items':layout([a]),'ratio':'16:9'})
    with TestClient(app) as c:
        result=c.get('/api/projects/legacy-stock').json()['assets'][0]
        assert result['allowed_export'] and result['license_type']=='Unsplash License'
    a.license_type='Unknown'
    assert not policy.apply(a).allowed_export

@pytest.mark.asyncio
async def test_export_event_failure_blocks_output_and_fetch(monkeypatch):
    a=stock('unsplash');store.put('image_assets',a.id,a.model_dump())
    async def fail(a):raise ValueError('event unavailable')
    async def forbidden(url):pytest.fail('Must not fetch after failed tracking')
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',fail)
    monkeypatch.setattr(asset_router,'fetch_image',forbidden)
    before=set((DATA/'exports').iterdir())
    with pytest.raises(ValueError,match='event unavailable'):
        await export_project({'id':'event-fail','ratio':'16:9','asset_ids':[a.id],'items':layout([a])},'png')
    assert set((DATA/'exports').iterdir())==before

@pytest.mark.asyncio
async def test_unknown_in_mixed_board_blocks_all_network(monkeypatch):
    a=stock('unsplash');b=stock('pixabay');b.license_type='Unknown'
    for row in (a,b):store.put('image_assets',row.id,row.model_dump())
    async def forbidden(*args):pytest.fail('Check all rights before network')
    monkeypatch.setattr(PROVIDERS['unsplash'],'track_selection',forbidden)
    monkeypatch.setattr(asset_router,'fetch_image',forbidden)
    with pytest.raises(ValueError,match='许可'):
        await export_project({'id':'mixed-fail','ratio':'16:9','asset_ids':[a.id,b.id],'items':layout([a,b])},'png')

@pytest.mark.asyncio
async def test_pixabay_single_image_only_is_not_a_creative_board():
    a=stock('pixabay');store.put('image_assets',a.id,a.model_dump())
    with pytest.raises(ValueError,match='组合创作'):
        await export_project({'id':'standalone','ratio':'16:9','asset_ids':[a.id],'items':layout([a])},'png')

def test_pixabay_board_preview_is_local_and_does_not_grant_analysis(monkeypatch):
    a=stock('pixabay');store.put('image_assets',a.id,a.model_dump())
    async def fetch(url):return fixture_bytes(1)
    monkeypatch.setattr(asset_router,'fetch_image',fetch)
    store.put('projects','pixabay-preview',{'id':'pixabay-preview','asset_ids':[a.id],'items':layout([a]),'ratio':'16:9'})
    with TestClient(app) as c:
        assert c.get('/api/assets/'+a.id+'/image').status_code==200
        project=next(p for p in c.get('/api/projects').json() if p['id']=='pixabay-preview')
        assert project['assets'][0]['allowed_export'] and not project['assets'][0]['display_url']
    assert not policy.apply(a).allowed_temporary_analysis
