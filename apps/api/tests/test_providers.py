import asyncio
import httpx,pytest
from app.providers.artic import ArticProvider
from app.providers.metmuseum import MetProvider
from app.providers.openverse import OpenverseProvider
from app.providers.mock import MockProvider
from app.pipeline.license_filter import policy
from app.schemas.models import SearchRequest
from app.pipeline.retrieval import retrieve
from app.db import store

def test_normalization_and_policy():
    a=ArticProvider().normalize({'id':3,'title':'Vase','image_id':'abc','iiif_base':'https://www.artic.edu/iiif/2','is_public_domain':True})
    assert policy.apply(a).allowed_export and a.provider_asset_id=='3'
    b=OpenverseProvider().normalize({'id':'uuid','license':'cc0','url':'https://example.org/a.jpg'})
    assert not policy.apply(b).allowed_export and not b.allowed_temporary_analysis
    with pytest.raises(ValueError):policy.require_export(b)
@pytest.mark.asyncio
async def test_met_pagination():
    seen=[]
    def handle(r):
        seen.append(str(r.url))
        if '/v1.1/search' in r.url.path:return httpx.Response(200,json={'objectIDs':[10]})
        return httpx.Response(200,json={'objectID':10,'isPublicDomain':True,'primaryImageSmall':'https://images.metmuseum.org/a.jpg'})
    p=MetProvider(httpx.MockTransport(handle));p.interval=0
    rows=await p.search('paging-test',{},2,3)
    assert len(rows)==1 and 'offset=3' in seen[0] and '/v1.1/' in seen[0]
@pytest.mark.asyncio
async def test_429_and_timeout(monkeypatch):
    async def no_wait(*a):pass
    monkeypatch.setattr(asyncio,'sleep',no_wait)
    calls=[]
    def handle(r):
        calls.append(1)
        if len(calls)<3:return httpx.Response(429,headers={'Retry-After':'0'})
        return httpx.Response(200,json={'results':[]})
    p=OpenverseProvider(httpx.MockTransport(handle));p.interval=0
    assert await p.search('retry-test',{},1,1)==[] and len(calls)==3
    def timeout(r):raise httpx.ReadTimeout('timeout')
    p=OpenverseProvider(httpx.MockTransport(timeout));p.interval=0
    with pytest.raises(Exception,match='网络'):await p.search('timeout-test',{},1,1)
@pytest.mark.asyncio
async def test_mock_empty_and_pagination():
    p=MockProvider();assert await p.search('empty',{},1,5)==[]
    a=await p.search('a',{},1,5);b=await p.search('a',{},2,5)
    assert not {x.id for x in a}&{x.id for x in b}
@pytest.mark.asyncio
async def test_partial_results():
    r=await retrieve(SearchRequest(queries=['fixture'],providers=['mock','pixabay'],per_page=3),lambda **kw:None)
    assert len(r['assets'])==3 and r['errors'][0]['provider']=='pixabay'

def test_optional_normalization():
    from app.providers.pixabay import PixabayProvider
    from app.providers.unsplash import UnsplashProvider
    a=PixabayProvider().normalize({'id':12,'tags':'metal','user':'artist','webformatURL':'https://pixabay.com/get/x.jpg'})
    b=UnsplashProvider().normalize({'id':'abc','urls':{'small':'https://images.unsplash.com/a'},'user':{'name':'artist'},'links':{'html':'https://unsplash.com/photos/abc'}})
    assert not policy.apply(a).allowed_export and not policy.apply(b).allowed_temporary_analysis
    assert PixabayProvider.ttl==86400
