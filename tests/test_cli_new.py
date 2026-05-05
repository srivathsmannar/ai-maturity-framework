import json
from pathlib import Path
from unittest.mock import patch
from click.testing import CliRunner
from ai_maturity.cli import cli

SAMPLE_SESSION_RECORD = {
    "type": "user", "isMeta": False,
    "message": {"role": "user", "content": "help me debug this"},
    "timestamp": "2026-04-25T10:00:00Z", "sessionId": "s1"
}

FAKE_JUDGE = {
    "level": 2, "confidence": "medium",
    "evidence": ["debug request"], "matched_signals": ["ad-hoc"],
    "reasoning": "Basic usage."
}

def test_submit_creates_developer(tmp_path):
    db = tmp_path / "test.db"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    (session_dir / "abc123.jsonl").write_text(json.dumps(SAMPLE_SESSION_RECORD) + "\n")
    runner = CliRunner()
    result = runner.invoke(cli, ["submit", str(session_dir), "--name", "alice", "--team", "platform", "--db", str(db)])
    assert result.exit_code == 0, result.output
    assert "alice" in result.output
    from ai_maturity.store import Store
    store = Store(db)
    assert store.get_developer("alice") is not None
    assert len(store.get_records("alice")) > 0

def test_assess_grades_developer(tmp_path):
    db = tmp_path / "test.db"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    (session_dir / "abc123.jsonl").write_text(json.dumps(SAMPLE_SESSION_RECORD) + "\n")
    runner = CliRunner()
    runner.invoke(cli, ["submit", str(session_dir), "--name", "alice", "--team", "t", "--db", str(db)])
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        result = runner.invoke(cli, ["assess", "alice", "--db", str(db)])
    assert result.exit_code == 0, result.output
    assert "Overall" in result.output
    from ai_maturity.store import Store
    store = Store(db)
    scores = store.get_scores("alice")
    assert len(scores) == 12

def test_report_generates_output(tmp_path):
    db = tmp_path / "test.db"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    (session_dir / "abc123.jsonl").write_text(json.dumps(SAMPLE_SESSION_RECORD) + "\n")
    runner = CliRunner()
    runner.invoke(cli, ["submit", str(session_dir), "--name", "alice", "--team", "t", "--db", str(db)])
    with patch("ai_maturity.grader.call_claude_judge", return_value=FAKE_JUDGE):
        runner.invoke(cli, ["assess", "alice", "--db", str(db)])
    report_dir = tmp_path / "reports"
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative."):
        with patch("ai_maturity.report.extract_project_context", return_value="Context."):
            result = runner.invoke(cli, ["report", "alice", "--db", str(db), "--output-dir", str(report_dir), "--format", "md"])
    assert result.exit_code == 0, result.output
    assert len(list(report_dir.glob("*.md"))) >= 1

def test_list_shows_developers(tmp_path):
    db = tmp_path / "test.db"
    session_dir = tmp_path / "sessions"
    session_dir.mkdir()
    (session_dir / "abc123.jsonl").write_text(json.dumps(SAMPLE_SESSION_RECORD) + "\n")
    runner = CliRunner()
    runner.invoke(cli, ["submit", str(session_dir), "--name", "alice", "--team", "platform", "--db", str(db)])
    runner.invoke(cli, ["submit", str(session_dir), "--name", "bob", "--team", "infra", "--db", str(db)])
    result = runner.invoke(cli, ["list", "--db", str(db)])
    assert result.exit_code == 0
    assert "alice" in result.output
    assert "bob" in result.output

def test_assess_unknown_developer(tmp_path):
    db = tmp_path / "test.db"
    runner = CliRunner()
    result = runner.invoke(cli, ["assess", "nobody", "--db", str(db)])
    assert result.exit_code == 0
    assert "not found" in result.output.lower()
