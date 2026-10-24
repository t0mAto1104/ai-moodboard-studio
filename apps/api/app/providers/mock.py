from io import BytesIO
from PIL import Image,ImageDraw
from app.providers.base import Provider
from app.schemas.models import ImageAsset
COLORS=['#7B91A8','#BDC7D1','#DCE5EC','#59716F','#CBB9A0','#4E5963','#AEAF9D','#D3CEC5','#879C9E','#92959B','#B7A18C','#73849A']
def fixture_bytes(index):
    i=int(index)%12;im=Image.new('RGB',(640,480),COLORS[i]);d=ImageDraw.Draw(im)
    for n in range(i%4+2):
        x=45+n*100;d.rounded_rectangle((x,70+(n%2)*45,x+75,400-n*20),radius=15,fill=COLORS[(i+n+3)%12],outline='#eeeeee',width=3)
    b=BytesIO();im.save(b,'PNG');return b.getvalue()
class MockProvider(Provider):
    name='mock'
    async def search(self,query,filters,page,per_page):
        if query=='empty':return []
        return [self.normalize({'id':i}) for i in range((page-1)*per_page,min(12,page*per_page))]
    def normalize(self,r):
        i=str(r['id']);return ImageAsset(id='mock:'+i,provider='mock',provider_asset_id=i,title='Demo material study '+i,description='Geometric test fixture, not a stock photograph',creator_name='Mood Board test fixture',source_page_url='',thumbnail_url='/api/assets/mock:'+i+'/image',image_url='/api/assets/mock:'+i+'/image',width=640,height=480,license_type='cc0',license_url='https://creativecommons.org/publicdomain/zero/1.0/',license_evidence={'source_verified':True,'fixture':True},attribution_text='Procedural test fixture '+i+' — AI Mood Board Studio / CC0')
    async def get_asset_details(self,asset_id):return self.normalize({'id':int(asset_id)})
