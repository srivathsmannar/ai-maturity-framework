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

---

Developer prompts:

{combined}"""

    result = call_claude_writer(prompt, model=model)
    return result or _FALLBACK
