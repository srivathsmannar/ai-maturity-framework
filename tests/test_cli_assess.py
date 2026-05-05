import json
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
from ai_maturity.cli import cli

SAMPLE_INPUT_RECORD = {
    "id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
    "dimension": "capability", "team": "platform", "user": "alice",
    "session_id": "s1", "timestamp": "2026-04-25T10:00:00Z",
    "source": "claude_session_log", "data": {"prompt_text": "help me debug"},
    "metadata": {}
}

FAKE_JUDGE = {
    "level": 2, "confidence": "medium",
    "evidence": ["debug request"], "matched_signals": ["ad-hoc"],
    "reasoning": "Basic usage."
}

def test_assess_produces_output(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "platform_alice_2026-04-25.jsonl").write_text(
        json.dumps(SAMPLE_INPUT_RECORD) + "\n"
    )
    output_dir = tmp_path / "output"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "assess",
            "--input-dir", str(input_dir),
            "--output-dir", str(output_dir),
        ])
    assert result.exit_code == 0, result.output
    output_files = list(output_dir.glob("*.jsonl"))
    assert len(output_files) >= 1

def test_assess_output_has_12_scores(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "platform_alice_2026-04-25.jsonl").write_text(
        json.dumps(SAMPLE_INPUT_RECORD) + "\n"
    )
    output_dir = tmp_path / "output"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        runner = CliRunner()
        runner.invoke(cli, [
            "assess",
            "--input-dir", str(input_dir),
            "--output-dir", str(output_dir),
        ])
    output_file = list(output_dir.glob("*.jsonl"))[0]
    records = [json.loads(l) for l in output_file.read_text().strip().split("\n")]
    assert len(records) == 12

def test_assess_prints_summary(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "platform_alice_2026-04-25.jsonl").write_text(
        json.dumps(SAMPLE_INPUT_RECORD) + "\n"
    )
    output_dir = tmp_path / "output"
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "assess",
            "--input-dir", str(input_dir),
            "--output-dir", str(output_dir),
        ])
    assert "Overall" in result.output or "overall" in result.output

def test_assess_merges_multiple_inputs(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    record1 = {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
        "dimension": "capability", "team": "t", "user": "u", "session_id": "s1",
        "timestamp": "2026-04-25T10:00:00Z", "source": "claude_session_log",
        "data": {"prompt_text": "help me"}, "metadata": {}}
    record2 = {"id": "in-002", "category": "prompts", "sub_dimension": "cicd_integration",
        "dimension": "integration", "team": "t", "user": "u", "session_id": "s2",
        "timestamp": "2026-04-26T10:00:00Z", "source": "claude_session_log",
        "data": {"prompt_text": "fix CI"}, "metadata": {}}
    (input_dir / "t_u_2026-04-25_session1.jsonl").write_text(json.dumps(record1) + "\n")
    (input_dir / "t_u_2026-04-26_session2.jsonl").write_text(json.dumps(record2) + "\n")
    output_dir = tmp_path / "output"

    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        runner = CliRunner()
        result = runner.invoke(cli, [
            "assess",
            "--input-dir", str(input_dir),
            "--output-dir", str(output_dir),
        ])
    assert result.exit_code == 0, result.output
    output_files = list(output_dir.glob("*_scored.jsonl"))
    assert len(output_files) == 1

    # Verify merged file was persisted
    merged_files = list(input_dir.glob("*_merged.jsonl"))
    assert len(merged_files) == 1
