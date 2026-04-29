import subprocess
from unittest.mock import MagicMock
from ai_maturity.claude_writer import call_claude_writer

def test_returns_text(monkeypatch):
    mock = MagicMock(returncode=0, stdout="This is a well-written narrative about AI maturity.")
    monkeypatch.setattr("ai_maturity.claude_writer.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_writer("write a narrative")
    assert result == "This is a well-written narrative about AI maturity."

def test_returns_none_on_failure(monkeypatch):
    mock = MagicMock(returncode=1, stdout="", stderr="error")
    monkeypatch.setattr("ai_maturity.claude_writer.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_writer("write something")
    assert result is None

def test_returns_none_on_timeout(monkeypatch):
    def timeout_run(*a, **kw):
        raise subprocess.TimeoutExpired(cmd="claude", timeout=120)
    monkeypatch.setattr("ai_maturity.claude_writer.subprocess.run", timeout_run)
    result = call_claude_writer("write something")
    assert result is None

def test_strips_whitespace(monkeypatch):
    mock = MagicMock(returncode=0, stdout="\n  Some narrative text.\n\n")
    monkeypatch.setattr("ai_maturity.claude_writer.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_writer("write")
    assert result == "Some narrative text."
