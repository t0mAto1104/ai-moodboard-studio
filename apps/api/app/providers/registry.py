from app.providers.artic import ArticProvider
from app.providers.metmuseum import MetProvider
from app.providers.openverse import OpenverseProvider
from app.providers.mock import MockProvider
from app.providers.pixabay import PixabayProvider
from app.providers.unsplash import UnsplashProvider
PROVIDERS={p.name:p for p in [ArticProvider(),MetProvider(),OpenverseProvider(),MockProvider(),PixabayProvider(),UnsplashProvider()]}
