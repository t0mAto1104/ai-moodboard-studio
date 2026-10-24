# Build with the project's venv. Data sources are explicit: no .local, keys or models.
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
root=Path(SPECPATH).parent
assets=[(str(root/'apps/web/dist'),'studio/apps/web/dist'),(str(root/'apps/api/migrations'),'studio/apps/api/migrations'),(str(root/'desktop/THIRD_PARTY_NOTICES.txt'),'studio/THIRD_PARTY_NOTICES.txt')]
for package in ('litellm','transformers','reportlab','webview'):
    assets += collect_data_files(package,excludes=['**/tests/**','**/test/**','**/__pycache__/**','**/proxy/**'])
for package in ('torch','transformers','tokenizers','huggingface-hub','safetensors','sentencepiece','litellm','keyring','pywebview','pydantic','numpy','scikit-image','httpx','fastapi','uvicorn','sqlalchemy','alembic','reportlab','tiktoken','packaging','regex','requests','PyYAML','filelock','tqdm'):
    try:assets+=copy_metadata(package)
    except Exception:pass
hidden=['uvicorn.logging','uvicorn.protocols.http.h11_impl','uvicorn.lifespan.on','uvicorn.loops.asyncio','sqlalchemy.dialects.sqlite','keyring.backends.macOS','webview.platforms.cocoa','transformers.models.siglip.modeling_siglip','transformers.models.siglip.processing_siglip','transformers.models.siglip.image_processing_siglip','transformers.models.siglip.tokenization_siglip','transformers.models.gemma.tokenization_gemma_fast','PIL._imagingft']
hidden+=collect_submodules('alembic',filter=lambda name:'.testing' not in name and '.tests' not in name)
hidden+=collect_submodules('scipy.special')
excludes=['tkinter','IPython','jupyter','notebook','pytest','matplotlib','pandas','bokeh','plotly','PyQt5','PyQt6','PySide2','PySide6','webview.platforms.qt','webview.platforms.gtk','webview.platforms.winforms','webview.platforms.cef','tensorflow','tensorflow_probability','jax','jaxlib','flax','tensorboard','triton','torchvision','torchaudio','onnx','onnxruntime','cv2','datasets','accelerate','timm','sklearn']
a=Analysis([str(root/'desktop/launcher.py')],pathex=[str(root/'apps/api')],binaries=[],datas=assets,hiddenimports=hidden,hookspath=[str(root/'desktop/hooks')],excludes=excludes,noarchive=False)
pyz=PYZ(a.pure)
exe=EXE(pyz,a.scripts,[],exclude_binaries=True,name='AI Mood Board Studio',debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False,target_arch='arm64',codesign_identity=None,entitlements_file=None)
coll=COLLECT(exe,a.binaries,a.datas,strip=False,upx=False,name='AI Mood Board Studio')
app=BUNDLE(coll,name='AI Mood Board Studio.app',icon=str(root/'desktop/AppIcon.icns'),bundle_identifier='local.moodboard.studio',version='0.2.0',info_plist={'CFBundleDisplayName':'AI Mood Board Studio','CFBundleShortVersionString':'0.2.0','LSMinimumSystemVersion':'14.0','NSHighResolutionCapable':True,'NSAppTransportSecurity':{'NSAllowsLocalNetworking':True},'NSHumanReadableCopyright':'AI Mood Board Studio; includes third-party open-source components.'})
