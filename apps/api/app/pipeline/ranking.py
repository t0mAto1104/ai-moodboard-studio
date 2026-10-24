WEIGHTS={'semantic':(.55,.25,.10,.10),'color':(.30,.50,.10,.10),'diversity':(.45,.25,.15,.15)}
PHASH_DISTANCE=4
VISUAL_DUPLICATE_THRESHOLD=.985
MMR_LAMBDA={'semantic':.8,'color':.75,'diversity':.5}
def score(a,preference='semantic'):
    return sum(w*getattr(a,k) for w,k in zip(WEIGHTS[preference],('semantic_score','palette_score','quality_score','composition_score')))
