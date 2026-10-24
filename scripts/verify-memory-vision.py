"""Verify real SigLIP ranking of existing, user-authorized Unsplash candidates via local API."""
import argparse,json,sys,time
from pathlib import Path
import httpx
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'apps/api'))
from app.core.config import DATA
from app.db import store
parser=argparse.ArgumentParser()
parser.add_argument('--enable-authorized-unsplash',action='store_true',help='Only use after user confirms local inference rights')
args=parser.parse_args()
def snapshot():
    return {str(p.relative_to(DATA)):(p.stat().st_size,p.stat().st_mtime_ns) for folder in ('cache','uploads') for p in (DATA/folder).glob('*') if p.is_file()}
with httpx.Client(base_url='http://127.0.0.1:8765/api',timeout=30,headers={'X-Moodboard-Request':'1'},trust_env=False) as client:
    if args.enable_authorized_unsplash:
        cfg=next(p for p in client.get('/providers').json() if p['id']=='unsplash')
        r=client.put('/providers/unsplash/settings',json={'enabled':cfg['enabled'],'analysis_enabled':True,'analysis_rights_confirmed':True});r.raise_for_status()
    assets=[];selected_intent=None
    for project in client.get('/projects').json():
        for asset in project.get('assets',[]):
            if asset['provider']=='unsplash' and asset['id'] not in {a['id'] for a in assets}:
                assets.append(asset)
                if selected_intent is None:selected_intent=project['intent']
    assert assets,'Search Unsplash once first'
    assets=assets[:3]
    before=snapshot();vectors_before=len(store.all_rows('embeddings'))
    body={'asset_ids':[a['id'] for a in assets],'intent':selected_intent}
    started=time.perf_counter();r=client.post('/search/rank',json=body);r.raise_for_status();job_id=r.json()['job_id']
    deadline=time.monotonic()+300
    while time.monotonic()<deadline:
        r=client.get('/jobs/'+job_id);r.raise_for_status();job=r.json()
        if job['status']=='failed':raise RuntimeError(job['error'])
        if job['status']=='completed':break
        time.sleep(.5)
    else:raise TimeoutError('Analysis job exceeded 300 seconds')
    result=job['result'];stats=result['stats']
    assert stats['ranking_mode']=='siglip2' and stats['analyzed_count']==len(assets),stats
    assert before==snapshot(),'Image file snapshot changed'
    assert len(store.all_rows('embeddings'))==vectors_before,'Temporary-analysis vectors persisted unexpectedly'
    report={'passed':True,'job_id':job_id,'provider':'unsplash','authorization':'user confirmed local inference rights in conversation','seconds':time.perf_counter()-started,'stats':stats,'image_files_unchanged':True,'persistent_embedding_count_unchanged':True,'scores':[{'id':a['id'],'semantic_score':a['semantic_score'],'final_score':a['final_score'],'model_id':a.get('embedding_model_id'),'model_revision':a.get('embedding_model_revision')} for a in result['assets'] if a.get('embedding_model_id')]}
    (root/'docs/memory-vision-live.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
