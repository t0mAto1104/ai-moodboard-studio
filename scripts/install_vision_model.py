"""Explicit, pinned SigLIP deployment. Does not import Torch or execute model code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

PINNED=json.loads(Path(__file__).with_name('siglip2-files.json').read_text())

def verify(directory):
    for entry in PINNED['files']:
        file=directory/entry['name']
        if not file.is_file() or file.stat().st_size!=entry['bytes']:
            raise ValueError('文件缺失或大小不符：'+entry['name'])
        digest=hashlib.sha256()
        with file.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024),b''):digest.update(chunk)
        if digest.hexdigest()!=entry['sha256']:raise ValueError('SHA256 不符：'+entry['name'])
    manifest=directory/'deployment_manifest.json'
    if manifest.exists() and json.loads(manifest.read_text())!=PINNED:
        raise ValueError('现有部署清单不匹配；不会覆盖')
    return {'verified':True,'repo':PINNED['repo'],'revision':PINNED['revision'],
            'files':len(PINNED['files']),'bytes':sum(e['bytes'] for e in PINNED['files'])}

def download(directory):
    # Set paths BEFORE importing the Hub client; no weights in default user cache.
    cache=directory.parent/'huggingface'
    os.environ.update(HF_HOME=str(cache),HF_HUB_CACHE=str(cache/'hub'),
                      HF_XET_CACHE=str(cache/'xet'),HF_HUB_DISABLE_TELEMETRY='1')
    os.environ.pop('HF_HUB_OFFLINE',None)
    from huggingface_hub import snapshot_download
    snapshot_download(repo_id=PINNED['repo'],revision=PINNED['revision'],
                      local_dir=str(directory),cache_dir=str(cache/'hub'),
                      allow_patterns=[e['name'] for e in PINNED['files']],
                      token=False,max_workers=1)

def install(directory,verify_only=False):
    directory=Path(directory).expanduser().resolve()
    if verify_only:
        if not (directory/'deployment_manifest.json').is_file():raise ValueError('缺少部署清单')
        return verify(directory)
    if sys.platform=='darwin' and directory.parts[:2]==('/','Volumes'):
        volume=Path(*directory.parts[:3])
        if not os.path.ismount(volume):raise ValueError('目标外接磁盘未挂载；下载已停止')
    marker=directory/'.moodboard-installing.json'
    complete=all((directory/e['name']).is_file() for e in PINNED['files'])
    if not complete:
        if directory.exists() and any(directory.iterdir()):
            if not marker.is_file() or json.loads(marker.read_text())!={'revision':PINNED['revision']}:
                raise ValueError('目标不是空目录或本工具创建的未完成下载；不会覆盖，请选择新的空目录')
        directory.mkdir(parents=True,exist_ok=True)
        if not marker.exists():
            with marker.open('x') as stream:json.dump({'revision':PINNED['revision']},stream)
        required=sum(e['bytes'] for e in PINNED['files'])+64*1024*1024
        if shutil.disk_usage(directory).free<required:raise ValueError('可用空间不足，建议目标磁盘预留至少 3 GB')
        download(directory)
    result=verify(directory)
    manifest=directory/'deployment_manifest.json'
    if not manifest.exists():
        with manifest.open('x') as stream:json.dump(PINNED,stream,indent=2)
    if marker.is_file() and json.loads(marker.read_text())=={'revision':PINNED['revision']}:marker.unlink()
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Download and verify the supported fixed SigLIP 2 revision')
    parser.add_argument('--directory',type=Path,required=True,help='Explicit destination on your chosen disk')
    parser.add_argument('--verify-only',action='store_true',help='Read-only local SHA256 verification; no network')
    args=parser.parse_args()
    try:print(json.dumps(install(args.directory,args.verify_only),ensure_ascii=False,indent=2))
    except Exception as error:parser.exit(1,'部署失败：'+str(error)+'\n')
