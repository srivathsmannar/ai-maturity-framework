from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone


def _parse_ts(ts: str) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = (len(sorted_vals) - 1) * p / 100
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


def _dist_stats(values: list[float]) -> dict:
    if not values:
        return {"mean": 0.0, "median": 0.0, "p25": 0.0, "p75": 0.0}
    s = sorted(values)
    mean = sum(s) / len(s)
    return {
        "mean": round(mean, 2),
        "median": round(_percentile(s, 50), 2),
        "p25": round(_percentile(s, 25), 2),
        "p75": round(_percentile(s, 75), 2),
    }


def compute_metrics(records: list[dict]) -> dict:
    if not records:
        return {
            "session_count": 0,
            "total_messages": 0,
            "tool_call_count": 0,
            "agent_spawn_count": 0,
            "skill_invocation_count": 0,
            "records_by_category": {},
            "records_by_sub_dimension": {},
            "hour_distribution": {},
            "day_of_week_distribution": {},
            "session_duration_minutes": _dist_stats([]),
            "messages_per_session": _dist_stats([]),
        }

    all_session_ids: set[str] = set()
    session_timestamps: dict[str, list[datetime]] = defaultdict(list)
    session_messages: dict[str, int] = defaultdict(int)
    category_counts: Counter = Counter()
    sd_counts: Counter = Counter()
    hour_counts: Counter = Counter()
    dow_counts: Counter = Counter()
    tool_calls = agent_spawns = skill_invocations = total_messages = 0

    for rec in records:
        sid = rec.get("session_id", "unknown")
        rtype = rec.get("record_type", "")
        category = rec.get("category", "")
        sd = rec.get("sub_dimension", "")
        ts_str = rec.get("timestamp", "")

        all_session_ids.add(sid)
        category_counts[category] += 1
        if sd:
            sd_counts[sd] += 1

        if rtype == "prompt":
            total_messages += 1
            session_messages[sid] += 1

        if rtype == "tool_call":
            tool_calls += 1
        elif rtype == "agent_spawn":
            agent_spawns += 1
        elif rtype == "skill_invocation":
            skill_invocations += 1

        ts = _parse_ts(ts_str)
        if ts:
            session_timestamps[sid].append(ts)
            hour_counts[ts.hour] += 1
            dow_counts[ts.weekday()] += 1

    durations = []
    for sid in all_session_ids:
        timestamps = session_timestamps.get(sid, [])
        if len(timestamps) >= 2:
            s = sorted(timestamps)
            durations.append((s[-1] - s[0]).total_seconds() / 60)
        else:
            durations.append(0.0)

    return {
        "session_count": len(all_session_ids),
        "total_messages": total_messages,
        "tool_call_count": tool_calls,
        "agent_spawn_count": agent_spawns,
        "skill_invocation_count": skill_invocations,
        "records_by_category": dict(category_counts),
        "records_by_sub_dimension": dict(sd_counts),
        "hour_distribution": {k: v for k, v in sorted(hour_counts.items())},
        "day_of_week_distribution": {k: v for k, v in sorted(dow_counts.items())},
        "session_duration_minutes": _dist_stats(durations),
        "messages_per_session": _dist_stats(list(session_messages.values())),
    }
