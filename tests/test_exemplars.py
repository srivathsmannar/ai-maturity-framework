import json
from pathlib import Path
from ai_maturity.exemplars import load_exemplars

SAMPLE_INPUT = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "use the presto-query skill"}},
    {"id": "in-002", "category": "tool_usage", "sub_dimension": "ai_tool_adoption",
     "data": {"tool_name": "Skill", "input": {"skill": "google-docs"}}},
    {"id": "in-003", "category": "tool_usage", "sub_dimension": "ai_tool_adoption",
     "data": {"tool_name": "Bash", "input": {"command": "ls -la"}}},
    {"id": "in-004", "category": "tool_usage", "sub_dimension": "ai_tool_adoption",
     "data": {"tool_name": "Read", "input": {"file_path": "/tmp/x"}}},
    {"id": "in-005", "category": "prompts", "sub_dimension": "cicd_integration",
     "data": {"prompt_text": "fix the CI pipeline"}},
]

def test_load_exemplars_groups_by_subdim(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    exemplars = load_exemplars(f, max_per_subdim=3)
    assert "ai_tool_adoption" in exemplars
    assert "cicd_integration" in exemplars

def test_load_exemplars_limits_count(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    exemplars = load_exemplars(f, max_per_subdim=2)
    assert len(exemplars["ai_tool_adoption"]) == 2

def test_load_exemplars_prefers_prompts(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    exemplars = load_exemplars(f, max_per_subdim=2)
    categories = [r["category"] for r in exemplars["ai_tool_adoption"]]
    assert categories[0] == "prompts"

def test_load_exemplars_empty_file(tmp_path):
    f = tmp_path / "empty.jsonl"
    f.write_text("")
    exemplars = load_exemplars(f, max_per_subdim=3)
    assert exemplars == {}
