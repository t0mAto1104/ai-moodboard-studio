"""Metrics for fully judged rankings; never silently treat missing labels as irrelevant."""
import math

def metrics(ranking, judgments, k=10):
    if k < 1 or len(ranking) < k:
        raise ValueError('Need at least k ranked results')
    if any(id not in judgments for id in ranking[:k]):
        raise ValueError('Unjudged results cannot be scored')
    if any(type(grade) is not int or not 0 <= grade <= 3 for grade in judgments.values()):
        raise ValueError('Relevance grades must be integers 0–3')
    seen=set();grades=[]
    for id in ranking[:k]:
        grades.append(0 if id in seen else judgments[id])
        seen.add(id)
    def dcg(values):
        return sum((2**grade-1)/math.log2(i+2) for i,grade in enumerate(values))
    ideal=dcg(sorted(judgments.values(),reverse=True)[:k])
    return {'precision_at_k':sum(g>=2 for g in grades)/k,
            'ndcg_at_k':dcg(grades)/ideal if ideal else 0.0,
            'duplicate_ratio':1-len(set(ranking[:k]))/k,'k':k}
