import numpy as np
from app.pipeline.ranking import MMR_LAMBDA

def select_mmr(assets,vectors,count,preference='semantic'):
    remaining=sorted(assets,key=lambda a:(-a.final_score,a.id));selected=[];lam=MMR_LAMBDA[preference]
    while remaining and len(selected)<count:
        def utility(a):
            redundancy=max((max(0,float(vectors[a.id]@vectors[b.id])) for b in selected if a.id in vectors and b.id in vectors),default=0)
            source_penalty=.025*sum(b.provider==a.provider for b in selected)
            coverage=.04 if a.query_origin not in [b.query_origin for b in selected] else 0
            return lam*a.final_score-(1-lam)*redundancy-source_penalty+coverage
        best=max(remaining,key=utility);selected.append(best);remaining.remove(best)
    return selected
