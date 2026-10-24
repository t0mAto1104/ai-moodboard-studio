import asyncio
from app.providers.base import Provider
from app.schemas.models import ImageAsset
class MetProvider(Provider):
    name='metmuseum';base='https://collectionapi.metmuseum.org/public/collection';interval=.3;supported_filters=['hasImages']
    async def search(self,query,filters,page,per_page):
        d=await self.request('/v1.1/search',{'q':query,'hasImages':'true','offset':(page-1)*per_page,'limit':per_page})
        results=await asyncio.gather(*(self.get_asset_details(i) for i in (d.get('objectIDs') or [])[:per_page]),return_exceptions=True)
        return [a for a in results if isinstance(a,ImageAsset) and a.license_evidence.get('source_verified') and a.image_url]
    async def get_asset_details(self,asset_id):return self.normalize(await self.request('/v1/objects/'+str(int(asset_id))))
    def normalize(self,r):
        ident=str(r['objectID']);img=r.get('primaryImageSmall') or r.get('primaryImage') or ''
        return ImageAsset(id='metmuseum:'+ident,provider=self.name,provider_asset_id=ident,title=r.get('title') or 'Untitled',creator_name=r.get('artistDisplayName') or 'Unknown',description=r.get('medium') or '',source_page_url=r.get('objectURL') or '',image_url=img,thumbnail_url=img,license_type='cc0' if r.get('isPublicDomain') else 'Unknown',license_url='https://www.metmuseum.org/about-the-met/policies-and-documents/open-access',license_evidence={'source_verified':r.get('isPublicDomain') is True,'isPublicDomain':r.get('isPublicDomain'),'api_record':self.base+'/v1/objects/'+ident},attribution_text=f"{r.get('title','Untitled')} — {r.get('artistDisplayName','Unknown')} / The Metropolitan Museum of Art")
