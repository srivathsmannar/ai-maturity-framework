from __future__ import annotations

import json
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

GRADING_SCHEMA = {
    "type": "object",
    "properties": {
        "level": {
            "type": "integer",
            "minimum": 1,
            "maximum": 4,
            "description": "Maturity level: 1=Assisted, 2=Integrated, 3=Agentic, 4=Autonomous"
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
            "description": "Confidence in the grade"
        },
        "evidence": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Specific excerpts that justify the score"
        },
        "matched_signals": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Signal patterns from the rubric that were detected"
        },
        "reasoning": {
            "type": "string",
            "description": "1-2 sentence explanation"
        }
    },
    "required": ["level", "confidence", "evidence", "matched_signals", "reasoning"]
}


def call_claude_judge(
    prompt: str,
    model: str = "sonnet",
) -> Optional[dict]:
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--json-schema", json.dumps(GRADING_SCHEMA),
        "--model", model,
        "--no-session-persistence",
        "--bare",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        logger.error("Claude subprocess timed out")
        return None

    if result.returncode != 0:
        logger.error("Claude subprocess failed (exit %d): %s", result.returncode, result.stderr[:500])
        return None

    try:
        outer = json.loads(result.stdout)
        if isinstance(outer, dict) and "structured_output" in outer:
            return outer["structured_output"]
        return outer
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        logger.error("Failed to parse Claude response: %s — raw: %s", e, result.stdout[:500])
        return None
