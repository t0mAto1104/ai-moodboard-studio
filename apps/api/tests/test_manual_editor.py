import io,zipfile
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.db import store
from app.providers.mock import MockProvider
from app.pipeline.license_filter import policy
from app.ai.llm.rule_based_parser import RuleBasedIntentParser
from app.exports.render import export_project
from app.core.config import DATA
from app.schemas.models import LayoutItem
H={'X-Moodboard-Request':'1'}
def body():
    rows=[policy.apply(MockProvider().normalize({'id':i})) for i in range(3)]
    for a in rows:store.put('image_assets',a.id,a.model_dump())
    return {'name':'Favorite board','intent':RuleBasedIntentParser().parse('metal').model_dump(),'asset_ids':[a.id for a in rows],'from_selection':True}

def test_manual_selection_save_reopen_and_permissions():
    c=TestClient(app);b=body();r=c.post('/api/projects',json=b,headers=H)
    assert r.status_code==200,r.text
    p=r.json();assert {i['asset_id'] for i in p['items']}==set(b['asset_ids'])
    assert p['stats']['ranking_mode']=='manual'
    text=LayoutItem(id='text',kind='text',x=30,y=30,width=400,height=100,text='Design direction',font_size=48,font_weight='bold',text_align='center',font_family='serif').model_dump()
    r=c.patch('/api/projects/'+p['id'],json={'items':p['items']+[text],'background':'#123456'},headers=H)
    assert r.status_code==200,r.text
    reopened=c.get('/api/projects/'+p['id']).json()
    assert reopened['background']=='#123456'
    assert reopened['items'][-1]['font_size']==48 and reopened['items'][-1]['font_weight']=='bold'
    assert c.patch('/api/projects/'+p['id'],json={'background':'not a color'},headers=H).status_code==422
    assert c.patch('/api/projects/'+p['id'],json={'items':[{**text,'font_size':50000}]},headers=H).status_code==422
    restricted=store.get('image_assets',b['asset_ids'][0]);restricted['license_type']='Unknown';store.put('image_assets',restricted['id'],restricted)
    assert c.post('/api/projects',json=b,headers=H).status_code==422
    assert c.post('/api/projects',json={**b,'asset_ids':['missing']},headers=H).status_code==422
    assert c.post('/api/projects',json={**b,'asset_ids':[]},headers=H).status_code==422

@pytest.mark.asyncio
async def test_export_background_shapes_text_style_and_reopen():
    items=[LayoutItem(id='oval',kind='color',shape='ellipse',fill='#ff0000',x=100,y=100,width=100,height=100).model_dump(),LayoutItem(id='txt',kind='text',text='Design\n材质',fill='#111111',font_size=42,font_weight='bold',text_align='center',x=300,y=100,width=300,height=150).model_dump()]
    p={'id':'styled','ratio':'16:9','background':'#123456','asset_ids':[],'items':items}
    for fmt in ('png','pdf'):
        result=await export_project(p,fmt)
        with zipfile.ZipFile(DATA/'exports'/(result['id']+'.zip')) as z:
            if fmt=='png':
                im=Image.open(io.BytesIO(z.read('moodboard.png')))
                assert im.getpixel((0,0))==(18,52,86)
                assert im.getpixel((150,150))==(255,0,0)
                assert im.getpixel((100,100))==(18,52,86)
                assert sum(im.getpixel((x,y))!=(18,52,86) for x in range(300,600) for y in range(100,250))>500
            else:assert z.read('moodboard.pdf').startswith(b'%PDF')
            assert 'attribution.txt' in z.namelist()
