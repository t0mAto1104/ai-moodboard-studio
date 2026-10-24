import json
import pytest
from app.core import config
from app.ai.embeddings.siglip2 import SigLIP2EmbeddingProvider

def test_desktop_model_path_can_be_selected_without_copying_weights(tmp_path,monkeypatch):
    directory=tmp_path/'external-model';directory.mkdir()
    needed=('model.safetensors','config.json','preprocessor_config.json','tokenizer_config.json','tokenizer.json')
    files=[]
    for name in needed:
        (directory/name).write_bytes(b'test')
        files.append({'name':name,'bytes':4})
    (directory/'deployment_manifest.json').write_text(json.dumps({'repo':config.MODEL_ID,'revision':config.REVISION,'files':files}))
    monkeypatch.setattr(config,'MODEL_SETTINGS',tmp_path/'selected-model.json')
    before={p.name for p in directory.iterdir()}
    provider=SigLIP2EmbeddingProvider();assert provider.select_directory(directory)==directory
    assert config.model_directory()==directory and before=={p.name for p in directory.iterdir()}
    assert provider.device=='unloaded'


def test_invalid_model_folder_does_not_overwrite_selection(tmp_path,monkeypatch):
    settings=tmp_path/'model-path.json';settings.write_text(json.dumps({'path':'/existing/choice'}))
    monkeypatch.setattr(config,'MODEL_SETTINGS',settings)
    with pytest.raises(ValueError):config.save_model_directory(tmp_path/'missing')
    assert json.loads(settings.read_text())['path']=='/existing/choice'


def test_broken_settings_fall_back_to_environment(tmp_path,monkeypatch):
    settings=tmp_path/'model-path.json';settings.write_text('[]')
    monkeypatch.setattr(config,'MODEL_SETTINGS',settings);monkeypatch.setenv('SIGLIP_MODEL_DIR',str(tmp_path/'chosen'))
    assert config.model_directory()==tmp_path/'chosen'
