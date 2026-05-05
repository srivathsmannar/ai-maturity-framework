import json
from ai_maturity.store import Store

SAMPLE_RECORDS = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "help me debug"}},
    {"id": "in-002", "category": "tool_usage", "sub_dimension": "agent_configuration",
     "data": {"tool_name": "Agent", "input": {}}},
]

SAMPLE_SCORES = [
    {"sub_dimension": "ai_tool_adoption", "level": 2, "confidence": "high",
     "reasoning": "Uses tools deliberately."},
]

def test_save_and_get_developer(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    dev = store.get_developer("alice")
    assert dev is not None
    assert dev["name"] == "alice"
    assert dev["team"] == "platform"

def test_get_nonexistent_developer(tmp_path):
    store = Store(tmp_path / "test.db")
    assert store.get_developer("nobody") is None

def test_save_and_get_records(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_records("alice", SAMPLE_RECORDS)
    records = store.get_records("alice")
    assert len(records) == 2
    assert records[0]["id"] == "in-001"

def test_save_records_replaces_previous(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_records("alice", SAMPLE_RECORDS)
    store.save_records("alice", [SAMPLE_RECORDS[0]])
    records = store.get_records("alice")
    assert len(records) == 1

def test_save_and_get_scores(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_scores("alice", SAMPLE_SCORES)
    scores = store.get_scores("alice")
    assert len(scores) == 1
    assert scores[0]["level"] == 2

def test_list_developers(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_developer("bob", "infra")
    devs = store.list_developers()
    names = [d["name"] for d in devs]
    assert "alice" in names
    assert "bob" in names

def test_developer_has_scores_flag(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    devs = store.list_developers()
    assert devs[0]["has_scores"] is False
    store.save_scores("alice", SAMPLE_SCORES)
    devs = store.list_developers()
    assert devs[0]["has_scores"] is True

def test_write_records_jsonl(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_records("alice", SAMPLE_RECORDS)
    path = store.write_records_jsonl("alice")
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2

def test_write_scores_jsonl(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice", "platform")
    store.save_scores("alice", SAMPLE_SCORES)
    path = store.write_scores_jsonl("alice")
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 1
