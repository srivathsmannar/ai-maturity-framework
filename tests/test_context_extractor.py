import json
from pathlib import Path
from unittest.mock import patch
from ai_maturity.context_extractor import extract_project_context

SAMPLE_INPUT = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "I need a query that breaks down ABM CI Demand by PA"}},
    {"id": "in-002", "category": "prompts", "sub_dimension": "ticketing_planning",
     "data": {"prompt_text": "Implement the plan for T260669092 — PA-Level CI Demand Pipeline"}},
    {"id": "in-003", "category": "tool_usage", "sub_dimension": "cross_system_connectivity",
     "data": {"tool_name": "Skill", "input": {"skill": "google-docs"}}},
    {"id": "in-004", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "can you update the google doc with new findings?"}},
]

def test_extract_context_returns_string(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.context_extractor.call_claude_writer",
               return_value="Developer was building a CI demand attribution pipeline."):
        ctx = extract_project_context(f)
    assert isinstance(ctx, str)
    assert len(ctx) > 10

def test_extract_context_fallback_on_failure(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.context_extractor.call_claude_writer", return_value=None):
        ctx = extract_project_context(f)
    assert "session" in ctx.lower() or "project" in ctx.lower() or "context" in ctx.lower()

def test_extract_context_only_reads_prompts(tmp_path):
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    captured_prompt = {}
    def mock_writer(prompt, model="sonnet"):
        captured_prompt["text"] = prompt
        return "A context summary."
    with patch("ai_maturity.context_extractor.call_claude_writer", side_effect=mock_writer):
        extract_project_context(f)
    assert "ABM CI Demand" in captured_prompt["text"]
    assert "tool_name" not in captured_prompt["text"]

def test_extract_context_filters_noise(tmp_path):
    records = SAMPLE_INPUT + [
        {"id": "in-005", "category": "prompts", "sub_dimension": "ai_tool_adoption",
         "data": {"prompt_text": "<task-notification><task-id>x</task-id></task-notification>"}},
    ]
    f = tmp_path / "input.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in records))
    captured_prompt = {}
    def mock_writer(prompt, model="sonnet"):
        captured_prompt["text"] = prompt
        return "A context summary."
    with patch("ai_maturity.context_extractor.call_claude_writer", side_effect=mock_writer):
        extract_project_context(f)
    assert "<task-notification>" not in captured_prompt["text"]
