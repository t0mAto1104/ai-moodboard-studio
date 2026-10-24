from app.providers.base import Provider
from app.schemas.models import ImageAsset
class ArticProvider(Provider):
    name='artic';base='https://api.artic.edu/api/v1';supported_filters=['public_domain']
    fields='id,title,image_id,is_public_domain,artist_display,medium_display'
    async def search(self,query,filters,page,per_page):
        d=await self.request('/artworks/search',{'q':query,'page':page,'limit':per_page,'fields':self.fields,'query[term][is_public_domain]':'true'})
        return [self.normalize({**r,'iiif_base':d.get('config',{}).get('iiif_url','')}) for r in d['data'] if r.get('is_public_domain') is True and r.get('image_id')]
    def normalize(self,r):
        ident=str(r['id']);base=r.get('iiif_base','');img=f"{base}/{r['image_id']}/full/843,/0/default.jpg" if base else ''
        return ImageAsset(id='artic:'+ident,provider=self.name,provider_asset_id=ident,title=r.get('title') or 'Untitled',creator_name=r.get('artist_display') or 'Unknown',description=r.get('medium_display') or '',source_page_url=f'https://www.artic.edu/artworks/{ident}',image_url=img,thumbnail_url=img,license_type='cc0' if r.get('is_public_domain') else 'Unknown',license_url='https://www.artic.edu/open-access/open-access-images',license_evidence={'source_verified':r.get('is_public_domain') is True,'is_public_domain':r.get('is_public_domain'),'api_record':self.base+'/artworks/'+ident},attribution_text=f"{r.get('title','Untitled')} — {r.get('artist_display','Unknown')} / Art Institute of Chicago")
    async def get_asset_details(self,asset_id):
        d=await self.request('/artworks/'+str(int(asset_id)),{'fields':self.fields})
        return self.normalize({**d['data'],'iiif_base':d.get('config',{}).get('iiif_url','')})
