import argparse,json,hashlib
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('bundle',type=Path);parser.add_argument('--output',type=Path);args=parser.parse_args()
files=[p for p in args.bundle.rglob('*') if p.is_file() and not p.is_symlink()]
forbidden=[]
for p in files:
    name=p.name.lower()
    if name.endswith(('.safetensors','.gguf','.sqlite','.sqlite3','.sqlite-wal')) or name in ('.env','model-path.json','deployment_manifest.json','studio.sqlite') or name.startswith('pytorch_model'):
        forbidden.append(str(p.relative_to(args.bundle)))
report={'bundle':str(args.bundle),'files':len(files),'bytes':sum(p.stat().st_size for p in files),'contains_visual_model_weights':any(p.endswith(('.safetensors','.gguf')) for p in forbidden),'forbidden_files':forbidden,'passed':not forbidden}
if args.output:args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2));assert not forbidden,forbidden
