from ai_maturity.prompt_builder import build_grading_prompt

FAKE_GT = "### AI Tool Adoption\nL1: Ad-hoc\nL2: Standardized\nL3: Right tool\nL4: Autonomous"

FAKE_RECORDS = [
    {"id": "in-001", "category": "prompts", "data": {"prompt_text": "help me debug this"}},
    {"id": "in-002", "category": "tool_usage", "data": {"tool_name": "Bash", "input": {"command": "ls"}}},
]

def test_prompt_contains_ground_truth():
    prompt = build_grading_prompt("ai_tool_adoption", FAKE_GT, FAKE_RECORDS)
    assert "Ad-hoc" in prompt
    assert "Standardized" in prompt

def test_prompt_contains_evidence():
    prompt = build_grading_prompt("ai_tool_adoption", FAKE_GT, FAKE_RECORDS)
    assert "help me debug this" in prompt
    assert "Bash" in prompt

def test_prompt_contains_sub_dimension_name():
    prompt = build_grading_prompt("ai_tool_adoption", FAKE_GT, FAKE_RECORDS)
    assert "ai_tool_adoption" in prompt

def test_prompt_asks_for_level():
    prompt = build_grading_prompt("ai_tool_adoption", FAKE_GT, FAKE_RECORDS)
    assert "level" in prompt.lower()

def test_prompt_empty_records():
    prompt = build_grading_prompt("measurement_kpis", FAKE_GT, [])
    assert "no records" in prompt.lower()

def test_prompt_truncates_large_evidence():
    big_records = [{"id": f"in-{i:03d}", "category": "prompts",
                    "data": {"prompt_text": f"prompt number {i} " * 100}}
                   for i in range(100)]
    prompt = build_grading_prompt("ai_tool_adoption", FAKE_GT, big_records)
    assert len(prompt) < 50000
