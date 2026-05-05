from __future__ import annotations

import re
from pathlib import Path
from typing import Dict

_HEADING_MAP = {
    "1.1 AI Tool Adoption": "ai_tool_adoption",
    "1.2 Prompt & Context Engineering": "prompt_context_engineering",
    "1.3 Agent Configuration": "agent_configuration",
    "2.1 CI/CD Integration": "cicd_integration",
    "2.2 Ticketing & Planning": "ticketing_planning",
    "2.3 Cross-System Connectivity": "cross_system_connectivity",
    "3.1 Quality Controls": "quality_controls",
    "3.2 Security & Compliance": "security_compliance",
    "3.3 Measurement & KPIs": "measurement_kpis",
    "4.1 Ways of Working": "ways_of_working",
    "4.2 Accountability & Ownership": "accountability_ownership",
    "4.3 Scalability & Knowledge Transfer": "scalability_knowledge_transfer",
}

# Matches lines like "### 1.1 AI Tool Adoption"
_SECTION_RE = re.compile(r"^###\s+(\d+\.\d+\s+.+)$", re.MULTILINE)

# Matches the sentinel heading where parsing should stop
_STOP_RE = re.compile(r"^##\s+How to Use This Ground Truth", re.MULTILINE)


def load_ground_truth(path: Path) -> Dict[str, str]:
    """Parse the ground-truth markdown into per-sub-dimension sections.

    Returns a dict mapping sub-dimension identifiers (e.g. ``"ai_tool_adoption"``)
    to the raw markdown text of their rubric section.
    """
    text = path.read_text(encoding="utf-8")

    # Truncate at the "How to Use" sentinel so summary/appendix content
    # is never included in any section.
    stop = _STOP_RE.search(text)
    if stop:
        text = text[: stop.start()]

    # Find all ### X.Y headings and split the text at those boundaries.
    matches = list(_SECTION_RE.finditer(text))

    result: Dict[str, str] = {}
    for i, match in enumerate(matches):
        heading = match.group(1).strip()
        sd_id = _HEADING_MAP.get(heading)
        if sd_id is None:
            continue  # heading not in our map — skip

        # Section body runs from the end of this heading line to the start
        # of the next heading (or end of text).
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        result[sd_id] = body

    return result
