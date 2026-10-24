import pytest
from pydantic import ValidationError
from app.ai.llm.rule_based_parser import RuleBasedIntentParser
from app.ai.llm.provider_manager import LLMProviderManager,LLMSettings
from app.schemas.models import SearchIntent

def test_chinese_rules():
    i=RuleBasedIntentParser().parse('简约冷色工业产品，银色金属、磨砂玻璃，高级干净')
    assert 'minimalist' in i.style_keywords and 'frosted glass' in i.materials
    assert len(set(i.search_queries))==len(i.search_queries)<=4

def test_invalid_schema():
    with pytest.raises(ValidationError):SearchIntent.model_validate_json('{"subject":"test","search_queries":[]}')
@pytest.mark.asyncio
async def test_cloud_failure_fallback(monkeypatch):
    m=LLMProviderManager();monkeypatch.setattr(m,'settings',lambda:LLMSettings(enabled=True,model_id='user-model'))
    count=[]
    async def fail(*a):count.append(1);raise ValueError('bad json')
    monkeypatch.setattr(m,'call',fail)
    i,mode,w=await m.parse('简约金属')
    assert mode=='rules' and len(count)==2 and i.materials

def test_secret_not_echoed_on_validation():
    from fastapi.testclient import TestClient
    from app.main import app
    r=TestClient(app).put('/api/llm/settings',json={'api_key':'secret-never-echo','provider':'invalid'},headers={'X-Moodboard-Request':'1'})
    assert r.status_code==422 and 'secret-never-echo' not in r.text
