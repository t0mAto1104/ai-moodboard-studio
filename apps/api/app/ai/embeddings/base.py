from abc import ABC,abstractmethod
class EmbeddingProvider(ABC):
    model_id:str
    revision:str
    dimension:int
    @abstractmethod
    def encode_images(self,images):...
    @abstractmethod
    def encode_texts(self,texts):...
