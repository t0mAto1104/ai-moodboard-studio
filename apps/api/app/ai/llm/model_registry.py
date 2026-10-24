import httpx
from app.ai.llm.credential_manager import credentials
from app.ai.llm.provider_manager import validate_base
class ModelRegistry:
    async def list(self,s):
        key=credentials.get(s.provider)
        if not key:return {'status':'unconfigured','models':[]}
        headers={'Authorization':'Bearer '+key};params=None
        endpoints={'openai':'https://api.openai.com/v1/models','deepseek':'https://api.deepseek.com/models','openrouter':'https://openrouter.ai/api/v1/models','anthropic':'https://api.anthropic.com/v1/models','gemini':'https://generativelanguage.googleapis.com/v1beta/models'}
        if s.api_base:
            validate_base(s.api_base);url=s.api_base.rstrip('/')+'/models'
        elif s.provider in endpoints:url=endpoints[s.provider]
        else:return {'status':'unsupported','models':[],'message':'请手动输入 Model ID'}
        if s.provider=='anthropic':headers={'x-api-key':key,'anthropic-version':'2023-06-01'}
        if s.provider=='gemini':headers={'x-goog-api-key':key}
        try:
            async with httpx.AsyncClient(timeout=15,follow_redirects=False) as c:r=await c.get(url,headers=headers,params=params)
            r.raise_for_status();d=r.json()
            models=[m['name'].removeprefix('models/') for m in d.get('models',[])] if s.provider=='gemini' else [m['id'] for m in d.get('data',[])]
            return {'status':'ok','models':models}
        except Exception:return {'status':'unavailable','models':[],'message':'无法获取列表，可手动填写 Model ID'}
registry=ModelRegistry()
