from ai_maturity.narrative_prompts import build_dimension_prompt, build_executive_prompt

FAKE_DIM_DATA = {
    "dimension": "capability",
    "average": 2.3,
    "sub_dimensions": [
        {"sub_dimension": "ai_tool_adoption", "level": 2, "level_label": "Integrated",
         "confidence": "high", "reasoning": "Developer selects specific tools.",
         "evidence": ["uses presto-query skill"]},
        {"sub_dimension": "prompt_context_engineering", "level": 1, "level_label": "Assisted",
         "confidence": "medium", "reasoning": "Asks basic context questions.",
         "evidence": ["how do i add files as context?"]},
        {"sub_dimension": "agent_configuration", "level": 2, "level_label": "Integrated",
         "confidence": "high", "reasoning": "Hooks and skills configured.",
         "evidence": ["Skill: executing-plans"]},
    ],
}

FAKE_SCORES = {
    "overall_score": 1.5,
    "maturity_label": "L2: Integrated",
    "dimensions": {
        "capability": {"average": 2.3},
        "integration": {"average": 1.0},
        "governance": {"average": 1.0},
        "execution_ownership": {"average": 1.0},
    },
}

def test_dimension_prompt_contains_scores():
    prompt = build_dimension_prompt(FAKE_DIM_DATA)
    assert "ai_tool_adoption" in prompt
    assert "L2" in prompt or "Integrated" in prompt

def test_dimension_prompt_contains_evidence():
    prompt = build_dimension_prompt(FAKE_DIM_DATA)
    assert "presto-query" in prompt

def test_dimension_prompt_asks_for_narrative():
    prompt = build_dimension_prompt(FAKE_DIM_DATA)
    assert "narrative" in prompt.lower() or "write" in prompt.lower()

def test_executive_prompt_contains_overall():
    prompt = build_executive_prompt(FAKE_SCORES, user="alice", team="platform")
    assert "1.5" in prompt or "L2" in prompt
    assert "alice" in prompt

def test_executive_prompt_contains_dimensions():
    prompt = build_executive_prompt(FAKE_SCORES, user="alice", team="platform")
    assert "capability" in prompt.lower()
    assert "integration" in prompt.lower()
