import json
from pathlib import Path
from ai_maturity.exemplars import load_exemplars, is_noise

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

def test_filters_xml_task_notifications(tmp_path):
    records = [
        {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "<task-notification><task-id>abc</task-id></task-notification>"}},
        {"id": "in-002", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "use the presto-query skill"}},
    ]
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in records))
    exemplars = load_exemplars(f, max_per_subdim=3)
    texts = [r["data"]["prompt_text"] for r in exemplars["ai_tool_adoption"]]
    assert "<task-notification>" not in str(texts)
    assert "presto-query" in str(texts)

def test_filters_interrupted_requests(tmp_path):
    records = [
        {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "[Request interrupted by user]"}},
        {"id": "in-002", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "help me debug this"}},
    ]
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in records))
    exemplars = load_exemplars(f, max_per_subdim=3)
    texts = [r["data"]["prompt_text"] for r in exemplars["ai_tool_adoption"]]
    assert "[Request interrupted" not in str(texts)

def test_filters_exit_commands(tmp_path):
    records = [
        {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "<command-name>/exit</command-name>"}},
        {"id": "in-002", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "run the tests"}},
    ]
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in records))
    exemplars = load_exemplars(f, max_per_subdim=3)
    assert len(exemplars["ai_tool_adoption"]) == 1
