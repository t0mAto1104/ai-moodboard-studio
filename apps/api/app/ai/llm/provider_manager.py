import asyncio,json,time,uuid,os
from urllib.parse import urlparse
from pydantic import BaseModel,Field,SecretStr
from typing import Literal
from app.db import store
from app.schemas.models import SearchIntent
from app.ai.llm.rule_based_parser import RuleBasedIntentParser
from app.ai.llm.credential_manager import credentials
PREFIX={'openai':'openai','anthropic':'anthropic','gemini':'gemini','deepseek':'deepseek','qwen':'openai','openrouter':'openrouter','custom':'openai'}
class LLMSettings(BaseModel):
    provider:Literal['openai','anthropic','gemini','deepseek','qwen','openrouter','custom']='openai'
    model_id:str=Field(default='',max_length=200)
    api_base:str=''
    enabled:bool=False
    fallback_model_id:str=''
    task_budget:float|None=Field(default=None,ge=0)
    total_budget:float|None=Field(default=None,ge=0)
    input_price_per_million:float|None=Field(default=None,ge=0)
    output_price_per_million:float|None=Field(default=None,ge=0)
    api_key:SecretStr|None=None

def validate_base(url):
    if not url:return
    import socket,ipaddress
    p=urlparse(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.query or p.fragment or p.port not in (None,443):raise ValueError('API Base 必须为无凭证的公网 HTTPS 地址')
    for addr in socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(addr[4][0]).is_global:raise ValueError('不允许内网 API 地址')

class LLMProviderManager:
    lock=asyncio.Lock()
    def settings(self):return LLMSettings(**(store.get('settings','llm') or {}))
    def public_settings(self):
        s=self.settings();d=s.model_dump(exclude={'api_key'});d['has_key']=bool(credentials.get(s.provider));return d
    def save(self,s):
        validate_base(s.api_base)
        if s.provider=='custom' and s.enabled and not s.api_base:raise ValueError('自定义供应商需要 API Base')
        if s.api_key is not None:credentials.save(s.provider,s.api_key.get_secret_value())
        store.put('settings','llm',s.model_dump(exclude={'api_key'}));return self.public_settings()
    async def call(self,prompt,s,model):
        key=credentials.get(s.provider)
        if not key:raise ValueError('未配置 API Key')
        os.environ.setdefault('LITELLM_LOCAL_MODEL_COST_MAP','True')
        import litellm
        litellm.suppress_debug_info=True;litellm.turn_off_message_logging=True
        kwargs={'model':PREFIX[s.provider]+'/'+model,'messages':[{'role':'system','content':'Return only a JSON object matching this JSON Schema. Produce at most 4 useful English search queries. Never output URLs. '+json.dumps(SearchIntent.model_json_schema())},{'role':'user','content':prompt}], 'api_key':key,'timeout':25,'num_retries':0,'max_tokens':1500}
        base=s.api_base or ('https://dashscope.aliyuncs.com/compatible-mode/v1' if s.provider=='qwen' else '')
        if base:kwargs['api_base']=base
        response=await litellm.acompletion(**kwargs)
        u=response.usage
        cost=None
        if s.input_price_per_million is not None and s.output_price_per_million is not None:
            cost=(u.prompt_tokens*s.input_price_per_million+u.completion_tokens*s.output_price_per_million)/1e6
        else:
            try:cost=litellm.completion_cost(completion_response=response)
            except Exception:pass
        store.put('llm_usage',str(uuid.uuid4()),{'provider':s.provider,'model':model,'input_tokens':u.prompt_tokens,'output_tokens':u.completion_tokens,'cost_usd':cost,'cost_type':'estimate' if cost is not None else 'unknown','time':time.time()})
        content=response.choices[0].message.content or ''
        if content.startswith('```'):content=content.strip('`').removeprefix('json').strip()
        result=SearchIntent.model_validate_json(content);result.raw_prompt=prompt
        if any('://' in q for q in result.search_queries):raise ValueError('检索词不能是 URL')
        return result
    async def parse(self,prompt,force=False):
        s=self.settings();reason='未启用云端模型'
        if s.enabled and s.model_id:
            async with self.lock:
                reserved = 0.0
                for model in [s.model_id,s.fallback_model_id or s.model_id]:
                    # A configured budget requires user-supplied rates; never assume unknown cost is zero.
                    usage = store.all_rows('llm_usage')
                    spent=sum(x.get('cost_usd') or 0 for x in usage)
                    if s.task_budget is not None or s.total_budget is not None:
                        if s.total_budget is not None and any(x.get('cost_usd') is None for x in usage):
                            reason='预算保护：历史调用存在未知费用';break
                        if s.input_price_per_million is None or s.output_price_per_million is None:
                            reason='预算保护：请先设置模型输入/输出单价';break
                        upper=((len(prompt.encode())+6000)*s.input_price_per_million+1500*s.output_price_per_million)/1e6
                        if (s.task_budget is not None and reserved+upper>s.task_budget) or (s.total_budget is not None and spent+reserved+upper>s.total_budget):reason='预算上限已触发';break
                        reserved += upper
                    try:return await self.call(prompt,s,model),'cloud',None
                    except Exception as e:reason='云端请求或 JSON 校验失败（'+type(e).__name__+'）'
        if force:raise ValueError(reason)
        return RuleBasedIntentParser().parse(prompt),'rules',reason
manager=LLMProviderManager()
