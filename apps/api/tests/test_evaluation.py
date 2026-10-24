import pytest
from app.pipeline.evaluation import metrics

def test_perfect_ranking():
    result=metrics(['a','b','c'],{'a':3,'b':2,'c':0},3)
    assert result['ndcg_at_k']==1
    assert result['precision_at_k']==pytest.approx(2/3)
    assert result['duplicate_ratio']==0

def test_reversed_ranking_is_worse():
    assert metrics(['c','b','a'],{'a':3,'b':2,'c':0},3)['ndcg_at_k']<1

def test_missing_labels_never_count_as_negative():
    with pytest.raises(ValueError,match='Unjudged'):metrics(['a'],{},1)

def test_duplicate_cannot_inflate_gain():
    result=metrics(['a','a'],{'a':3,'b':2},2)
    assert result['ndcg_at_k']<1 and result['duplicate_ratio']==.5
