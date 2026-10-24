import asyncio
import pytest
from pydantic import ValidationError
from app.db import store
from app.jobs.queue import JobQueue
from app.ai.llm.provider_manager import LLMProviderManager, LLMSettings
from app.schemas.models import SearchIntent

def test_palette_validation():
    with pytest.raises(ValidationError):
        SearchIntent(subject='metal',search_queries=['metal'],target_palette=['blue'])

def test_restart_recovery():
    queue=JobQueue()
    for state in ('queued','running','completed','cancelled'):
        store.put('background_jobs',state,{'id':state,'status':state})
    queue.recover()
    for state in ('queued','running'):assert store.get('background_jobs',state)['status']=='failed'
    for state in ('completed','cancelled'):assert store.get('background_jobs',state)['status']==state

@pytest.mark.asyncio
async def test_cancel_job():
    queue=JobQueue();started=asyncio.Event()
    async def work(progress):
        started.set()
        await asyncio.Event().wait()
    id=queue.start(work)
    await started.wait()
    queue.cancel(id)
    await queue.shutdown()
    assert store.get('background_jobs',id)['status']=='cancelled'

@pytest.mark.asyncio
async def test_retry_shares_task_budget(monkeypatch):
    manager=LLMProviderManager()
    settings=LLMSettings(enabled=True,model_id='manual',input_price_per_million=1,output_price_per_million=1,task_budget=.01)
    monkeypatch.setattr(manager,'settings',lambda:settings)
    monkeypatch.setattr(store,'all_rows',lambda _:[])
    attempts=[]
    async def fail(*args):
        attempts.append(1)
        raise ValueError('invalid JSON')
    monkeypatch.setattr(manager,'call',fail)
    _,mode,reason=await manager.parse('metal')
    assert mode=='rules' and len(attempts)==1 and '预算' in reason

@pytest.mark.asyncio
async def test_unknown_cost_blocks_total_budget(monkeypatch):
    manager=LLMProviderManager()
    monkeypatch.setattr(manager,'settings',lambda:LLMSettings(enabled=True,model_id='manual',total_budget=10,input_price_per_million=1,output_price_per_million=1))
    monkeypatch.setattr(store,'all_rows',lambda _:[{'cost_usd':None}])
    async def forbidden(*args):pytest.fail('Unknown cost must prevent paid requests')
    monkeypatch.setattr(manager,'call',forbidden)
    _,mode,reason=await manager.parse('metal')
    assert mode=='rules' and '未知费用' in reason
