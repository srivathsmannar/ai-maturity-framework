import json
import tempfile
from pathlib import Path
from ai_maturity.pipeline import process_session, write_output

SAMPLE_SESSION = [
    {"type": "permission-mode", "permissionMode": "default", "sessionId": "s1"},
    {"type": "user", "isMeta": False, "message": {"role": "user", "content": "fix the CI pipeline"},
     "timestamp": "2026-04-25T10:00:00Z", "sessionId": "s1", "cwd": "/home/alice", "version": "2.1.92"},
    {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "thinking", "thinking": "let me check"},
        {"type": "tool_use", "name": "Bash", "id": "t1",
         "input": {"command": "buck2 test //foo:bar", "description": "Run tests"}}
    ]}, "timestamp": "2026-04-25T10:00:05Z", "sessionId": "s1", "cwd": "/home/alice", "version": "2.1.92"},
    {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Agent", "id": "t2",
         "input": {"subagent_type": "Plan", "description": "Design fix", "prompt": "plan the fix"}}
    ]}, "timestamp": "2026-04-25T10:00:10Z", "sessionId": "s1", "cwd": "/home/alice", "version": "2.1.92"},
    {"type": "progress", "data": {"type": "hook_progress"}, "sessionId": "s1"},
    {"type": "system", "subtype": "stop_hook_summary", "hookCount": 1,
     "hookInfos": [{"command": "otel_wrapper"}],
     "timestamp": "2026-04-25T10:00:15Z", "sessionId": "s1"},
    {"type": "user", "toolUseResult": {"success": True},
     "message": {"role": "user", "content": "result"}, "sessionId": "s1"},
]

def _write_session(records, tmp_path):
    session_file = tmp_path / "test-session.jsonl"
    with open(session_file, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
    return session_file

def test_process_session_count(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    # permission-mode → skip, user prompt → 1, bash tool → 1,
    # agent → 1, progress → skip, system hook → 1, tool_result → skip
    assert len(results) == 4

def test_process_session_ids_sequential(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    ids = [r["id"] for r in results]
    assert ids == ["in-001", "in-002", "in-003", "in-004"]

def test_process_session_routing(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    sub_dims = [r["sub_dimension"] for r in results]
    assert "cicd_integration" in sub_dims  # "fix the CI pipeline" prompt AND buck2 test
    assert "agent_configuration" in sub_dims  # Agent spawn + hook summary

def test_process_session_output_schema(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    required_fields = {"id", "category", "sub_dimension", "dimension", "team", "user",
                       "session_id", "timestamp", "source", "data", "metadata"}
    for r in results:
        assert required_fields.issubset(r.keys()), f"Missing fields: {required_fields - r.keys()}"
        assert r["team"] == "platform"
        assert r["user"] == "alice"
        assert r["source"] == "claude_session_log"

def test_process_session_categories(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    categories = [r["category"] for r in results]
    assert "prompts" in categories
    assert "tool_usage" in categories
    assert "agent_delegation" in categories
    assert "session_metadata" in categories

def test_process_session_metadata(tmp_path):
    session_file = _write_session(SAMPLE_SESSION, tmp_path)
    results = process_session(session_file, team="platform", user="alice")
    prompt_record = results[0]
    assert prompt_record["metadata"]["cwd"] == "/home/alice"
    assert prompt_record["metadata"]["version"] == "2.1.92"

def test_malformed_json_skipped(tmp_path):
    session_file = tmp_path / "bad.jsonl"
    session_file.write_text('{"type": "user", "isMeta": false, "message": {"role": "user", "content": "hi"}, "timestamp": "2026-04-25T10:00:00Z", "sessionId": "s1"}\n{bad json\n')
    results = process_session(session_file, team="t", user="u")
    assert len(results) == 1

def test_write_output(tmp_path):
    records = [{"id": "in-001", "category": "prompts", "data": {"prompt_text": "hello"}}]
    out = tmp_path / "output" / "test.jsonl"
    write_output(records, out)
    assert out.exists()
    lines = out.read_text().strip().split("\n")
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["id"] == "in-001"
