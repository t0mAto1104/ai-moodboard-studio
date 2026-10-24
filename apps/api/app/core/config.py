import json
import os
import sys
from pathlib import Path

DESKTOP=bool(getattr(sys,'frozen',False) or os.environ.get('MOODBOARD_DESKTOP')=='1')
ROOT=Path(getattr(sys,'_MEIPASS','.'))/'studio' if getattr(sys,'frozen',False) else Path(__file__).resolve().parents[4]
def application_data_dir():
    if sys.platform=='darwin':return Path.home()/'Library/Application Support/AI Mood Board Studio'
    if sys.platform=='win32':return Path(os.environ.get('LOCALAPPDATA',Path.home()))/'AI Mood Board Studio'
    return Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local/share'))/'ai-moodboard-studio'
DATA=Path(os.environ.get('MOODBOARD_DATA_DIR',str(application_data_dir() if DESKTOP else ROOT/'.local'))).expanduser().resolve()
DATA.mkdir(parents=True,exist_ok=True)
for folder in ('cache','exports','logs'):(DATA/folder).mkdir(exist_ok=True)
MODEL_ID='google/siglip2-base-patch16-224'
REVISION='75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2'
MODEL_SETTINGS=DATA/'model-path.json'

def model_directory():
    try:
        saved=json.loads(MODEL_SETTINGS.read_text())
        if isinstance(saved,dict) and isinstance(saved.get('path'),str) and saved['path']:return Path(saved['path']).expanduser().resolve()
    except (OSError,ValueError,TypeError):pass
    default=DATA/'models/siglip2-base-patch16-224' if DESKTOP else Path('/Volumes/KINGSTON/AI_Models/siglip2-base-patch16-224')
    return Path(os.environ.get('SIGLIP_MODEL_DIR',str(default))).expanduser().resolve()

# Kept for existing scripts; runtime model selection uses model_directory().
MODEL_DIR=model_directory()

def validate_model_directory(path):
    directory=Path(path).expanduser().resolve()
    needed=('model.safetensors','config.json','preprocessor_config.json','tokenizer_config.json','tokenizer.json','deployment_manifest.json')
    if not directory.is_dir() or any(not (directory/name).is_file() for name in needed):
        raise ValueError('请选择完整的 SigLIP 2 模型目录，需包含权重、配置、Tokenizer 和版本清单')
    manifest=json.loads((directory/'deployment_manifest.json').read_text())
    if not isinstance(manifest,dict) or manifest.get('repo')!=MODEL_ID or manifest.get('revision')!=REVISION:raise ValueError('模型 ID 或版本与此应用不匹配')
    if not isinstance(manifest.get('files'),list):raise ValueError('模型版本清单无效')
    expected={f['name']:f for f in manifest.get('files',[]) if isinstance(f,dict) and 'name' in f}
    for name in needed[:-1]:
        if name not in expected or (directory/name).stat().st_size!=expected[name].get('bytes'):raise ValueError('模型文件缺失或大小校验失败：'+name)
    return directory

def save_model_directory(path):
    directory=validate_model_directory(path)
    temporary=MODEL_SETTINGS.with_suffix('.tmp')
    temporary.write_text(json.dumps({'path':str(directory),'model_id':MODEL_ID,'revision':REVISION},ensure_ascii=False))
    temporary.replace(MODEL_SETTINGS)
    return directory
