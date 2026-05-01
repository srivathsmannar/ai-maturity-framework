import json
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
from ai_maturity.cli import cli
from ai_maturity.taxonomy import SUB_DIMENSIONS, dimension_for

def _make_scored_and_input(tmp_path):
    scored_dir = tmp_path / "scored"
    scored_dir.mkdir()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    scored = []
    for sd in SUB_DIMENSIONS:
        scored.append({"sub_dimension": sd, "dimension": dimension_for(sd), "level": 2,
            "level_label": "Integrated", "confidence": "high", "record_count": 3,
            "reasoning": "Good usage.", "evidence": ["example"], "matched_signals": ["signal"],
            "team": "platform", "user": "alice", "id": f"out-{sd}",
            "category": "prompts", "input_id": "in-001", "assessed_at": "2026-04-28T10:00:00Z"})

    (scored_dir / "platform_alice_scored.jsonl").write_text(
        "\n".join(json.dumps(r) for r in scored))

    inp = [{"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
            "data": {"prompt_text": "use the sql-query skill"}}]
    (input_dir / "platform_alice_input.jsonl").write_text(
        "\n".join(json.dumps(r) for r in inp))

    return scored_dir, input_dir

def test_report_creates_md_file(tmp_path):
    scored_dir, input_dir = _make_scored_and_input(tmp_path)
    output_dir = tmp_path / "reports"
    with patch("ai_maturity.report.call_claude_writer", return_value="Solid narrative. Improve context."):
        with patch("ai_maturity.report.extract_project_context", return_value="Developer built a pipeline."):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "report",
                "--scored-dir", str(scored_dir),
                "--input-dir", str(input_dir),
                "--output-dir", str(output_dir),
            ])
    assert result.exit_code == 0, result.output
    md_files = list(output_dir.glob("*.md"))
    assert len(md_files) >= 1

def test_report_md_content(tmp_path):
    scored_dir, input_dir = _make_scored_and_input(tmp_path)
    output_dir = tmp_path / "reports"
    with patch("ai_maturity.report.call_claude_writer", return_value="Solid narrative. Improve context."):
        with patch("ai_maturity.report.extract_project_context", return_value="Developer built a pipeline."):
            runner = CliRunner()
            runner.invoke(cli, [
                "report",
                "--scored-dir", str(scored_dir),
                "--input-dir", str(input_dir),
                "--output-dir", str(output_dir),
            ])
    md_file = list(output_dir.glob("*.md"))[0]
    content = md_file.read_text()
    assert "AI Maturity Assessment" in content
    assert "Overall Maturity" in content

def test_report_prints_path(tmp_path):
    scored_dir, input_dir = _make_scored_and_input(tmp_path)
    output_dir = tmp_path / "reports"
    with patch("ai_maturity.report.call_claude_writer", return_value="Solid narrative. Improve context."):
        with patch("ai_maturity.report.extract_project_context", return_value="Developer built a pipeline."):
            runner = CliRunner()
            result = runner.invoke(cli, [
                "report",
                "--scored-dir", str(scored_dir),
                "--input-dir", str(input_dir),
                "--output-dir", str(output_dir),
            ])
    assert ".md" in result.output
