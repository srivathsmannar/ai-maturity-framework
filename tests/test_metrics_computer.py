from ai_maturity.metrics_computer import compute_metrics

def _make_record(record_type, sub_dimension, session_id, timestamp, category="prompts"):
    return {
        "id": f"{record_type}-{session_id}-{sub_dimension}",
        "record_type": record_type,
        "category": category,
        "sub_dimension": sub_dimension,
        "session_id": session_id,
        "timestamp": timestamp,
        "data": {"prompt_text": "help me"},
    }

BASE_TIME = "2026-05-01T09:00:00.000Z"
LATER_TIME = "2026-05-01T09:30:00.000Z"
NEXT_DAY   = "2026-05-02T14:00:00.000Z"

SAMPLE_RECORDS = [
    _make_record("prompt", "ai_tool_adoption", "s1", BASE_TIME),
    _make_record("prompt", "ai_tool_adoption", "s1", LATER_TIME),
    _make_record("tool_call", "cicd_integration", "s1", LATER_TIME, "tool_usage"),
    _make_record("agent_spawn", "agent_configuration", "s1", LATER_TIME, "agent_delegation"),
    _make_record("skill_invocation", "agent_configuration", "s2", NEXT_DAY, "skill_usage"),
    _make_record("prompt", "prompt_context_engineering", "s2", NEXT_DAY),
]

def test_session_count():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["session_count"] == 2

def test_total_messages():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["total_messages"] == 3  # prompt records only

def test_records_by_category():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["records_by_category"]["prompts"] == 3
    assert m["records_by_category"]["tool_usage"] == 1
    assert m["records_by_category"]["agent_delegation"] == 1
    assert m["records_by_category"]["skill_usage"] == 1

def test_records_by_sub_dimension():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["records_by_sub_dimension"]["ai_tool_adoption"] == 2
    assert m["records_by_sub_dimension"]["agent_configuration"] == 2

def test_tool_agent_skill_counts():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["tool_call_count"] == 1
    assert m["agent_spawn_count"] == 1
    assert m["skill_invocation_count"] == 1

def test_hour_distribution():
    m = compute_metrics(SAMPLE_RECORDS)
    assert m["hour_distribution"].get(9, 0) >= 2
    assert m["hour_distribution"].get(14, 0) >= 1

def test_day_of_week_distribution():
    m = compute_metrics(SAMPLE_RECORDS)
    # 2026-05-01 is Friday (4), 2026-05-02 is Saturday (5)
    assert 4 in m["day_of_week_distribution"] and 5 in m["day_of_week_distribution"]

def test_session_duration_stats():
    m = compute_metrics(SAMPLE_RECORDS)
    stats = m["session_duration_minutes"]
    assert "mean" in stats and "median" in stats and "p25" in stats and "p75" in stats
    # s1: 09:00 -> 09:30 = 30 min; s2: single timestamp = 0 min; mean = 15.0
    assert stats["mean"] == 15.0
    assert stats["p25"] >= 0

def test_messages_per_session_stats():
    m = compute_metrics(SAMPLE_RECORDS)
    stats = m["messages_per_session"]
    assert "mean" in stats and "median" in stats and "p25" in stats and "p75" in stats
    # s1 has 2 prompts, s2 has 1 prompt; mean = 1.5
    assert stats["mean"] == 1.5

def test_empty_records():
    m = compute_metrics([])
    assert m["session_count"] == 0
    assert m["total_messages"] == 0
    assert m["tool_call_count"] == 0
    assert m["agent_spawn_count"] == 0
    assert m["skill_invocation_count"] == 0
    assert m["records_by_category"] == {}
    assert m["records_by_sub_dimension"] == {}
    assert m["hour_distribution"] == {}
    assert m["day_of_week_distribution"] == {}
    zero_stats = {"mean": 0.0, "median": 0.0, "p25": 0.0, "p75": 0.0}
    assert m["session_duration_minutes"] == zero_stats
    assert m["messages_per_session"] == zero_stats
