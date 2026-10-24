import asyncio,time,uuid
from app.db import store
class JobQueue:
    def __init__(self):self.tasks={};self.slots=asyncio.Semaphore(2)
    def recover(self):
        for job in store.all_rows('background_jobs'):
            if job['status'] in ('queued', 'running'):
                self.update(job['id'], status='failed', error='应用已重启，请重新运行任务')
    async def shutdown(self):
        tasks = list(self.tasks.values())
        for id in list(self.tasks):
            self.cancel(id)
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    def update(self,id,**values):
        job=store.get('background_jobs',id)
        if job and job['status']!='cancelled':job.update(values);store.put('background_jobs',id,job)
    def start(self,fn):
        id=str(uuid.uuid4());store.put('background_jobs',id,{'id':id,'status':'queued','progress':0,'created_at':time.time(),'result':None,'error':None})
        async def run():
            try:
                async with self.slots:
                    self.update(id,status='running');result=await fn(lambda **kw:self.update(id,**kw));self.update(id,status='completed',progress=100,result=result)
            except asyncio.CancelledError:pass
            except Exception as e:self.update(id,status='failed',error=str(e)[:400] if isinstance(e,ValueError) else '任务失败：'+type(e).__name__)
            finally:self.tasks.pop(id,None)
        self.tasks[id]=asyncio.create_task(run());return id
    def cancel(self,id):
        j=store.get('background_jobs',id)
        if j and j['status'] in ('queued','running'):
            j['status']='cancelled';store.put('background_jobs',id,j)
            if id in self.tasks:self.tasks[id].cancel()
        return j
queue=JobQueue()
