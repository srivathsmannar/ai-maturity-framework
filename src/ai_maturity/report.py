"""Report generator that assembles the full Markdown assessment report (T3 Step 4).

Reads scored output and input JSONL files, calls Claude for narratives
with project context and exemplar prompts woven in, and produces a
compact Markdown report.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

from ai_maturity.claude_writer import call_claude_writer
from ai_maturity.context_extractor import extract_project_context
from ai_maturity.exemplars import load_exemplars
from ai_maturity.narrative_prompts import build_dimension_prompt, build_executive_prompt
from ai_maturity.scorer import compute_scores
from ai_maturity.taxonomy import DIMENSIONS, LEVELS

logger = logging.getLogger(__name__)

_DIM_DISPLAY = {
    "capability": "Capability",
    "integration": "Integration",
    "governance": "Governance",
    "execution_ownership": "Execution Ownership",
}

_PLACEHOLDER_EXEC = "Assessment complete. See dimension sections for details."
_PLACEHOLDER_DIM = "See sub-dimension results below for details. Consider focusing on the lowest-scoring area."


def generate_report(
    scored_path: Path,
    input_path: Path,
    model: str = "sonnet",
) -> str:
    """Generate the full Markdown assessment report.

    Parameters
    ----------
    scored_path:
        Path to the scored JSONL file (grading output with levels/reasoning).
    input_path:
        Path to the input JSONL file (raw records for exemplars).
    model:
        Claude model to use for narrative generation.

    Returns
    -------
    str
        The complete Markdown report.
    """
    scored = _load_jsonl(scored_path)
    meta = _extract_meta(scored)
    scores = compute_scores(scored)
    by_dim = _group_by_dimension(scored)

    # Extract project context from input prompts
    project_context = extract_project_context(input_path, model)

    # Load exemplars keyed by sub-dimension
    exemplars = load_exemplars(input_path, max_per_subdim=3)

    sections: list[str] = []

    # Header
    sections.append(_render_header(meta, scores))

    # Project Context section
    sections.append(_render_project_context(project_context))

    # Executive summary
    exec_prompt = build_executive_prompt(scores, meta["user"], meta["team"], project_context)
    exec_narrative = call_claude_writer(exec_prompt, model) or _PLACEHOLDER_EXEC
    sections.append(_render_executive_summary(scores, exec_narrative))

    # Dimension sections
    dim_narratives: dict[str, str] = {}
    for dim in DIMENSIONS:
        sub_results = by_dim.get(dim, [])
        dim_data = _build_dim_data(dim, sub_results, scores)

        # Collect exemplar prompt_text strings for this dimension's sub-dimensions
        exemplar_texts = _collect_exemplar_texts(dim, exemplars)

        dim_prompt = build_dimension_prompt(dim_data, project_context, exemplar_texts)
        narrative = call_claude_writer(dim_prompt, model) or _PLACEHOLDER_DIM
        dim_narratives[dim] = narrative
        sections.append(_render_dimension_section(dim, dim_data, narrative))

    # Recommendations
    sections.append(_render_recommendations(dim_narratives))

    return "\n".join(sections)


def _load_jsonl(path: Path) -> list[dict]:
    """Read a JSONL file and return a list of dicts."""
    records: list[dict] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def _extract_meta(scored: list[dict]) -> dict:
    """Extract user, team, and assessed_at from the first scored record."""
    if not scored:
        return {"user": "Unknown", "team": "Unknown", "assessed_at": str(date.today())}
    first = scored[0]
    return {
        "user": first.get("user", "Unknown"),
        "team": first.get("team", "Unknown"),
        "assessed_at": first.get("assessed_at", str(date.today())),
    }


def _group_by_dimension(scored: list[dict]) -> dict[str, list[dict]]:
    """Group scored records by their dimension field."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in scored:
        dim = record.get("dimension", "")
        if dim:
            groups[dim].append(record)
    return dict(groups)


def _build_dim_data(
    dim: str,
    sub_results: list[dict],
    scores: dict,
) -> dict:
    """Assemble data dict for a dimension narrative prompt."""
    dim_scores = scores["dimensions"].get(dim, {"average": 1.0, "sub_dimensions": {}})
    return {
        "dimension": dim,
        "average": dim_scores["average"],
        "sub_dimensions": [
            {
                "sub_dimension": r["sub_dimension"],
                "level": r["level"],
                "level_label": r.get("level_label", LEVELS.get(r["level"], "Assisted")),
                "confidence": r.get("confidence", "low"),
                "reasoning": r.get("reasoning", ""),
                "evidence": r.get("evidence", []),
            }
            for r in sub_results
        ],
    }


