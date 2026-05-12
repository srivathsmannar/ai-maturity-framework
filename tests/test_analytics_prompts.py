from ai_maturity.analytics_prompts import build_analytics_prompt

SAMPLE_METRICS = {
    "session_count": 12,
    "total_messages": 87,
    "tool_call_count": 34,
    "agent_spawn_count": 8,
    "skill_invocation_count": 5,
    "records_by_category": {"prompts": 87, "tool_usage": 34, "agent_delegation": 8},
    "records_by_sub_dimension": {"ai_tool_adoption": 40, "agent_configuration": 20},
    "hour_distribution": {9: 20, 10: 30, 14: 15, 15: 22},
    "day_of_week_distribution": {0: 30, 1: 25, 2: 20, 3: 10, 4: 2},
    "session_duration_minutes": {"mean": 24.5, "median": 18.0, "p25": 8.0, "p75": 35.0},
    "messages_per_session": {"mean": 7.2, "median": 6.0, "p25": 3.0, "p75": 10.0},
}

def test_build_analytics_prompt_returns_string():
    prompt = build_analytics_prompt(SAMPLE_METRICS, user="alice", team="platform")
    assert isinstance(prompt, str)
    assert len(prompt) > 100

def test_prompt_includes_key_metrics():
    prompt = build_analytics_prompt(SAMPLE_METRICS, user="alice", team="platform")
    assert "12" in prompt        # session_count
    assert "87" in prompt        # total_messages
    assert "24.5" in prompt      # mean session duration

def test_prompt_requests_table_and_narrative():
    prompt = build_analytics_prompt(SAMPLE_METRICS, user="alice", team="platform")
    assert "table" in prompt.lower()
    assert "narrative" in prompt.lower() or "analysis" in prompt.lower()
