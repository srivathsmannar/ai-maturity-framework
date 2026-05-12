from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from ai_maturity.claude_writer import call_claude_writer
from ai_maturity.exemplars import is_noise

_FALLBACK = "Developer session data was analyzed but project context could not be determined."
_MAX_PROMPT_CHARS = 15000


def extract_project_context(
    input_path: Path,
    model: str = "sonnet",
) -> str:
    prompts = []
    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            if record.get("category") != "prompts":
                continue
            if is_noise(record):
                continue
            text = record.get("data", {}).get("prompt_text", "").strip()
            if text and len(text) > 5:
                prompts.append(text)

    if not prompts:
        return _FALLBACK

    combined = "\n---\n".join(prompts)
    if len(combined) > _MAX_PROMPT_CHARS:
        combined = combined[:_MAX_PROMPT_CHARS] + "\n... (truncated)"

    prompt = f"""Below are all the prompts a developer sent to Claude Code during their work sessions. Read them and write a brief project context summary (3-5 sentences).

Cover:
1. What project or task were they working on?
2. What were they trying to accomplish?
3. What tools, systems, or data sources did they interact with?
4. What did they achieve or produce?

Write in third person past tense ("The developer was building...", "They used...").
Be specific — name the actual project, systems, and outputs. No generic platitudes.
Start directly with the summary — do not include any preamble or introduction such as "Here is the project context:" or "Based on the prompts...".

---

Developer prompts:

{combined}"""

    result = call_claude_writer(prompt, model=model)
    if result:
        result = _strip_preamble(result)
    return result or _FALLBACK


def _strip_preamble(text: str) -> str:
    """Remove a leading preamble line if Claude added one despite instructions."""
    lines = text.strip().splitlines()
    if not lines:
        return text
    first = lines[0].lower()
    preamble_signals = ("here is", "here's", "based on", "looking at", "below is", "the following")
    if any(first.startswith(s) for s in preamble_signals) and first.endswith(":"):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines)
