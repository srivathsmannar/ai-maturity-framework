from ai_maturity.router import route_record


def test_prompt_security():
    assert route_record("prompt", {"prompt_text": "make sure there's no PII in the output"}) == "security_compliance"


def test_prompt_ticket_id():
    assert route_record("prompt", {"prompt_text": "I'm working on T260669092"}) == "ticketing_planning"


def test_prompt_jira():
    assert route_record("prompt", {"prompt_text": "check ACME-234 before starting"}) == "ticketing_planning"


def test_prompt_cicd():
    assert route_record("prompt", {"prompt_text": "the CI is failing, can you look at it?"}) == "cicd_integration"


def test_prompt_generic_defaults():
    assert route_record("prompt", {"prompt_text": "help me debug this"}) == "ai_tool_adoption"


def test_prompt_context_engineering():
    assert route_record("prompt", {"prompt_text": "following our conventions from CLAUDE.md"}) == "prompt_context_engineering"


def test_prompt_measurement():
    assert route_record("prompt", {"prompt_text": "track adoption rate and KPIs across the team"}) == "measurement_kpis"


def test_prompt_ways_of_working_readme():
    assert route_record("prompt", {"prompt_text": "check the README for our team process"}) == "ways_of_working"


def test_skill_google_docs():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "google-docs"}}) == "cross_system_connectivity"


def test_skill_review_diff():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "review-diff"}}) == "quality_controls"


def test_skill_ci_signals():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "ci-signals"}}) == "cicd_integration"


def test_skill_namespaced():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "workflow:code-reviewer"}}) == "quality_controls"


def test_skill_generic():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "brainstorming"}}) == "agent_configuration"


def test_tool_call_agent():
    assert route_record("agent_spawn", {"tool_name": "Agent", "input": {"subagent_type": "Plan"}}) == "agent_configuration"


def test_tool_call_bash_test():
    assert route_record("tool_call", {"tool_name": "Bash", "input": {"command": "pytest tests/ -v"}}) == "cicd_integration"


def test_tool_call_bash_lint():
    assert route_record("tool_call", {"tool_name": "Bash", "input": {"command": "flake8 src/"}}) == "quality_controls"


def test_tool_call_mcp():
    assert route_record("tool_call", {"tool_name": "mcp__google_docs__google_docs", "input": {}}) == "cross_system_connectivity"


def test_tool_call_read_claude_md():
    assert route_record("tool_call", {"tool_name": "Read", "input": {"file_path": "/project/CLAUDE.md"}}) == "prompt_context_engineering"


def test_tool_call_bash_default():
    assert route_record("tool_call", {"tool_name": "Bash", "input": {"command": "ls -la"}}) == "ai_tool_adoption"


def test_session_config():
    assert route_record("session_config", {"subtype": "stop_hook_summary"}) == "agent_configuration"


def test_tool_call_webfetch():
    assert route_record("tool_call", {"tool_name": "WebFetch", "input": {"url": "https://example.com"}}) == "cross_system_connectivity"


def test_tool_call_task_create():
    assert route_record("tool_call", {"tool_name": "TaskCreate", "input": {"subject": "Fix bug"}}) == "ticketing_planning"


def test_skill_sql_query():
    assert route_record("skill_invocation", {"tool_name": "Skill", "input": {"skill": "sql-query"}}) == "cross_system_connectivity"


def test_mcp_jira_routes_to_ticketing():
    assert route_record("tool_call", {"tool_name": "mcp__jira__create_issue", "input": {}}) == "ticketing_planning"


def test_mcp_linear_routes_to_ticketing():
    assert route_record("tool_call", {"tool_name": "mcp__linear__list_issues", "input": {}}) == "ticketing_planning"


def test_mcp_grafana_routes_to_measurement():
    assert route_record("tool_call", {"tool_name": "mcp__grafana__query_dashboard", "input": {}}) == "measurement_kpis"


def test_mcp_sentry_routes_to_measurement():
    assert route_record("tool_call", {"tool_name": "mcp__sentry__get_issues", "input": {}}) == "measurement_kpis"


def test_mcp_postgres_routes_to_cross_system():
    assert route_record("tool_call", {"tool_name": "mcp__postgres__query", "input": {}}) == "cross_system_connectivity"


def test_mcp_slack_routes_to_cross_system():
    assert route_record("tool_call", {"tool_name": "mcp__slack__post_message", "input": {}}) == "cross_system_connectivity"
