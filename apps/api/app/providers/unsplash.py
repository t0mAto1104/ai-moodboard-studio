import re
from app.providers.base import Provider,ProviderError
from app.ai.llm.credential_manager import credentials
from app.schemas.models import ImageAsset
class UnsplashProvider(Provider):
    name='unsplash';base='https://api.unsplash.com';interval=1.5;supported_filters=['orientation','color']
    def headers(self):
        key=credentials.get('image:unsplash')
        if not key:raise ProviderError('未配置 Unsplash Access Key')
        return {'Authorization':'Client-ID '+key,'Accept-Version':'v1'}
    async def search(self,query,filters,page,per_page):
        d=await self.request('/search/photos',{'query':query,'page':page,'per_page':per_page,**{k:v for k,v in filters.items() if k in self.supported_filters}},self.headers())
        return [self.normalize(r) for r in d['results']]
    async def get_asset_details(self,asset_id):
        if not re.fullmatch(r'[A-Za-z0-9_-]+',asset_id):raise ProviderError('Invalid photo ID')
        return self.normalize(await self.request('/photos/'+asset_id,headers=self.headers()))
    async def track_selection(self,asset):
        from urllib.parse import urlparse,parse_qsl
        url=asset.license_evidence.get('download_location','')
        parsed=urlparse(url)
        expected='/photos/'+asset.provider_asset_id+'/download'
        if parsed.scheme!='https' or parsed.hostname!='api.unsplash.com' or parsed.path!=expected or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ProviderError('Unsplash 下载事件地址无效')
        await self.request(expected,dict(parse_qsl(parsed.query)),self.headers(),cache=False)
    def normalize(self,r):
        id=r['id'];user=r.get('user') or {};urls=r.get('urls') or {};links=r.get('links') or {}
        return ImageAsset(id='unsplash:'+id,provider=self.name,provider_asset_id=id,title=r.get('alt_description') or r.get('description') or 'Unsplash photo',creator_name=user.get('name') or 'Unknown',creator_url=referral((user.get('links') or {}).get('html','')),source_page_url=referral(links.get('html','')),download_url=urls.get('full',''),image_url=urls.get('regular',''),thumbnail_url=urls.get('small',''),width=r.get('width',0),height=r.get('height',0),license_type='Unsplash License',license_url='https://unsplash.com/license',license_evidence={'source_verified':True,'download_location':links.get('download_location'),'license_basis':'official API Terms section 8; Unsplash License'},attribution_text=f"Photo by {user.get('name','Unknown')} on Unsplash")


def referral(url):
    from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
    if not url:return ''
    parts=urlsplit(url);query=dict(parse_qsl(parts.query))
    query.update(utm_source='ai_moodboard_studio',utm_medium='referral')
    return urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(query),parts.fragment))
