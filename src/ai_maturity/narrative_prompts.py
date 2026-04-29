from __future__ import annotations

from typing import Dict


def build_dimension_prompt(dim_data: dict) -> str:
    dim = dim_data["dimension"]
    avg = dim_data["average"]
    subs = dim_data["sub_dimensions"]

    sub_details = []
    for sd in subs:
        sub_details.append(
            f"- {sd['sub_dimension']}: L{sd['level']} ({sd['level_label']}), "
            f"confidence={sd['confidence']}\n"
            f"  Reasoning: {sd['reasoning']}\n"
            f"  Evidence: {'; '.join(str(e) for e in sd.get('evidence', []))}"
        )

    return f"""You are writing a section of an AI Maturity Assessment report for the "{dim}" dimension.

Dimension average score: {avg}

Sub-dimension results:
{chr(10).join(sub_details)}

Write a 2-3 sentence narrative that:
1. Summarizes the developer's maturity in this dimension
2. Highlights the strongest sub-dimension and why
3. Identifies the biggest gap and gives one specific, actionable recommendation

Write in second person ("You demonstrate...", "Your gap is...").
Be concise and direct. No headers, no bullet points — just prose."""


def build_executive_prompt(
    scores: Dict,
    user: str,
    team: str,
) -> str:
    dims = scores["dimensions"]
    dim_lines = "\n".join(
        f"- {dim}: {info['average']}"
        for dim, info in dims.items()
    )

    return f"""You are writing the executive summary of an AI Maturity Assessment report.

Developer: {user}
Team: {team}
Overall score: {scores['overall_score']} — {scores['maturity_label']}

Dimension scores:
{dim_lines}

Write a 3-4 sentence executive summary that:
1. States the overall maturity level and what it means practically
2. Highlights the strongest dimension
3. Identifies the biggest gap
4. Gives one high-level recommendation

Write in second person ("You are currently at...", "Your strongest area...").
Be concise and direct. No headers — just prose."""
