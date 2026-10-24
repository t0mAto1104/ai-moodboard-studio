import imagehash
from app.pipeline.ranking import PHASH_DISTANCE,VISUAL_DUPLICATE_THRESHOLD

def duplicate(a,b,vectors):
    if a.content_hash and a.content_hash==b.content_hash:return True
    if a.perceptual_hash and b.perceptual_hash:
        distance=imagehash.hex_to_hash(a.perceptual_hash)-imagehash.hex_to_hash(b.perceptual_hash)
        if distance<=PHASH_DISTANCE:return True
        if distance<=12 and a.id in vectors and b.id in vectors:
            return float(vectors[a.id]@vectors[b.id])>=VISUAL_DUPLICATE_THRESHOLD
    return False
