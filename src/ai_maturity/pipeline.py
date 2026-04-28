from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from ai_maturity.extractor import extract_record
from ai_maturity.router import route_record
from ai_maturity.taxonomy import dimension_for

logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    "prompt": "prompts",
    "tool_call": "tool_usage",
    "agent_spawn": "agent_delegation",
    "skill_invocation": "tool_usage",
    "session_config": "session_metadata",
}


def process_session(
    session_path: Path,
    team: str,
    user: str,
) -> list[dict]:
    results = []
    seq = 0

    with open(session_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSON at %s:%d", session_path.name, line_num)
                continue

            extracted = extract_record(raw)
            if extracted is None:
                continue

            record_type = extracted["record_type"]
            data = extracted["data"]
            sub_dim = route_record(record_type, data)
            dim = dimension_for(sub_dim)

            seq += 1
            results.append({
                "id": f"in-{seq:03d}",
                "category": CATEGORY_MAP.get(record_type, "prompts"),
                "sub_dimension": sub_dim,
                "dimension": dim,
                "team": team,
                "user": user,
                "session_id": extracted["session_id"],
                "timestamp": extracted["timestamp"],
                "source": "claude_session_log",
                "data": data,
                "metadata": {
                    "cwd": raw.get("cwd", ""),
                    "version": raw.get("version", ""),
                },
            })

    return results


def write_output(results: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for record in results:
            f.write(json.dumps(record) + "\n")
