"""Isolated real HTTP-routing workflow; --vision uses existing offline SigLIP weights."""
import argparse,io,json,os,resource,sys,tempfile,time,zipfile
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--vision',action='store_true')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'apps/api'))
with tempfile.TemporaryDirectory(prefix='moodboard-smoke-') as folder:
    os.environ['MOODBOARD_DATA_DIR']=folder
    from app.db import store
    store.metadata.create_all(store.engine)
    from app.main import app
    from app.ai.embeddings.siglip2 import provider
    from fastapi.testclient import TestClient
    from PIL import Image
    times={}
    with TestClient(app,headers={'X-Moodboard-Request':'1'}) as client:
        def post(path,data):
            response=client.post('/api'+path,json=data)
            response.raise_for_status()
            return response.json()
        def job(path,data):
            start=time.perf_counter();id=post(path,data)['job_id']
            deadline=time.monotonic()+300
            while time.monotonic()<deadline:
                response=client.get('/api/jobs/'+id);response.raise_for_status();value=response.json()
                if value['status']=='completed':return value['result'],time.perf_counter()-start
                if value['status'] in ('failed','cancelled'):raise RuntimeError(value)
                time.sleep(.05)
            raise TimeoutError(path)
        intent=post('/intent/parse',{'prompt':'简约冷色系金属与磨砂玻璃工业设计'})['intent']
        intent['target_image_count']=6
        search,times['search']=job('/search',{'queries':intent['search_queries'],'providers':['mock'],'per_page':8})
        project=post('/projects',{'name':'Smoke validation','intent':intent,'asset_ids':[a['id'] for a in search['assets']]})
        id=project['id']
        generated,times['generate']=job('/projects/'+id+'/generate',{'use_vision':args.vision})
        project=client.get('/api/projects/'+id).json()
        assert project['items']
        original={x['asset_id'] for x in project['items'] if x['kind']=='image'}
        response=client.patch('/api/projects/'+id,json={'layout_style':'material'});response.raise_for_status()
        job('/projects/'+id+'/generate',{'relayout_only':True})
        reopened=client.get('/api/projects/'+id).json()
        assert original=={x['asset_id'] for x in reopened['items'] if x['kind']=='image'}
        for fmt in ('png','pdf'):
            result,times['export_'+fmt]=job('/projects/'+id+'/export',{'format':fmt})
            response=client.get(result['url']);response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                data=archive.read('moodboard.'+fmt)
                assert archive.read('attribution.txt')
                assert json.loads(archive.read('license-manifest.json'))
                if fmt=='png':
                    with Image.open(io.BytesIO(data)) as image:
                        assert image.size==(1200,675)
                        assert image.convert('RGB').getpixel((0,0))==(255,255,255)
                else:assert data.startswith(b'%PDF-')
        report={'passed':True,'source':'explicit procedural Mock Provider','vision_requested':args.vision,'device':provider.device,'model_id':provider.model_id,'revision':provider.revision,'selected_count':len(original),'stage_seconds':times,'generation_stats':generated['stats'],'process_peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024),'human_relevance_metrics':None}
        if args.vision:
            assert generated['stats']['ranking_mode']=='siglip2',generated
            vectors=store.all_rows('embeddings');assert vectors and all(v['dimension']==768 for v in vectors)
            report['embedding_count']=len(vectors)
        if provider.device=='mps':report['mps_driver_allocated_bytes']=provider.torch.mps.driver_allocated_memory()
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(report,ensure_ascii=False,indent=2))
