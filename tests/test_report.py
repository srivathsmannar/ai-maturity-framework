"""Tests for the report generator (T3 Step 4)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from ai_maturity.report import generate_report
from ai_maturity.taxonomy import SUB_DIMENSIONS, dimension_for

SAMPLE_SCORED = [
    {"sub_dimension": "ai_tool_adoption", "dimension": "capability", "level": 2,
     "level_label": "Integrated", "confidence": "high", "record_count": 5,
     "reasoning": "Developer selects tools deliberately.", "evidence": ["uses sql-query skill"],
     "matched_signals": ["tool selection"], "team": "platform", "user": "alice",
     "id": "out-001", "category": "prompts", "input_id": "in-001", "assessed_at": "2026-04-28T10:00:00Z"},
]

SAMPLE_INPUT = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "use the sql-query skill for this"}},
    {"id": "in-002", "category": "prompts", "sub_dimension": "ticketing_planning",
     "data": {"prompt_text": "I'm working on T260669092 — CI demand pipeline"}},
]


def _fill_all_12(scored):
    existing = {r["sub_dimension"] for r in scored}
    full = list(scored)
    for sd in SUB_DIMENSIONS:
        if sd not in existing:
            full.append({"sub_dimension": sd, "dimension": dimension_for(sd), "level": 1,
                "level_label": "Assisted", "confidence": "low", "record_count": 0,
                "reasoning": "No evidence.", "evidence": [], "matched_signals": [],
                "team": "platform", "user": "alice", "id": f"out-{sd}",
                "category": "prompts", "input_id": "none", "assessed_at": "2026-04-28T10:00:00Z"})
    return full


def test_report_has_project_context_section(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="Built a CI pipeline."):
        with patch("ai_maturity.report.extract_project_context", return_value="Developer built a CI demand pipeline."):
            md = generate_report(scored_f, input_f)
    assert "CI demand pipeline" in md
    assert "Overall Maturity" in md


def test_report_no_separate_exemplar_sections(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative text."):
        with patch("ai_maturity.report.extract_project_context", return_value="Context."):
            md = generate_report(scored_f, input_f)
    assert "**Exemplar evidence:**" not in md


def test_report_has_score_matrix(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative."):
        with patch("ai_maturity.report.extract_project_context", return_value="Context."):
            md = generate_report(scored_f, input_f)
    assert "AI Tool Adoption" in md
    assert "| Dimension |" in md or "Sub-Dimension" in md


def test_report_has_all_4_dimensions(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="Narrative."):
        with patch("ai_maturity.report.extract_project_context", return_value="Context."):
            md = generate_report(scored_f, input_f)
    assert "Capability" in md
    assert "Integration" in md
    assert "Governance" in md
    assert "Execution Ownership" in md


def test_report_has_recommendations(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="Good narrative. Improve X."):
        with patch("ai_maturity.report.extract_project_context", return_value="Context."):
            md = generate_report(scored_f, input_f)
    assert "Recommendation" in md
