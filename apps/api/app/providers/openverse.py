from app.providers.base import Provider
from app.schemas.models import ImageAsset
class OpenverseProvider(Provider):
    name='openverse';base='https://api.openverse.org/v1';interval=3.1;supported_filters=['license']
    async def search(self,query,filters,page,per_page):
        d=await self.request('/images/',{'q':query[:200],'page':page,'page_size':min(20,per_page),'license':'cc0,pdm,by','mature':'false'})
        return [self.normalize(r) for r in d['results']]
    async def get_asset_details(self,asset_id):
        from uuid import UUID
        return self.normalize(await self.request('/images/'+str(UUID(asset_id))+'/'))
    def normalize(self,r):
        ident=str(r['id']);return ImageAsset(id='openverse:'+ident,provider=self.name,provider_asset_id=ident,title=r.get('title') or 'Untitled',creator_name=r.get('creator') or 'Unknown',creator_url=r.get('creator_url') or '',source_page_url=r.get('foreign_landing_url') or '',thumbnail_url=r.get('thumbnail') or '',image_url=r.get('url') or '',width=r.get('width') or 0,height=r.get('height') or 0,license_type=r.get('license') or 'Unknown',license_url=r.get('license_url') or '',license_evidence={'source_verified':False,'index_license':r.get('license'),'source':r.get('source'),'reason':'Openverse index is not source verification'},attribution_text=f"{r.get('title','Untitled')} — {r.get('creator','Unknown')} / {r.get('source','Openverse')}")
