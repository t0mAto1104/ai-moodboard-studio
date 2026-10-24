import numpy as np
from PIL import Image
from app.pipeline.color_analysis import analyze
from app.pipeline.deduplication import duplicate
from app.pipeline.selection import select_mmr
from app.pipeline.ranking import score
from app.schemas.models import ImageAsset

def asset(id,**kw):return ImageAsset(id=id,provider='mock',provider_asset_id=id,**kw)
def test_color_delta_e():
    from skimage.color import deltaE_ciede2000
    assert abs(float(deltaE_ciede2000(np.array([50,2.6772,-79.7751]),np.array([50,0,-82.7485])))-2.0425)<.0001
    im=Image.new('RGB',(200,200),'red');assert analyze(im,['#ff0000'])['palette_score']>analyze(im,['#0000ff'])['palette_score']
def test_exact_and_near_duplicates():
    assert duplicate(asset('a',content_hash='abc'),asset('b',content_hash='abc'),{})
    assert duplicate(asset('a',perceptual_hash='ffffffffffffffff'),asset('b',perceptual_hash='fffffffffffffffe'),{})
    assert not duplicate(asset('a',perceptual_hash='ffffffffffffffff'),asset('b',perceptual_hash='0000000000000000'),{'a':np.ones(2),'b':np.ones(2)})
def test_mmr_diversity_and_stability():
    a=[asset('a',final_score=.9),asset('b',final_score=.89),asset('c',final_score=.8)]
    v={'a':np.array([1.,0]),'b':np.array([1.,0]),'c':np.array([0.,1])}
    assert [x.id for x in select_mmr(a,v,2,'diversity')]==['a','c']
    assert score(asset('z',semantic_score=1,palette_score=1,quality_score=1,composition_score=1))==1
