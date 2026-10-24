import os,threading,json
import numpy as np
from app.core.config import model_directory,MODEL_ID,REVISION
from app.ai.embeddings.base import EmbeddingProvider
class SigLIP2EmbeddingProvider(EmbeddingProvider):
    model_id=MODEL_ID;revision=REVISION;dimension=768;preprocess='siglip224-slow-fp32-v1'
    def __init__(self):self.model=None;self.lock=threading.RLock();self.device='unloaded';self.error=None
    def load(self):
        if self.model is not None:return
        directory=model_directory()
        if not (directory/'model.safetensors').is_file():raise ValueError('外接视觉模型不可用，已采用元数据排序')
        manifest=directory/'deployment_manifest.json'
        if not manifest.exists() or json.loads(manifest.read_text()).get('revision')!=self.revision:raise ValueError('模型版本清单不匹配')
        root=directory.parent
        for k,p in {'HF_HOME':root/'huggingface','HF_HUB_CACHE':root/'huggingface/hub','HF_XET_CACHE':root/'huggingface/xet','TORCH_HOME':root/'torch'}.items():os.environ[k]=str(p)
        os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false')
        import torch
        from transformers import AutoModel,AutoProcessor
        self.torch=torch;self.device='cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu'
        self.processor=AutoProcessor.from_pretrained(str(directory),local_files_only=True,use_fast=False)
        self.model=AutoModel.from_pretrained(str(directory),local_files_only=True,dtype=torch.float32,attn_implementation='eager').eval().to(self.device)
    def select_directory(self,path):
        from app.core.config import save_model_directory
        with self.lock:
            directory=save_model_directory(path)
            self.model=None;self.processor=None;self.device='unloaded';self.error=None
            import gc
            gc.collect()
            if hasattr(self,'torch') and self.torch.backends.mps.is_available():self.torch.mps.empty_cache()
            return directory
    def encode_images(self,images):
        with self.lock:
            self.load()
            with self.torch.inference_mode():
                inputs=self.processor(images=images,return_tensors='pt').to(self.device)
                v=self.model.get_image_features(**inputs)
                return self.torch.nn.functional.normalize(v,dim=-1).cpu().numpy()
    def encode_texts(self,texts):
        with self.lock:
            self.load()
            with self.torch.inference_mode():
                inputs=self.processor(text=texts,padding='max_length',max_length=64,truncation=True,return_tensors='pt').to(self.device)
                v=self.model.get_text_features(**inputs)
                return self.torch.nn.functional.normalize(v,dim=-1).cpu().numpy()
provider=SigLIP2EmbeddingProvider()
