import json
from pathlib import Path
from unittest.mock import patch
from ai_maturity.grader import grade_session
from ai_maturity.taxonomy import SUB_DIMENSIONS, LEVELS

SAMPLE_INPUT = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "cicd_integration",
     "dimension": "integration", "team": "t", "user": "u", "session_id": "s1",
     "timestamp": "2026-04-25T10:00:00Z", "source": "claude_session_log",
     "data": {"prompt_text": "fix the CI pipeline"}, "metadata": {}},
    {"id": "in-002", "category": "tool_usage", "sub_dimension": "cicd_integration",
     "dimension": "integration", "team": "t", "user": "u", "session_id": "s1",
     "timestamp": "2026-04-25T10:00:05Z", "source": "claude_session_log",
     "data": {"tool_name": "Bash", "input": {"command": "buck2 test //foo"}}, "metadata": {}},
    {"id": "in-003", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "dimension": "capability", "team": "t", "user": "u", "session_id": "s1",
     "timestamp": "2026-04-25T10:00:10Z", "source": "claude_session_log",
     "data": {"prompt_text": "help me debug this"}, "metadata": {}},
]

FAKE_JUDGE_RESPONSE = {
    "level": 2, "confidence": "medium",
    "evidence": ["fix the CI pipeline", "buck2 test"],
    "matched_signals": ["CI commands"],
    "reasoning": "Developer references CI and runs test commands."
}

def test_grade_session_returns_12_results(tmp_path):
    input_file = tmp_path / "input.jsonl"
    input_file.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    gt_path = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE_RESPONSE):
        results = grade_session(input_file, gt_path)
    assert len(results) == 12

def test_grade_session_all_sub_dimensions_present(tmp_path):
    input_file = tmp_path / "input.jsonl"
    input_file.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    gt_path = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE_RESPONSE):
        results = grade_session(input_file, gt_path)
    result_sds = {r["sub_dimension"] for r in results}
    assert result_sds == set(SUB_DIMENSIONS)

def test_grade_session_output_schema(tmp_path):
    input_file = tmp_path / "input.jsonl"
    input_file.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    gt_path = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE_RESPONSE):
        results = grade_session(input_file, gt_path)
    for r in results:
        assert "id" in r
        assert "category" in r
        assert "input_id" in r
        assert "sub_dimension" in r
        assert "dimension" in r
        assert "level" in r
        assert "level_label" in r
        assert "confidence" in r
        assert "evidence" in r
        assert "reasoning" in r
        assert r["level"] in (1, 2, 3, 4)
        assert r["level_label"] in LEVELS.values()

def test_grade_session_empty_subdim_still_graded(tmp_path):
    input_file = tmp_path / "input.jsonl"
    input_file.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    gt_path = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE_RESPONSE):
        results = grade_session(input_file, gt_path)
    mkpi = [r for r in results if r["sub_dimension"] == "measurement_kpis"][0]
    assert mkpi["level"] in (1, 2, 3, 4)

def test_grade_session_handles_judge_failure(tmp_path):
    input_file = tmp_path / "input.jsonl"
    input_file.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    gt_path = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    with patch("ai_maturity.grader.call_claude_judge", return_value=None):
        results = grade_session(input_file, gt_path)
    assert len(results) == 12
    for r in results:
        assert r["level"] == 1
        assert r["confidence"] == "low"
