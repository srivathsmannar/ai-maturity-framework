import json
import pytest
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
    store.save_developer("alice@co.com", "alice", "platform")
    dev = store.get_developer("alice@co.com")
    assert dev is not None
    assert dev["name"] == "alice"
    assert dev["email"] == "alice@co.com"
    assert dev["team"] == "platform"

def test_get_nonexistent_developer(tmp_path):
    store = Store(tmp_path / "test.db")
    assert store.get_developer("nobody@co.com") is None

def test_save_and_get_records(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_records("alice@co.com", SAMPLE_RECORDS)
    records = store.get_records("alice@co.com")
    assert len(records) == 2
    assert records[0]["id"] == "in-001"

def test_save_records_replaces_previous(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_records("alice@co.com", SAMPLE_RECORDS)
    store.save_records("alice@co.com", [SAMPLE_RECORDS[0]])
    records = store.get_records("alice@co.com")
    assert len(records) == 1

def test_save_and_get_scores(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_scores("alice@co.com", SAMPLE_SCORES)
    scores = store.get_scores("alice@co.com")
    assert len(scores) == 1
    assert scores[0]["level"] == 2

def test_list_developers(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_developer("bob@co.com", "bob", "infra")
    devs = store.list_developers()
    emails = [d["email"] for d in devs]
    assert "alice@co.com" in emails
    assert "bob@co.com" in emails

def test_developer_has_scores_flag(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    devs = store.list_developers()
    assert devs[0]["has_scores"] is False
    store.save_scores("alice@co.com", SAMPLE_SCORES)
    devs = store.list_developers()
    assert devs[0]["has_scores"] is True

def test_write_records_jsonl(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_records("alice@co.com", SAMPLE_RECORDS)
    path = store.write_records_jsonl("alice@co.com")
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 2

def test_write_scores_jsonl(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_scores("alice@co.com", SAMPLE_SCORES)
    path = store.write_scores_jsonl("alice@co.com")
    assert path.exists()
    lines = path.read_text().strip().split("\n")
    assert len(lines) == 1

def test_same_name_different_emails(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@platform.com", "alice", "platform")
    store.save_developer("alice@infra.com", "alice", "infra")
    store.save_records("alice@platform.com", SAMPLE_RECORDS)
    store.save_records("alice@infra.com", [SAMPLE_RECORDS[0]])
    assert len(store.get_records("alice@platform.com")) == 2
    assert len(store.get_records("alice@infra.com")) == 1
    devs = store.list_developers()
    assert len(devs) == 2

def test_export_developer(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_records("alice@co.com", SAMPLE_RECORDS)
    out = tmp_path / "alice_records.jsonl"
    count = store.export_developer("alice@co.com", out)
    assert count == 2
    lines = out.read_text().strip().split("\n")
    assert len(lines) == 3  # 1 metadata + 2 records
    meta = json.loads(lines[0])
    assert meta["type"] == "developer"
    assert meta["email"] == "alice@co.com"
    assert meta["name"] == "alice"
    assert meta["team"] == "platform"
    rec = json.loads(lines[1])
    assert rec["id"] == "in-001"

def test_export_developer_not_found(tmp_path):
    store = Store(tmp_path / "test.db")
    out = tmp_path / "nobody.jsonl"
    with pytest.raises(ValueError, match="not found"):
        store.export_developer("nobody@co.com", out)

def test_import_developer(tmp_path):
    store_a = Store(tmp_path / "a.db")
    store_a.save_developer("alice@co.com", "alice", "platform")
    store_a.save_records("alice@co.com", SAMPLE_RECORDS)
    export_path = tmp_path / "alice_records.jsonl"
    store_a.export_developer("alice@co.com", export_path)

    store_b = Store(tmp_path / "b.db")
    count = store_b.import_developer(export_path)
    assert count == 2
    dev = store_b.get_developer("alice@co.com")
    assert dev is not None
    assert dev["name"] == "alice"
    records = store_b.get_records("alice@co.com")
    assert len(records) == 2
    assert records[0]["id"] == "in-001"

def test_import_developer_replaces_existing(tmp_path):
    store = Store(tmp_path / "test.db")
    store.save_developer("alice@co.com", "alice", "platform")
    store.save_records("alice@co.com", SAMPLE_RECORDS)
    export_path = tmp_path / "alice_records.jsonl"
    store.export_developer("alice@co.com", export_path)
    count = store.import_developer(export_path)
    assert count == 2
    assert len(store.get_records("alice@co.com")) == 2

def test_import_developer_invalid_file(tmp_path):
    store = Store(tmp_path / "test.db")
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text("not json\n")
    with pytest.raises(ValueError, match="invalid"):
        store.import_developer(bad_file)

def test_import_developer_missing_metadata(tmp_path):
    store = Store(tmp_path / "test.db")
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text(json.dumps({"type": "record", "id": "x"}) + "\n")
    with pytest.raises(ValueError, match="metadata"):
        store.import_developer(bad_file)
