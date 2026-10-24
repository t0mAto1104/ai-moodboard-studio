import asyncio,time,hashlib,json
import httpx
from app.db import store
GLOBAL=asyncio.Semaphore(6)
class ProviderError(Exception):pass
class Provider:
    name='base'; base=''; interval=1.1; ttl=3600; timeout=15; supported_filters=[]
    def __init__(self,transport=None):
        self.transport=transport;self.sem=asyncio.Semaphore(2);self.pace=asyncio.Lock();self.last=0
    async def request(self,path,params=None,headers=None,cache=True):
        key=hashlib.sha256(json.dumps([self.name,path,params],sort_keys=True).encode()).hexdigest()
        cached=store.get('provider_responses_cache',key) if cache else None
        if cached and time.time()-cached['time']<self.ttl:return cached['data']
        for attempt in range(3):
            async with self.sem:
                async with self.pace:
                    await asyncio.sleep(max(0,self.interval-(time.monotonic()-self.last)));self.last=time.monotonic()
                async with GLOBAL:
                    try:
                        async with httpx.AsyncClient(timeout=self.timeout,transport=self.transport,follow_redirects=False) as client:
                            r=await client.get(self.base+path,params=params,headers=headers or {})
                    except httpx.RequestError:
                        if attempt==2:raise ProviderError('网络超时或连接失败')
                        await asyncio.sleep(2**attempt);continue
            quota={k:r.headers.get(v) for k,v in {'limit':'x-ratelimit-limit','remaining':'x-ratelimit-remaining'}.items() if r.headers.get(v) is not None}
            store.put('settings','diagnostics:'+self.name,{'checked_at':time.time(),'http_status':r.status_code,'quota':quota})
            if r.status_code==429 or r.status_code>=500:
                if attempt==2:raise ProviderError(f'服务限流或暂不可用 ({r.status_code})')
                try:delay=float(r.headers.get('retry-after',2**attempt))
                except ValueError:delay=2**attempt
                await asyncio.sleep(min(5,max(0,delay)));continue
            if r.status_code==401:raise ProviderError('API Key 无效或已失效 (HTTP 401)')
            if r.is_error:raise ProviderError(f'图库返回 HTTP {r.status_code}')
            data=r.json()
            if cache:store.put('provider_responses_cache',key,{'time':time.time(),'data':data})
            return data
        raise ProviderError('重试次数已用尽')
    async def search(self,query,filters,page,per_page):raise NotImplementedError
    def normalize(self,raw):raise NotImplementedError
    async def get_asset_details(self,asset_id):return {'status':'unsupported'}
    def get_usage_policy(self):return {'max_concurrency':2,'min_interval':self.interval,'cache_seconds':self.ttl,'timeout':self.timeout,'supported_filters':self.supported_filters}
    async def health_check(self):
        try:await self.search('ceramic',{},1,1);return {'status':'ok'}
        except Exception as e:return {'status':'unavailable','error':str(e) if isinstance(e,ProviderError) else '请求失败'}
