from __future__ import annotations

import re
from typing import Dict


# ---------------------------------------------------------------------------
# Skill-name -> sub-dimension lookup
# ---------------------------------------------------------------------------
_SKILL_ROUTES: Dict[str, set[str]] = {
    "cross_system_connectivity": {
        "presto-query", "daiquery", "scuba", "datamate",
        "google-docs", "wiki-query", "scuba_cli",
    },
    "cicd_integration": {
        "ci-signals", "fix-diff", "continuous-integration-data",
    },
    "quality_controls": {
        "review-diff", "code-reviewer", "simplify",
        "auto-review-diff", "team-review",
    },
    "ticketing_planning": {
        "tasks", "diff-search",
    },
    "security_compliance": {
        "security-review", "agent-security-guardrails",
    },
    "measurement_kpis": {
        "ods-counter-analyzer", "metric360", "ods-helper", "ods-cli",
    },
    "prompt_context_engineering": {
        "init",
    },
}

# Invert so we can look up skill_name -> sub_dimension quickly.
_SKILL_LOOKUP: Dict[str, str] = {
    skill: sub_dim
    for sub_dim, skills in _SKILL_ROUTES.items()
    for skill in skills
}

# ---------------------------------------------------------------------------
# Prompt routing — priority-ordered keyword lists
# ---------------------------------------------------------------------------
_PROMPT_RULES: list[tuple[str, list[str]]] = [
    ("security_compliance", [
        "pii", "compliance", "policy", "secrets", "credentials",
        "audit", "gdpr", "soc2", "redact", "data handling",
    ]),
    ("measurement_kpis", [
        "metric", "kpi", "dashboard", "adoption rate", "dora",
        "velocity", "throughput", "cycle time", "mttr", "measure",
    ]),
    ("ticketing_planning", [
        "ticket", "jira", "linear", "issue", "backlog", "sprint",
        "story point", "acceptance criteria",
    ]),
    ("cicd_integration", [
        "ci", "cd", "pipeline", "deploy", "build log", "test failure",
        "github actions", "jenkins", "rollback", "merge gate",
    ]),
    ("quality_controls", [
        "quality", "lint", "checklist", "test coverage", "eval harness",
        "code review criteria", "auto-reject",
    ]),
    ("accountability_ownership", [
        "owner", "champion", "responsible", "team owns", "sla",
        "accountability",
    ]),
    ("ways_of_working", [
        "ways of working", "protocol", "convention", "team process",
        "documented workflow", "readme", "wiki",
    ]),
    ("scalability_knowledge_transfer", [
        "onboarding", "playbook", "knowledge transfer", "ramp-up",
        "template library", "new team",
    ]),
    ("agent_configuration", [
        "skill", "custom agent", "workflow chain", "spawn sub-agent",
    ]),
    ("prompt_context_engineering", [
        "claude.md", "context", "convention", "architecture doc",
        "loaded from", "per our", "template", "shared prompt",
    ]),
]

# Ticket-ID regex patterns (checked before keyword scan)
_TICKET_PATTERNS = [
    re.compile(r"T\d{6,}"),          # e.g. T260669092
    re.compile(r"[A-Z]+-\d+"),       # e.g. ACME-234
]

# Slash-command pattern for agent_configuration
_SLASH_CMD = re.compile(r"(?:^|\s)/\w+")

# Cross-system connectivity: mentions 2+ systems together
_CROSS_SYSTEM_TERMS = [
    "github", "jira", "slack", "confluence", "repo", "ticketing",
    "monitoring", "alerting",
]

# ---------------------------------------------------------------------------
# Bash command regex patterns for tool-call routing
# ---------------------------------------------------------------------------
_BASH_CI_RE = re.compile(
    r"buck2 test|pytest|npm test|jest|jf submit|gh pr|git push",
    re.IGNORECASE,
)
_BASH_LINT_RE = re.compile(
    r"lint|mypy|eslint|flake8|black|prettier|clippy|coverage",
    re.IGNORECASE,
)
_BASH_CROSS_RE = re.compile(
    r"\bjf\b|\bgh\b|\bsl\b|\bhg\b|\bcurl\b|\bmeta\b",
    re.IGNORECASE,
)
_BASH_CONTEXT_RE = re.compile(
    r"CLAUDE\.md|docs/|README|architecture",
    re.IGNORECASE,
)

