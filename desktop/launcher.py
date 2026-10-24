"""Standalone macOS entry point. No external Python/Node or model files required to launch."""
import argparse
import json
import logging
import multiprocessing
import os
from pathlib import Path
import socket
import sys
import threading
import time


def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test-report',type=Path)
    parser.add_argument('--data-dir',type=Path)
    parser.add_argument('--check-model-dir',type=Path)
    parser.add_argument('--no-window',action='store_true')
    return parser.parse_args()


def initialize_database():
    from alembic.config import Config
    from alembic import command
    from app.core.config import ROOT
    config=Config()
    config.set_main_option('script_location',str(ROOT/'apps/api/migrations'))
    command.upgrade(config,'head')


def self_test(report_path,model_path=None):
    import io
    import zipfile
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.config import DATA,ROOT,DESKTOP
    from app.db import store
    checks={}
    with TestClient(app,headers={'X-Moodboard-Request':'1'}) as client:
        def post(path,data):
            response=client.post('/api'+path,json=data);response.raise_for_status();return response.json()
        def job(path,data):
            id=post(path,data)['job_id'];deadline=time.monotonic()+180
            while time.monotonic()<deadline:
                response=client.get('/api/jobs/'+id);response.raise_for_status();j=response.json()
                if j['status']=='completed':return j['result']
                if j['status'] in ('failed','cancelled'):raise RuntimeError(j['error'])
                time.sleep(.05)
            raise TimeoutError(path)
        checks['health']=client.get('/api/health').json()['status']=='ok'
        checks['frontend']=client.get('/').status_code==200 and (ROOT/'apps/web/dist/index.html').is_file()
        checks['fresh_user_data']=client.get('/api/projects').json()==[] and client.get('/api/library').json()['favorites']==[]
        assert checks['fresh_user_data'],'Self-test must use a fresh test data directory'
        intent=post('/intent/parse',{'prompt':'简约冷色金属与磨砂玻璃'})['intent']
        results=job('/search',{'queries':intent['search_queries'][:1],'providers':['mock'],'per_page':3})
        checks['mock_search']=len(results['assets'])==3
        id=results['assets'][0]['id']
        tag=post('/library/tags',{'name':'安装包验证'})
        response=client.put('/api/library/favorites/'+id,json={'tag_ids':[tag['id']]});response.raise_for_status()
        checks['library']=client.get('/api/library').json()['favorites'][0]['tag_ids']==[tag['id']]
        project=post('/projects',{'name':'安装包自检','intent':intent,'asset_ids':[a['id'] for a in results['assets']]})
        job('/projects/'+project['id']+'/generate',{'use_vision':False})
        checks['project_save']=bool(client.get('/api/projects/'+project['id']).json()['items'])
        for fmt in ('png','pdf'):
            result=job('/projects/'+project['id']+'/export',{'format':fmt})
            response=client.get(result['url']);response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                data=archive.read('moodboard.'+fmt)
                checks['export_'+fmt]=data.startswith(b'\x89PNG' if fmt=='png' else b'%PDF-')
                checks['attribution_'+fmt]=bool(archive.read('attribution.txt'))
        # Exercise stock-license exports inside the frozen application too.
        # The network is explicitly mocked; no developer credentials are used.
        from unittest.mock import patch
        from app.providers.unsplash import UnsplashProvider
        from app.providers.pixabay import PixabayProvider
        from app.providers.registry import PROVIDERS
        from app.providers.mock import fixture_bytes
        from app.routers import assets as asset_router
        calls=[]
        async def track(asset):calls.append(asset.id)
        async def fetch(url):return fixture_bytes(3)
        with patch.object(PROVIDERS['unsplash'],'track_selection',track),patch.object(asset_router,'fetch_image',fetch):
            for source in ('unsplash','pixabay'):
                rows=[]
                for i in range(2):
                    if source=='unsplash':
                        id='package-export-'+str(i)
                        a=UnsplashProvider().normalize({'id':id,'urls':{'small':'https://images.unsplash.com/photo-test?w=400','regular':'https://images.unsplash.com/photo-test?w=1080'},'links':{'html':'https://unsplash.com/photos/'+id,'download_location':'https://api.unsplash.com/photos/'+id+'/download'},'user':{'name':'Package test artist','links':{'html':'https://unsplash.com/@test'}}})
                    else:a=PixabayProvider().normalize({'id':8800+i,'user':'Package test artist','pageURL':'https://pixabay.com/photos/test-'+str(8800+i)+'/','previewURL':'https://cdn.pixabay.com/photo/test.jpg','webformatURL':'https://pixabay.com/get/test.jpg'})
                    store.put('image_assets',a.id,a.model_dump());rows.append(a)
                p=post('/projects',{'name':'Stock export self-test','intent':intent,'asset_ids':[a.id for a in rows]})
                job('/projects/'+p['id']+'/generate',{'use_vision':False})
                for fmt in ('png','pdf'):
                    result=job('/projects/'+p['id']+'/export',{'format':fmt})
                    response=client.get(result['url']);response.raise_for_status()
                    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
                        manifest=json.loads(archive.read('license-manifest.json'))
                        checks[source+'_export_'+fmt]=len(manifest)==2 and bool(archive.read('moodboard.'+fmt)) and bool(archive.read('attribution.txt'))
        checks['unsplash_export_tracking']=len(calls)==6
        import keyring
        from app.ai.llm.credential_manager import SERVICE
        checks['separate_credential_service']=SERVICE=='AI Mood Board Studio Desktop'
        checks['os_keyring']=keyring.get_keyring().__class__.__module__.startswith('keyring.backends.macOS')
        import litellm
        checks['cloud_llm_runtime']=callable(litellm.acompletion)
        import torch
        import transformers
        checks['visual_runtime']=hasattr(torch,'inference_mode') and hasattr(transformers,'AutoProcessor')
        system=client.get('/api/system').json()
        checks['model_absent_by_default']=not system['model_available']
        if model_path:
            from app.ai.embeddings.siglip2 import provider
            from app.providers.mock import fixture_bytes
            from app.security.images import decode
            provider.select_directory(str(model_path))
            images=[decode(fixture_bytes(1))]
            text=provider.encode_texts(['a material study'])
            visual=provider.encode_images(images)
            images[0].close()
            checks['external_model_inference']=visual.shape==text.shape==(1,768)
            checks['external_model_device']=provider.device
        assert all(v for v in checks.values() if isinstance(v,bool)),checks
    return {'passed':True,'checks':checks,'desktop':DESKTOP,'data_dir':str(DATA),'resource_root':str(ROOT),'architecture':__import__('platform').machine(),'python':sys.version.split()[0]}


