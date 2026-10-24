import hashlib,importlib.util,json
from pathlib import Path
import pytest

@pytest.fixture
def helper(monkeypatch):
    path=Path(__file__).parents[1]/'install_vision_model.py'
    spec=importlib.util.spec_from_file_location('model_installer',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    files={'config.json':b'{}','model.safetensors':b'test-fixture-only'}
    pinned={'repo':'test/model','revision':'test-revision','files':[{'name':k,'bytes':len(v),'sha256':hashlib.sha256(v).hexdigest()} for k,v in files.items()]}
    monkeypatch.setattr(m,'PINNED',pinned)
    def download(directory):
        for name,value in files.items():(directory/name).write_bytes(value)
    monkeypatch.setattr(m,'download',download)
    return m,files

def test_install_creates_compatible_manifest_and_verify_is_read_only(helper,tmp_path):
    m,_=helper;target=tmp_path/'model'
    assert m.install(target)['verified']
    manifest=target/'deployment_manifest.json';before=manifest.stat().st_mtime_ns
    assert json.loads(manifest.read_text())==m.PINNED
    assert m.install(target,verify_only=True)['verified'] and manifest.stat().st_mtime_ns==before
    assert not (target/'.moodboard-installing.json').exists()

def test_unrelated_existing_files_are_never_overwritten(helper,tmp_path):
    m,_=helper;(tmp_path/'personal.txt').write_text('keep')
    with pytest.raises(ValueError,match='不会覆盖'):m.install(tmp_path)
    assert (tmp_path/'personal.txt').read_text()=='keep'

def test_bad_hash_is_rejected_without_manifest(helper,tmp_path):
    m,files=helper
    for name,value in files.items():(tmp_path/name).write_bytes(value)
    (tmp_path/'config.json').write_bytes(b'xx')
    with pytest.raises(ValueError,match='SHA256'):m.install(tmp_path)
    assert not (tmp_path/'deployment_manifest.json').exists()

def test_only_owned_partial_downloads_can_resume(helper,tmp_path):
    m,_=helper;(tmp_path/'.moodboard-installing.json').write_text(json.dumps({'revision':m.PINNED['revision']}))
    (tmp_path/'partial').write_bytes(b'partial')
    assert m.install(tmp_path)['verified']

def test_download_uses_explicit_disk_cache_and_pinned_revision(helper,tmp_path,monkeypatch):
    import sys,types,os
    m,_=helper;calls=[]
    # Reload the real download function while retaining fixture metadata.
    spec=importlib.util.spec_from_file_location('real_installer',Path(__file__).parents[1]/'install_vision_model.py')
    real=importlib.util.module_from_spec(spec);spec.loader.exec_module(real)
    monkeypatch.setattr(real,'PINNED',m.PINNED)
    monkeypatch.setitem(sys.modules,'huggingface_hub',types.SimpleNamespace(snapshot_download=lambda **kw:calls.append(kw)))
    for key in ('HF_HOME','HF_HUB_CACHE','HF_XET_CACHE','HF_HUB_DISABLE_TELEMETRY','HF_HUB_OFFLINE'):
        monkeypatch.setenv(key,'old-value')
    target=tmp_path/'model';real.download(target)
    assert calls[0]['revision']==m.PINNED['revision'] and calls[0]['token'] is False
    assert calls[0]['local_dir']==str(target) and calls[0]['cache_dir']==str(tmp_path/'huggingface/hub')
    assert os.environ['HF_XET_CACHE']==str(tmp_path/'huggingface/xet')
