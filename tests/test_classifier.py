from ai_maturity.classifier import classify_record

def test_user_prompt():
    record = {"type": "user", "message": {"role": "user", "content": "fix the tests"}, "isMeta": False}
    assert classify_record(record) == "prompt"

def test_user_meta_skipped():
    record = {"type": "user", "message": {"role": "user", "content": "text"}, "isMeta": True}
    assert classify_record(record) == "skip"

def test_user_tool_result_skipped():
    record = {"type": "user", "toolUseResult": {"success": True}, "message": {"role": "user", "content": "x"}}
    assert classify_record(record) == "skip"

def test_user_source_tool_skipped():
    record = {"type": "user", "sourceToolUseID": "toolu_123", "message": {"role": "user", "content": "x"}}
    assert classify_record(record) == "skip"

def test_assistant_tool_use():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Bash", "id": "t1", "input": {"command": "ls"}}
    ]}}
    assert classify_record(record) == "tool_call"

def test_assistant_agent_spawn():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Agent", "id": "t1", "input": {"prompt": "do stuff"}}
    ]}}
    assert classify_record(record) == "agent_spawn"

def test_assistant_skill_invocation():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Skill", "id": "t1", "input": {"skill": "google-docs"}}
    ]}}
    assert classify_record(record) == "skill_invocation"

def test_assistant_toolsearch_skipped():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "ToolSearch", "id": "t1", "input": {"query": "select:Bash"}}
    ]}}
    assert classify_record(record) == "skip"

def test_assistant_ask_user_question_skipped():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "AskUserQuestion", "id": "t1", "input": {"question": "which approach?"}}
    ]}}
    assert classify_record(record) == "skip"

def test_system_hook_summary():
    record = {"type": "system", "subtype": "stop_hook_summary", "hookCount": 2}
    assert classify_record(record) == "session_config"

def test_system_local_command():
    record = {"type": "system", "subtype": "local_command", "content": "/review"}
    assert classify_record(record) == "session_config"

def test_system_turn_duration_skipped():
    record = {"type": "system", "subtype": "turn_duration", "durationMs": 5000}
    assert classify_record(record) == "skip"

def test_system_api_error_skipped():
    record = {"type": "system", "subtype": "api_error"}
    assert classify_record(record) == "skip"

def test_progress_skipped():
    record = {"type": "progress", "data": {"type": "hook_progress"}}
    assert classify_record(record) == "skip"

def test_file_history_skipped():
    record = {"type": "file-history-snapshot", "snapshot": {}}
    assert classify_record(record) == "skip"

def test_assistant_thinking_only_skipped():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "thinking", "thinking": "let me think..."},
        {"type": "text", "text": "here is my answer"}
    ]}}
    assert classify_record(record) == "skip"

def test_assistant_mixed_returns_first_tool():
    record = {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "thinking", "thinking": "planning"},
        {"type": "tool_use", "name": "Read", "id": "t1", "input": {"file_path": "/tmp/x"}}
    ]}}
    assert classify_record(record) == "tool_call"