def main():
    multiprocessing.freeze_support()
    args=parse_args()
    os.environ['MOODBOARD_DESKTOP']='1'
    os.environ.setdefault('HF_HUB_DISABLE_TELEMETRY','1')
    os.environ.setdefault('LITELLM_LOCAL_MODEL_COST_MAP','True')
    os.environ.setdefault('DO_NOT_TRACK','1')
    if args.data_dir:os.environ['MOODBOARD_DATA_DIR']=str(args.data_dir.resolve())
    if not getattr(sys,'frozen',False):sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'apps/api'))
    from app.core.config import DATA
    log_path=DATA/'logs/desktop.log'
    log=log_path.open('a',buffering=1)
    if sys.stdout is None:sys.stdout=log
    if sys.stderr is None:sys.stderr=log
    logging.basicConfig(level=logging.INFO,filename=log_path,format='%(asctime)s %(levelname)s %(message)s')
    try:
        initialize_database()
        if args.self_test_report:
            result=self_test(args.self_test_report,args.check_model_dir)
            args.self_test_report.parent.mkdir(parents=True,exist_ok=True)
            args.self_test_report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
            return
        listener=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        listener.bind(('127.0.0.1',0));listener.listen(128)
        port=listener.getsockname()[1]
        url=f'http://127.0.0.1:{port}'
        os.environ['MOODBOARD_DESKTOP_ORIGIN']=url
        from app.main import app
        import uvicorn
        server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=port,log_config=None,access_log=False,loop='asyncio',http='h11',lifespan='on'))
        thread=threading.Thread(target=server.run,kwargs={'sockets':[listener]},daemon=True)
        thread.start()
        deadline=time.monotonic()+30
        while not server.started and thread.is_alive() and time.monotonic()<deadline:time.sleep(.05)
        if not server.started:raise RuntimeError('本地服务启动失败，请查看日志：'+str(log_path))
        (DATA/'desktop-runtime.json').write_text(json.dumps({'url':url,'pid':os.getpid(),'log_path':str(log_path)}))
        if args.no_window:
            thread.join();return
        import webview
        webview.settings['ALLOW_DOWNLOADS']=True
        webview.settings['ALLOW_FILE_URLS']=False
        webview.settings['OPEN_EXTERNAL_LINKS_IN_BROWSER']=True
        window=webview.create_window('AI Mood Board Studio',url,width=1320,height=880,min_size=(760,600),background_color='#ffffff')
        def choose_folder():
            result=window.create_file_dialog(webview.FileDialog.FOLDER,allow_multiple=False)
            return result[0] if result else None
        app.state.select_model_folder=choose_folder
        def shutdown():server.should_exit=True
        window.events.closed+=shutdown
        try:webview.start(gui='cocoa',debug=False,private_mode=True)
        finally:
            shutdown();thread.join(timeout=10);listener.close()
    except Exception as e:
        logging.exception('Desktop startup/self-test failed')
        if args.self_test_report:
            args.self_test_report.parent.mkdir(parents=True,exist_ok=True)
            args.self_test_report.write_text(json.dumps({'passed':False,'error':str(e),'log':str(log_path)},ensure_ascii=False,indent=2))
        raise

if __name__=='__main__':main()
