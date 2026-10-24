import pytest,zipfile
from fastapi.testclient import TestClient
from app.main import app
from app.providers.mock import MockProvider
from app.db import store
from app.pipeline.license_filter import policy
from app.layout.engine import layout,validate_items,RATIOS
from app.exports.render import export_project
from app.core.config import DATA
from app.security.images import validate_url
from app.ai.llm.rule_based_parser import RuleBasedIntentParser

def fixtures():
    rows=[policy.apply(MockProvider().normalize({'id':i})) for i in range(5)]
    for a in rows:store.put('image_assets',a.id,a.model_dump())
    return rows
@pytest.mark.parametrize('style',['editorial','material','collage'])
@pytest.mark.parametrize('ratio',list(RATIOS))
def test_layout_bounds(style,ratio):
    rows=fixtures();items=layout(rows,style,ratio)
    assert validate_items(items,ratio,[a.id for a in rows])

def test_save_reopen_security():
    c=TestClient(app);rows=fixtures();body={'name':'test','intent':RuleBasedIntentParser().parse('metal').model_dump(),'asset_ids':[a.id for a in rows]}
    assert c.post('/api/projects',json=body).status_code==403
    assert c.post('/api/projects',json=body,headers={'Origin':'https://evil.example','X-Moodboard-Request':'1'}).status_code==403
    p=c.post('/api/projects',json=body,headers={'X-Moodboard-Request':'1'}).json()
    assert c.get('/api/projects/'+p['id']).json()['name']=='test'
    invalid=layout(rows);invalid[0]['x']=10000
    assert c.patch('/api/projects/'+p['id'],json={'items':invalid},headers={'X-Moodboard-Request':'1'}).status_code==422
@pytest.mark.asyncio
async def test_export_allowed_and_unknown():
    rows=fixtures();p={'id':'test','ratio':'16:9','commercial':True,'asset_ids':[a.id for a in rows],'items':layout(rows)}
    for fmt in ['png','pdf']:
        e=await export_project(p,fmt)
        with zipfile.ZipFile(DATA/'exports'/(e['id']+'.zip')) as z:assert {'moodboard.'+fmt,'attribution.txt','license-manifest.json'}==set(z.namelist())
    a=rows[0];a.license_type='Unknown';store.put('image_assets',a.id,a.model_dump())
    with pytest.raises(ValueError,match='许可'):await export_project(p,'png')
@pytest.mark.parametrize('url',['http://127.0.0.1/a','https://localhost/a','file:///etc/passwd','https://www.artic.edu.evil.com/a','https://user:pass@www.artic.edu/a'])
def test_ssrf(url):
    with pytest.raises(ValueError):validate_url(url)

def test_upload_requires_rights():
    from app.providers.mock import fixture_bytes
    c=TestClient(app);headers={'X-Moodboard-Request':'1'}
    assert c.post('/api/assets/upload',files={'file':('a.png',fixture_bytes(1),'image/png')},headers=headers).status_code==400
    r=c.post('/api/assets/upload',files={'file':('a.png',fixture_bytes(1),'image/png')},data={'rights_confirmed':'true'},headers=headers)
    assert r.status_code==200 and r.json()['allowed_export'] and r.json()['license_type']=='user-owned'
    assert c.get('/api/assets/'+r.json()['id']+'/image').status_code==200
