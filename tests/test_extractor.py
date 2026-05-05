from ai_maturity.extractor import extract_record

def test_extract_prompt():
    record = {
        "type": "user", "isMeta": False,
        "message": {"role": "user", "content": "fix the bug"},
        "timestamp": "2026-04-25T14:30:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result is not None
    assert result["record_type"] == "prompt"
    assert result["data"]["prompt_text"] == "fix the bug"
    assert result["timestamp"] == "2026-04-25T14:30:00Z"

def test_extract_prompt_list_content():
    record = {
        "type": "user", "isMeta": False,
        "message": {"role": "user", "content": [
            {"type": "text", "text": "hello world"}
        ]},
        "timestamp": "2026-04-25T14:30:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["data"]["prompt_text"] == "hello world"

def test_extract_tool_call():
    record = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Bash", "id": "t1",
             "input": {"command": "pytest tests/ -v", "description": "Run tests"}}
        ]},
        "timestamp": "2026-04-25T14:31:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["record_type"] == "tool_call"
    assert result["data"]["tool_name"] == "Bash"
    assert result["data"]["input"]["command"] == "pytest tests/ -v"

def test_extract_agent_spawn():
    record = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Agent", "id": "t1",
             "input": {"subagent_type": "Plan", "description": "Design approach", "prompt": "design the thing"}}
        ]},
        "timestamp": "2026-04-25T14:32:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["record_type"] == "agent_spawn"
    assert result["data"]["agent_type"] == "Plan"
    assert result["data"]["agent_description"] == "Design approach"
    assert result["data"]["agent_prompt_summary"] == "design the thing"
    assert result["data"]["tool_name"] == "Agent"

def test_extract_agent_spawn_default_type():
    record = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Agent", "id": "t1",
             "input": {"description": "Do work", "prompt": "do the work"}}
        ]},
        "timestamp": "2026-04-25T14:32:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["data"]["agent_type"] == "general-purpose"

def test_extract_skill_invocation():
    record = {
        "type": "assistant",
        "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Skill", "id": "t1",
             "input": {"skill": "google-docs", "args": "create a new doc"}}
        ]},
        "timestamp": "2026-04-25T14:33:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["record_type"] == "skill_invocation"
    assert result["data"]["tool_name"] == "Skill"
    assert result["data"]["input"]["skill"] == "google-docs"

def test_extract_skip_returns_none():
    record = {"type": "progress", "data": {"type": "hook_progress"}}
    assert extract_record(record) is None

def test_extract_session_config():
    record = {
        "type": "system", "subtype": "stop_hook_summary",
        "hookCount": 2, "hookInfos": [{"command": "otel_wrapper"}],
        "timestamp": "2026-04-25T14:34:00Z", "sessionId": "sess-1"
    }
    result = extract_record(record)
    assert result["record_type"] == "session_config"
    assert result["data"]["subtype"] == "stop_hook_summary"
    assert result["data"]["hook_count"] == 2
    assert result["data"]["hooks"] == [{"command": "otel_wrapper"}]

def test_extract_tool_result_skipped():
    record = {
        "type": "user", "toolUseResult": {"success": True},
        "message": {"role": "user", "content": "result"},
        "timestamp": "2026-04-25T14:35:00Z", "sessionId": "sess-1"
    }
    assert extract_record(record) is None