def _collect_exemplar_texts(dim: str, exemplars: dict[str, list[dict]]) -> list[str]:
    """Collect prompt_text strings for all sub-dimensions in a dimension."""
    texts: list[str] = []
    for sd in DIMENSIONS.get(dim, []):
        for rec in exemplars.get(sd, []):
            pt = rec.get("data", {}).get("prompt_text", "").strip()
            if pt:
                texts.append(pt)
    return texts


def _level_label(score: float) -> str:
    """Convert a numeric score to a level label using thresholds."""
    if score < 1.5:
        return "L1"
    elif score < 2.5:
        return "L2"
    elif score < 3.5:
        return "L3"
    else:
        return "L4"


def _level_int(score: float) -> int:
    """Convert a numeric score to a level integer."""
    if score < 1.5:
        return 1
    elif score < 2.5:
        return 2
    elif score < 3.5:
        return 3
    else:
        return 4


def _render_header(meta: dict, scores: dict) -> str:
    """Render the report header with name, team, date."""
    assessed = meta["assessed_at"]
    if "T" in assessed:
        assessed = assessed.split("T")[0]
    return (
        f"# AI Maturity Assessment Report\n\n"
        f"**Name**: {meta['user']} | **Team**: {meta['team']} | **Date**: {assessed}\n\n"
        f"---\n"
    )


def _render_project_context(project_context: str) -> str:
    """Render the project context section."""
    return f"\n## Project Context\n\n{project_context}\n"


def _render_executive_summary(scores: dict, narrative: str) -> str:
    """Render the executive summary section with score table and narrative."""
    overall = scores["overall_score"]
    label = scores["maturity_label"]

    lines = [
        f"\n## Executive Summary\n",
        f"**Overall Score: {overall} — {label}**\n",
        "| Dimension | Score | Level |",
        "|-----------|-------|-------|",
    ]

    for dim in DIMENSIONS:
        dim_info = scores["dimensions"].get(dim, {"average": 1.0})
        avg = dim_info["average"]
        lvl = _level_label(avg)
        display = _DIM_DISPLAY.get(dim, dim)
        lines.append(f"| {display} | {avg} | {lvl} |")

    lines.append(f"\n{narrative}\n")
    lines.append("---\n")
    return "\n".join(lines)


def _render_dimension_section(dim: str, dim_data: dict, narrative: str) -> str:
    """Render a compact dimension section with narrative and one-liner sub-dimension scores."""
    display = _DIM_DISPLAY.get(dim, dim)
    avg = dim_data["average"]
    lvl_str = _level_label(avg)
    lvl_full = LEVELS.get(_level_int(avg), "Assisted")

    sd_parts = []
    for sd in dim_data["sub_dimensions"]:
        sd_display = sd["sub_dimension"].replace("_", " ").title()
        sd_parts.append(f"{sd_display}: L{sd['level']}")
    compact_line = " | ".join(sd_parts)

    return f"""
---

## {display} ({lvl_str}: {lvl_full})

{narrative}

{compact_line}
"""


def _render_recommendations(dim_narratives: dict[str, str]) -> str:
    """Render the recommendations section by extracting the last sentence from each narrative."""
    lines = ["\n## Recommendations\n"]
    idx = 1
    for dim in DIMENSIONS:
        display = _DIM_DISPLAY.get(dim, dim)
        narrative = dim_narratives.get(dim, _PLACEHOLDER_DIM)
        last_sentence = _extract_last_sentence(narrative)
        lines.append(f"{idx}. **{display}**: {last_sentence}")
        idx += 1
    lines.append("")
    return "\n".join(lines)


def _extract_last_sentence(text: str) -> str:
    """Extract the last sentence from a text block."""
    text = text.strip()
    if not text:
        return ""

    # Split on sentence-ending punctuation followed by space or end
    sentences: list[str] = []
    current = []
    for i, ch in enumerate(text):
        current.append(ch)
        if ch in ".!?" and (i + 1 >= len(text) or text[i + 1] == " " or text[i + 1] == "\n"):
            sentences.append("".join(current).strip())
            current = []
    if current:
        remaining = "".join(current).strip()
        if remaining:
            sentences.append(remaining)

    if sentences:
        return sentences[-1]
    return text
