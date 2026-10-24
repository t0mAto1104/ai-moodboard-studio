from app.providers.base import Provider,ProviderError
from app.ai.llm.credential_manager import credentials
from app.schemas.models import ImageAsset
class PixabayProvider(Provider):
    name='pixabay';base='https://pixabay.com';ttl=86400;interval=1.1;supported_filters=['image_type','orientation','colors','safesearch']
    def key(self):
        key=credentials.get('image:pixabay')
        if not key:raise ProviderError('未配置 Pixabay API Key')
        return key
    async def search(self,query,filters,page,per_page):
        params={'key':self.key(),'q':query[:100],'page':page,'per_page':max(3,per_page),'safesearch':'true','image_type':'photo'}
        params.update({k:v for k,v in filters.items() if k in self.supported_filters})
        d=await self.request('/api/',params);return [self.normalize(r) for r in d['hits']]
    async def get_asset_details(self,asset_id):
        d=await self.request('/api/',{'key':self.key(),'id':int(asset_id)})
        return self.normalize(d['hits'][0]) if d['hits'] else {'status':'not_found'}
    def normalize(self,r):
        id=str(r['id']);return ImageAsset(id='pixabay:'+id,provider=self.name,provider_asset_id=id,title=r.get('tags','Pixabay photo'),creator_name=r.get('user') or 'Unknown',creator_url=f"https://pixabay.com/users/{r.get('user','')}-{r.get('user_id','')}/",source_page_url=r.get('pageURL') or '',thumbnail_url=r.get('previewURL') or '',download_url=r.get('largeImageURL') or r.get('webformatURL') or '',image_url=r.get('webformatURL') or '',width=r.get('imageWidth',0),height=r.get('imageHeight',0),license_type='Pixabay Content License',license_url='https://pixabay.com/service/license-summary/',license_evidence={'source_verified':True,'license_basis':'official API Content License; creative derivative export permitted'},attribution_text=f"{r.get('user','Unknown')} / Pixabay")
