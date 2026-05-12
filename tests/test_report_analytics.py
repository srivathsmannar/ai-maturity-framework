from pathlib import Path
from unittest.mock import patch
import json

_ALL_SDS = [
    ("ai_tool_adoption", "capability"), ("prompt_context_engineering", "capability"),
    ("agent_configuration", "capability"), ("cicd_integration", "integration"),
    ("ticketing_planning", "integration"), ("cross_system_connectivity", "integration"),
    ("quality_controls", "governance"), ("security_compliance", "governance"),
    ("measurement_kpis", "governance"), ("ways_of_working", "execution_ownership"),
    ("accountability_ownership", "execution_ownership"),
    ("scalability_knowledge_transfer", "execution_ownership"),
]

SCORED = [
    {"sub_dimension": sd, "dimension": dim, "level": 2, "level_label": "Integrated",
     "confidence": "medium", "reasoning": "ok", "evidence": [], "matched_signals": [],
     "record_count": 3, "id": f"out-{sd}", "category": "prompts", "input_id": sd,
     "team": "eng", "user": "alice", "assessed_at": "2026-05-01T00:00:00Z"}
    for sd, dim in _ALL_SDS
]

METRICS = {
    "session_count": 5, "total_messages": 20, "tool_call_count": 3,
    "agent_spawn_count": 1, "skill_invocation_count": 2,
    "records_by_category": {"prompts": 20}, "records_by_sub_dimension": {"ai_tool_adoption": 20},
    "hour_distribution": {9: 10}, "day_of_week_distribution": {0: 20},
    "session_duration_minutes": {"mean": 15.0, "median": 12.0, "p25": 8.0, "p75": 20.0},
    "messages_per_session": {"mean": 4.0, "median": 4.0, "p25": 2.0, "p75": 6.0},
}

def _write_scored(path):
    path.write_text("\n".join(json.dumps(r) for r in SCORED) + "\n")

def _write_input(path):
    path.write_text(json.dumps({"sub_dimension": "ai_tool_adoption",
        "record_type": "prompt", "data": {"prompt_text": "help"}}) + "\n")

def test_report_includes_analytics_section(tmp_path):
    scored_path = tmp_path / "scored.jsonl"
    input_path = tmp_path / "input.jsonl"
    _write_scored(scored_path)
    _write_input(input_path)

    from ai_maturity.report import generate_report
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative."), \
         patch("ai_maturity.report.extract_project_context", return_value="Context."):
        md = generate_report(scored_path, input_path, metrics=METRICS)

    assert "## Usage Analytics" in md
    assert "Narrative." in md

def test_report_without_metrics_skips_analytics(tmp_path):
    scored_path = tmp_path / "scored.jsonl"
    input_path = tmp_path / "input.jsonl"
    _write_scored(scored_path)
    _write_input(input_path)

    from ai_maturity.report import generate_report
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative."), \
         patch("ai_maturity.report.extract_project_context", return_value="Context."):
        md = generate_report(scored_path, input_path, metrics=None)

    assert "## Usage Analytics" not in md
