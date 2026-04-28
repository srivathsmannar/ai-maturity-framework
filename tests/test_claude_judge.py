import json
from unittest.mock import MagicMock
from ai_maturity.claude_judge import call_claude_judge, GRADING_SCHEMA

def _mock_result(level=2, confidence="high"):
    return MagicMock(
        returncode=0,
        stdout=json.dumps({
            "result": "",
            "structured_output": {
                "level": level,
                "confidence": confidence,
                "evidence": ["used Bash for testing"],
                "matched_signals": ["test commands"],
                "reasoning": "Developer runs tests via CLI.",
            }
        })
    )

def test_schema_has_required_fields():
    props = GRADING_SCHEMA["properties"]
    assert "level" in props
    assert "confidence" in props
    assert "evidence" in props
    assert "matched_signals" in props
    assert "reasoning" in props

def test_schema_level_is_integer():
    assert GRADING_SCHEMA["properties"]["level"]["type"] == "integer"
    assert GRADING_SCHEMA["properties"]["level"]["minimum"] == 1
    assert GRADING_SCHEMA["properties"]["level"]["maximum"] == 4

def test_call_claude_returns_parsed(monkeypatch):
    mock = _mock_result(level=3, confidence="medium")
    monkeypatch.setattr("ai_maturity.claude_judge.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_judge("grade this developer")
    assert result["level"] == 3
    assert result["confidence"] == "medium"
    assert isinstance(result["evidence"], list)

def test_call_claude_nonzero_exit(monkeypatch):
    mock = MagicMock(returncode=1, stdout="", stderr="error")
    monkeypatch.setattr("ai_maturity.claude_judge.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_judge("grade this")
    assert result is None

def test_call_claude_bad_json(monkeypatch):
    mock = MagicMock(returncode=0, stdout="not json at all")
    monkeypatch.setattr("ai_maturity.claude_judge.subprocess.run", lambda *a, **kw: mock)
    result = call_claude_judge("grade this")
    assert result is None
