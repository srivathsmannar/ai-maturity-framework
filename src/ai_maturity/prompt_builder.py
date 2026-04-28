"""Prompt builder for AI Maturity grading pipeline (T2 Step 2).

Constructs the grading prompt for a single sub-dimension by combining the
ground truth rubric with the developer's evidence records.
"""
from __future__ import annotations

import json


def _format_record(record: dict) -> str:
    """Format a single evidence record into a readable one-line summary."""
    category = record.get("category", "unknown")
    data = record.get("data", {})

    # Prompt record
    if "prompt_text" in data:
        return f"[{category}] Prompt: {data['prompt_text']}"

    # Tool-based records
    if "tool_name" in data:
        tool_name = data["tool_name"]

        # Agent spawn: has agent_type alongside tool_name
        if "agent_type" in data:
            agent_desc = data.get("agent_description", "")
            return (
                f"[{category}] Agent spawn: type={data['agent_type']}, "
                f'description="{agent_desc}"'
            )

        inp = data.get("input", {})
        if isinstance(inp, dict):
            # Skill invocation
            if "skill" in inp:
                return f"[{category}] Skill: {inp['skill']}"

            # Command invocation
            if "command" in inp:
                cmd = inp["command"][:200]
                return f"[{category}] {tool_name}: {cmd}"

            # File path invocation
            if "file_path" in inp:
                return f"[{category}] {tool_name}: {inp['file_path']}"

        # Fallback for tool records without recognised input shape
        data_str = json.dumps(data)[:200]
        return f"[{category}] {data_str}"

    # Session config / system record with subtype
    if "subtype" in data:
        hook_count = len(data.get("hooks", []))
        return f"[{category}] System: {data['subtype']}, hooks={hook_count}"

    # Ultimate fallback
    data_str = json.dumps(data)[:200]
    return f"[{category}] {data_str}"


def _truncate_evidence(records: list[dict], max_chars: int = 30000) -> str:
    """Format all records into a single evidence string, truncating if needed."""
    lines: list[str] = []
    total = 0
    for rec in records:
        line = _format_record(rec)
        if total + len(line) + 1 > max_chars:
            lines.append("... (evidence truncated)")
            break
        lines.append(line)
        total += len(line) + 1  # +1 for newline
    return "\n".join(lines)


def build_grading_prompt(
    sub_dimension: str,
    ground_truth_section: str,
    records: list[dict],
) -> str:
    """Build the full grading prompt for a single sub-dimension.

    Parameters
    ----------
    sub_dimension:
        The sub-dimension key, e.g. ``"ai_tool_adoption"``.
    ground_truth_section:
        The rubric text (markdown) for this sub-dimension.
    records:
        Evidence records routed to this sub-dimension.

    Returns
    -------
    str
        The assembled prompt ready for LLM grading.
    """
    record_count = len(records)

    if record_count == 0:
        evidence_block = (
            "No records were routed to this sub-dimension.\n"
            "Assign maturity level L1 with low confidence."
        )
    else:
        evidence_block = _truncate_evidence(records)

    # Determine confidence guidance
    if record_count >= 3:
        confidence_hint = "high (3+ records available)"
    elif record_count >= 1:
        confidence_hint = "medium (1-2 records available)"
    else:
        confidence_hint = "low (0 records available)"

    prompt = f"""\
You are an expert AI-maturity grader. Your task is to assess a developer's \
maturity level for the sub-dimension **{sub_dimension}**.

## Instructions

1. Read the **Rubric** below carefully. It defines the maturity levels (L1-L4) \
for this sub-dimension.
2. Read the **Evidence** section. These are actual records from the developer's \
coding session.
3. Grade the developer's **average** behavior, not their peak. A single \
outstanding action does not justify a higher level if most behavior is lower.
4. Assign a **confidence** rating based on evidence volume: {confidence_hint}.
5. List the specific evidence items and matched signals that support your grade.
6. Explain your reasoning in 1-2 sentences.

## Rubric

{ground_truth_section}

## Evidence ({record_count} record(s))

{evidence_block}

## Required Output

Return a JSON object with the following fields:
- "sub_dimension": "{sub_dimension}"
- "level": the maturity level you assign (e.g. "L1", "L2", "L3", or "L4")
- "confidence": "high", "medium", or "low"
- "evidence": list of evidence items that support your grade
- "matched_signals": list of rubric signals matched by the evidence
- "reasoning": 1-2 sentence explanation of your grade
"""
    return prompt
