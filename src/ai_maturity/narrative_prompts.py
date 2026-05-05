from __future__ import annotations

from typing import Dict, List, Optional


def build_dimension_prompt(
    dim_data: dict,
    project_context: str = "",
    exemplar_texts: Optional[List[str]] = None,
) -> str:
    dim = dim_data["dimension"]
    avg = dim_data["average"]
    subs = dim_data["sub_dimensions"]

    sub_details = []
    for sd in subs:
        sub_details.append(
            f"- {sd['sub_dimension']}: L{sd['level']} ({sd['level_label']}), "
            f"confidence={sd['confidence']}\n"
            f"  Reasoning: {sd['reasoning']}"
        )

    texts = exemplar_texts or []
    exemplar_block = "\n".join(f'- "{t}"' for t in texts[:10]) if texts else "(no exemplar prompts available)"

    context_block = f"## Project Context\n{project_context}\n" if project_context else ""

    return f"""You are writing a section of an AI Maturity Assessment report for the "{dim}" dimension.

{context_block}## Scores
Dimension average: {avg}

{chr(10).join(sub_details)}

## Developer's Actual Prompts/Actions (for this dimension)
{exemplar_block}

## Writing Instructions

Write 2-3 short paragraphs (separated by blank lines) that:

Paragraph 1: Connect the developer's maturity to what they were actually building. Weave in 1-2 direct quotes from their prompts as evidence (use quotation marks). Don't just list scores.

Paragraph 2: Explain WHY their levels are what they are given the project context. Was a low score because they didn't need that capability for this project, or because they missed an opportunity?

Paragraph 3: Give one specific, actionable recommendation tied to their actual project work.

Write in second person ("You demonstrated...", "When you asked...").
Conversational, direct, human tone. No bullet points, no headers — just prose paragraphs.
Do NOT just restate the scores — interpret them in context."""


def build_executive_prompt(
    scores: Dict,
    user: str,
    team: str,
    project_context: str = "",
) -> str:
    dims = scores["dimensions"]
    dim_lines = "\n".join(
        f"- {dim}: {info['average']}"
        for dim, info in dims.items()
    )

    context_block = f"## Project Context\n{project_context}\n" if project_context else ""

    return f"""You are writing the executive summary of an AI Maturity Assessment report.

{context_block}## Scores
Developer: {user}
Team: {team}
Overall score: {scores['overall_score']} — {scores['maturity_label']}

Dimension scores:
{dim_lines}

## Writing Instructions

Write a 3-4 sentence executive summary that:
1. Briefly describes what the developer was working on (from the project context)
2. States their overall maturity level and what it means for their workflow
3. Highlights what they did well with AI and where the biggest gap is
4. Gives one high-level recommendation tied to their actual work

Write in second person ("You used Claude to...", "Your strongest area...").
Conversational, direct, human tone. No headers — just prose.
Do NOT just restate the numbers — interpret them in context of what they were building."""
