import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
from ai_maturity.cli import cli

SAMPLE_RECORD = {"type": "user", "isMeta": False,
    "message": {"role": "user", "content": "fix the tests"},
    "timestamp": "2026-04-25T10:00:00Z", "sessionId": "s1"}

def test_upload_creates_output(tmp_path):
    session_file = tmp_path / "abc12345.jsonl"
    session_file.write_text(json.dumps(SAMPLE_RECORD) + "\n")
    output_dir = tmp_path / "output"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "upload", str(tmp_path),
        "--team-name", "platform",
        "--user-name", "alice",
        "--output-dir", str(output_dir),
    ])
    assert result.exit_code == 0, result.output
    output_files = list(output_dir.glob("*.jsonl"))
    assert len(output_files) == 1

def test_upload_output_content(tmp_path):
    session_file = tmp_path / "abc12345.jsonl"
    session_file.write_text(json.dumps(SAMPLE_RECORD) + "\n")
    output_dir = tmp_path / "output"
    runner = CliRunner()
    runner.invoke(cli, [
        "upload", str(tmp_path),
        "--team-name", "platform",
        "--user-name", "alice",
        "--output-dir", str(output_dir),
    ])
    output_file = list(output_dir.glob("*.jsonl"))[0]
    records = [json.loads(l) for l in output_file.read_text().strip().split("\n")]
    assert len(records) == 1
    assert records[0]["team"] == "platform"
    assert records[0]["user"] == "alice"
    assert records[0]["category"] == "prompts"
    assert records[0]["sub_dimension"] == "ai_tool_adoption"

def test_upload_no_files(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    runner = CliRunner()
    result = runner.invoke(cli, ["upload", str(empty_dir), "--team-name", "t", "--user-name", "u"])
    assert result.exit_code == 0
    assert "No .jsonl files" in result.output

def test_upload_summary_output(tmp_path):
    session_file = tmp_path / "abc12345.jsonl"
    session_file.write_text(json.dumps(SAMPLE_RECORD) + "\n")
    output_dir = tmp_path / "output"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "upload", str(tmp_path),
        "--team-name", "myteam",
        "--user-name", "bob",
        "--output-dir", str(output_dir),
    ])
    assert "1 records" in result.output
    assert "Done" in result.output
