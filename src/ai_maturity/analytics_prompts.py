from __future__ import annotations

_DOW_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _peak_hours(hour_dist: dict) -> str:
    if not hour_dist:
        return "unknown"
    top = sorted(hour_dist.items(), key=lambda x: x[1], reverse=True)[:3]
    return ", ".join(f"{int(h):02d}:00" for h, _ in top)


def _peak_days(dow_dist: dict) -> str:
    if not dow_dist:
        return "unknown"
    top = sorted(dow_dist.items(), key=lambda x: x[1], reverse=True)[:3]
    return ", ".join(_DOW_NAMES[int(d)] for d, _ in top if int(d) < 7)


def build_analytics_prompt(metrics: dict, user: str, team: str) -> str:
    sd_breakdown = "\n".join(
        f"  - {sd}: {count} records"
        for sd, count in sorted(metrics.get("records_by_sub_dimension", {}).items(),
                                key=lambda x: x[1], reverse=True)
    )
    cat_breakdown = "\n".join(
        f"  - {cat}: {count}"
        for cat, count in sorted(metrics.get("records_by_category", {}).items(),
                                 key=lambda x: x[1], reverse=True)
    )
    dur = metrics.get("session_duration_minutes", {})
    mps = metrics.get("messages_per_session", {})

    return f"""You are writing the Usage Analytics section of an AI maturity assessment report for {user} ({team}).

Below are quantitative metrics extracted from their Claude Code session logs. Write a brief analytics section that includes:

1. A markdown table summarising the key metrics (session volume, message activity, tool/agent/skill usage, session length, working patterns).
2. A 2-3 paragraph narrative analysis that interprets what these metrics reveal about how {user} works with AI — their cadence, depth of engagement, preferred interaction style, and working hours patterns.

Keep the tone factual and constructive. Do not repeat numbers already in the table in the narrative — instead interpret what they mean.

## Raw Metrics

**Volume**
- Sessions: {metrics.get('session_count', 0)}
- Total messages (prompts): {metrics.get('total_messages', 0)}
- Tool calls: {metrics.get('tool_call_count', 0)}
- Agent spawns: {metrics.get('agent_spawn_count', 0)}
- Skill invocations: {metrics.get('skill_invocation_count', 0)}

**Session length (minutes)**
- Mean: {dur.get('mean', 0)} | Median: {dur.get('median', 0)} | P25: {dur.get('p25', 0)} | P75: {dur.get('p75', 0)}

**Messages per session**
- Mean: {mps.get('mean', 0)} | Median: {mps.get('median', 0)} | P25: {mps.get('p25', 0)} | P75: {mps.get('p75', 0)}

**Records by category**
{cat_breakdown}

**Records by sub-dimension**
{sd_breakdown}

**Working patterns**
- Peak hours (UTC): {_peak_hours(metrics.get('hour_distribution', {}))}
- Most active days: {_peak_days(metrics.get('day_of_week_distribution', {}))}

Write the analytics section now. Start with the markdown table, then the narrative.
"""
