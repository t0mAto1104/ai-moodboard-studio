"""One low-volume probe per source; credentials never printed or saved."""
import asyncio,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps/api'))
from app.providers.registry import PROVIDERS
from app.pipeline.license_filter import policy
from app.ai.llm.credential_manager import credentials
async def main():
    report=[]
    for name in ['unsplash','artic','metmuseum','openverse','pixabay']:
        if name in ('unsplash','pixabay') and not credentials.get('image:'+name):
            report.append({'provider':name,'status':'not_configured'});continue
        start=time.perf_counter()
        try:
            rows=await PROVIDERS[name].search('kitty' if name=='unsplash' else 'ceramic',{},1,3)
            rows=[policy.apply(a) for a in rows]
            report.append({'provider':name,'status':'ok','count':len(rows),'preview_count':sum(bool(a.display_url) for a in rows),'reference_board_count':sum(a.allowed_reference_board for a in rows),'seconds':round(time.perf_counter()-start,2)})
        except Exception as e:
            from app.providers.base import ProviderError
            report.append({'provider':name,'status':'failed','error':str(e) if isinstance(e,ProviderError) else type(e).__name__,'seconds':round(time.perf_counter()-start,2)})
    dest=Path(__file__).resolve().parents[1]/'docs/source-connection-check.json'
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
asyncio.run(main())