# Path patterns used for Read / Write / Edit routing
_CONTEXT_PATH_RE = re.compile(
    r"CLAUDE\.md|docs/|README|architecture",
    re.IGNORECASE,
)


# ===================================================================
# Public API
# ===================================================================

def route_record(record_type: str, data: dict) -> str:
    """Route a classified record to exactly one of the 12 sub-dimensions."""

    if record_type == "session_config":
        return "agent_configuration"

    if record_type in ("prompt", "user_prompt"):
        return _route_prompt(data)

    if record_type == "skill_invocation":
        return _route_skill(data)

    if record_type == "agent_spawn":
        return "agent_configuration"

    if record_type == "tool_call":
        return _route_tool_call(data)

    # Unknown record types default to ai_tool_adoption
    return "ai_tool_adoption"


# -------------------------------------------------------------------
# Internal routers
# -------------------------------------------------------------------

def _route_prompt(data: dict) -> str:
    text = (data.get("prompt_text") or "").lower()

    # 1. Check ticket-ID patterns first (maps to ticketing_planning, rule #3)
    for pat in _TICKET_PATTERNS:
        if pat.search(data.get("prompt_text") or ""):
            return "ticketing_planning"

    # 1b. CLAUDE.md is a strong signal for prompt_context_engineering
    if "claude.md" in text:
        return "prompt_context_engineering"

    # 2. Priority-ordered keyword scan
    for sub_dim, keywords in _PROMPT_RULES:
        for kw in keywords:
            if kw in text:
                # Special guard: "CI" should only match as a whole word
                if kw == "ci" and not re.search(r"\bci\b", text, re.IGNORECASE):
                    continue
                return sub_dim

    # 3. Slash-command pattern -> agent_configuration
    if _SLASH_CMD.search(data.get("prompt_text") or ""):
        return "agent_configuration"

    # 4. Cross-system connectivity: 2+ system terms together
    hits = sum(1 for t in _CROSS_SYSTEM_TERMS if t in text)
    if hits >= 2:
        return "cross_system_connectivity"

    return "ai_tool_adoption"


def _route_skill(data: dict) -> str:
    skill_name = ""
    inp = data.get("input") or {}
    if isinstance(inp, dict):
        skill_name = inp.get("skill", "")
    # Handle namespaced skills: "10x-engineer:code-reviewer" -> "code-reviewer"
    if ":" in skill_name:
        skill_name = skill_name.split(":", 1)[1]

    return _SKILL_LOOKUP.get(skill_name, "agent_configuration")


def _route_tool_call(data: dict) -> str:
    tool_name = data.get("tool_name", "")
    inp = data.get("input") or {}

    # Agent tool
    if tool_name == "Agent":
        return "agent_configuration"

    # MCP tools
    if tool_name.startswith("mcp__"):
        return "cross_system_connectivity"

    # Web tools
    if tool_name in ("WebFetch", "WebSearch"):
        return "cross_system_connectivity"

    # Task tools
    if tool_name in ("TaskCreate", "TaskUpdate", "TaskGet", "TaskList"):
        return "ticketing_planning"

    # Read / Write / Edit — path-based
    if tool_name in ("Read", "Write", "Edit"):
        path = ""
        if isinstance(inp, dict):
            path = inp.get("file_path", "")
        if _CONTEXT_PATH_RE.search(path):
            return "prompt_context_engineering"
        return "ai_tool_adoption"

    # Bash — command-based
    if tool_name == "Bash":
        cmd = ""
        if isinstance(inp, dict):
            cmd = inp.get("command", "")
        if _BASH_CI_RE.search(cmd):
            return "cicd_integration"
        if _BASH_LINT_RE.search(cmd):
            return "quality_controls"
        if _BASH_CROSS_RE.search(cmd):
            return "cross_system_connectivity"
        if _BASH_CONTEXT_RE.search(cmd):
            return "prompt_context_engineering"
        return "ai_tool_adoption"

    return "ai_tool_adoption"
