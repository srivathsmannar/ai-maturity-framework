"""Grader module for AI Maturity Framework (T2 Step 4).

Orchestrates grading for all 12 sub-dimensions by loading evidence,
building prompts, and calling the Claude LLM judge.
"""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from ai_maturity.claude_judge import call_claude_judge
from ai_maturity.ground_truth import load_ground_truth
from ai_maturity.prompt_builder import build_grading_prompt
from ai_maturity.taxonomy import LEVELS, SUB_DIMENSIONS, dimension_for

logger = logging.getLogger(__name__)

_FALLBACK_RESPONSE = {
    "level": 1,
    "confidence": "low",
    "evidence": [],
    "matched_signals": [],
    "reasoning": "No response from grading judge or no evidence available.",
}


def grade_session(
    input_path: Path,
    ground_truth_path: Path,
    model: str = "sonnet",
) -> list[dict]:
    """Grade a developer session across all 12 sub-dimensions.

    Parameters
    ----------
    input_path:
        Path to a JSONL file of evidence records.
    ground_truth_path:
        Path to the ground-truth markdown rubric.
    model:
        Claude model identifier to pass to the judge.

    Returns
    -------
    list[dict]
        Exactly 12 result dicts, one per sub-dimension.
    """
    # 1. Load ground truth
    ground_truth = load_ground_truth(ground_truth_path)

    # 2. Read all records from JSONL, group by sub_dimension
    records_by_sd: dict[str, list[dict]] = defaultdict(list)
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            sd = record.get("sub_dimension", "")
            records_by_sd[sd].append(record)

    results: list[dict] = []
    assessed_at = datetime.now(timezone.utc).isoformat()

    # 3. Iterate over all 12 canonical sub-dimensions
    for sd in SUB_DIMENSIONS:
        records = records_by_sd.get(sd, [])
        gt_section = ground_truth.get(sd, "")

        # Build grading prompt
        prompt = build_grading_prompt(sd, gt_section, records)

        # Call the Claude judge
        judge_response = call_claude_judge(prompt, model=model)

        # Fall back if judge returns None
        if judge_response is None:
            judge_response = dict(_FALLBACK_RESPONSE)

        # Validate level is 1-4, default to 1 if not
        level = judge_response.get("level", 1)
        if not isinstance(level, int) or level not in (1, 2, 3, 4):
            level = 1

        # Extract info from first record (if any)
        first_record = records[0] if records else None
        top_input_id = first_record["id"] if first_record else "none"
        category = first_record.get("category", "prompts") if first_record else "prompts"
        team = first_record.get("team", "") if first_record else ""
        user = first_record.get("user", "") if first_record else ""

        # Build output record
        result = {
            "id": f"out-{top_input_id}-{sd}",
            "category": category,
            "input_id": top_input_id,
            "sub_dimension": sd,
            "dimension": dimension_for(sd),
            "team": team,
            "user": user,
            "assessed_at": assessed_at,
            "level": level,
            "level_label": LEVELS[level],
            "confidence": judge_response.get("confidence", "low"),
            "evidence": judge_response.get("evidence", []),
            "matched_signals": judge_response.get("matched_signals", []),
            "reasoning": judge_response.get("reasoning", ""),
            "record_count": len(records),
        }
        results.append(result)

    return results
