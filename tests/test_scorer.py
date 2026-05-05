from ai_maturity.scorer import compute_scores
from ai_maturity.taxonomy import SUB_DIMENSIONS

def _make_results(level=2):
    return [{"sub_dimension": sd, "dimension": None, "level": level} for sd in SUB_DIMENSIONS]

def test_overall_score():
    results = _make_results(level=3)
    scores = compute_scores(results)
    assert scores["overall_score"] == 3.0

def test_overall_label_l1():
    scores = compute_scores(_make_results(level=1))
    assert scores["maturity_label"] == "L1: Assisted"

def test_overall_label_l2():
    scores = compute_scores(_make_results(level=2))
    assert scores["maturity_label"] == "L2: Integrated"

def test_overall_label_l3():
    scores = compute_scores(_make_results(level=3))
    assert scores["maturity_label"] == "L3: Agentic"

def test_overall_label_l4():
    scores = compute_scores(_make_results(level=4))
    assert scores["maturity_label"] == "L4: Autonomous"

def test_dimension_scores():
    results = _make_results(level=2)
    scores = compute_scores(results)
    assert "capability" in scores["dimensions"]
    assert "integration" in scores["dimensions"]
    assert "governance" in scores["dimensions"]
    assert "execution_ownership" in scores["dimensions"]
    for dim_score in scores["dimensions"].values():
        assert dim_score["average"] == 2.0
        assert len(dim_score["sub_dimensions"]) == 3

def test_mixed_levels():
    results = _make_results(level=1)
    for r in results:
        if r["sub_dimension"] in ("ai_tool_adoption", "prompt_context_engineering", "agent_configuration"):
            r["level"] = 3
    scores = compute_scores(results)
    assert scores["dimensions"]["capability"]["average"] == 3.0
    assert scores["dimensions"]["integration"]["average"] == 1.0
    assert scores["overall_score"] == 1.5
