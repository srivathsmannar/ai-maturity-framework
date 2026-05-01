from ai_maturity.narrative_prompts import build_dimension_prompt, build_executive_prompt

PROJECT_CONTEXT = "The developer was building a CI demand attribution pipeline using SQL queries and Google Docs."

FAKE_DIM_DATA = {
    "dimension": "capability",
    "average": 2.3,
    "sub_dimensions": [
        {"sub_dimension": "ai_tool_adoption", "level": 2, "level_label": "Integrated",
         "confidence": "high", "reasoning": "Developer selects specific tools.",
         "evidence": ["uses sql-query skill"]},
        {"sub_dimension": "prompt_context_engineering", "level": 1, "level_label": "Assisted",
         "confidence": "medium", "reasoning": "Asks basic context questions.",
         "evidence": ["how do i add files as context?"]},
        {"sub_dimension": "agent_configuration", "level": 2, "level_label": "Integrated",
         "confidence": "high", "reasoning": "Hooks and skills configured.",
         "evidence": ["Skill: executing-plans"]},
    ],
}

FAKE_EXEMPLARS = [
    "use the sql-query skill for this",
    "can you update the google doc?",
    "run the query in the notebook",
]

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

def test_dimension_prompt_contains_project_context():
    prompt = build_dimension_prompt(FAKE_DIM_DATA, PROJECT_CONTEXT, FAKE_EXEMPLARS)
    assert "CI demand" in prompt

def test_dimension_prompt_contains_exemplars():
    prompt = build_dimension_prompt(FAKE_DIM_DATA, PROJECT_CONTEXT, FAKE_EXEMPLARS)
    assert "sql-query" in prompt
    assert "google doc" in prompt

def test_dimension_prompt_asks_contextual_questions():
    prompt = build_dimension_prompt(FAKE_DIM_DATA, PROJECT_CONTEXT, FAKE_EXEMPLARS)
    assert "quote" in prompt.lower() or "weave" in prompt.lower() or "cite" in prompt.lower()

def test_dimension_prompt_works_without_context():
    prompt = build_dimension_prompt(FAKE_DIM_DATA)
    assert "capability" in prompt.lower()
    assert "ai_tool_adoption" in prompt

def test_executive_prompt_contains_project_context():
    prompt = build_executive_prompt(FAKE_SCORES, "alice", "platform", PROJECT_CONTEXT)
    assert "CI demand" in prompt

def test_executive_prompt_works_without_context():
    prompt = build_executive_prompt(FAKE_SCORES, "alice", "platform")
    assert "alice" in prompt
    assert "1.5" in prompt
