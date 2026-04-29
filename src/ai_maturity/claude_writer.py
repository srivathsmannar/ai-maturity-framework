from __future__ import annotations

import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def call_claude_writer(
    prompt: str,
    model: str = "sonnet",
) -> Optional[str]:
    cmd = [
        "claude",
        "-p",
        "--output-format", "text",
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
        logger.error("Claude writer subprocess timed out")
        return None

    if result.returncode != 0:
        logger.error("Claude writer failed (exit %d): %s", result.returncode, result.stderr[:500])
        return None

    return result.stdout.strip()
