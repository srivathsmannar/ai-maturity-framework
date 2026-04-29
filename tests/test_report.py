"""Tests for the report generator (T3 Step 4)."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from ai_maturity.report import generate_report

SAMPLE_SCORED = [
    {"sub_dimension": "ai_tool_adoption", "dimension": "capability", "level": 2,
     "level_label": "Integrated", "confidence": "high", "record_count": 5,
     "reasoning": "Developer selects tools deliberately.", "evidence": ["uses presto-query"],
     "matched_signals": ["tool selection"], "team": "platform", "user": "alice",
     "id": "out-001", "category": "prompts", "input_id": "in-001", "assessed_at": "2026-04-28T10:00:00Z"},
    {"sub_dimension": "prompt_context_engineering", "dimension": "capability", "level": 1,
     "level_label": "Assisted", "confidence": "medium", "record_count": 1,
     "reasoning": "Asks basic context questions.", "evidence": ["how do i add context?"],
     "matched_signals": [], "team": "platform", "user": "alice",
     "id": "out-002", "category": "prompts", "input_id": "in-002", "assessed_at": "2026-04-28T10:00:00Z"},
    {"sub_dimension": "agent_configuration", "dimension": "capability", "level": 2,
     "level_label": "Integrated", "confidence": "high", "record_count": 9,
     "reasoning": "Hooks and skills configured.", "evidence": ["Skill: executing-plans"],
     "matched_signals": ["skill usage"], "team": "platform", "user": "alice",
     "id": "out-003", "category": "tool_usage", "input_id": "in-003", "assessed_at": "2026-04-28T10:00:00Z"},
]

SAMPLE_INPUT = [
    {"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption",
     "data": {"prompt_text": "use the presto-query skill"}},
    {"id": "in-002", "category": "prompts", "sub_dimension": "prompt_context_engineering",
     "data": {"prompt_text": "how do i add files as context?"}},
    {"id": "in-003", "category": "tool_usage", "sub_dimension": "agent_configuration",
     "data": {"tool_name": "Skill", "input": {"skill": "10x-engineer:executing-plans"}}},
]


def _fill_all_12(scored):
    from ai_maturity.taxonomy import SUB_DIMENSIONS, dimension_for
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


def test_generate_report_returns_string(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="A solid narrative. Focus on context engineering."):
        md = generate_report(scored_f, input_f)
    assert isinstance(md, str)
    assert len(md) > 200


def test_report_has_executive_summary(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="A solid narrative. Focus on context engineering."):
        md = generate_report(scored_f, input_f)
    assert "Executive Summary" in md
    assert "Overall" in md


def test_report_has_all_4_dimensions(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="A solid narrative. Focus on context engineering."):
        md = generate_report(scored_f, input_f)
    assert "Capability" in md
    assert "Integration" in md
    assert "Governance" in md
    assert "Execution Ownership" in md


def test_report_has_exemplars(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="A solid narrative. Focus on context engineering."):
        md = generate_report(scored_f, input_f)
    assert "presto-query" in md
    assert "how do i add files" in md


def test_report_has_recommendations(tmp_path):
    scored_f = tmp_path / "scored.jsonl"
    scored_f.write_text("\n".join(json.dumps(r) for r in _fill_all_12(SAMPLE_SCORED)))
    input_f = tmp_path / "input.jsonl"
    input_f.write_text("\n".join(json.dumps(r) for r in SAMPLE_INPUT))
    with patch("ai_maturity.report.call_claude_writer", return_value="A solid narrative. Focus on context engineering."):
        md = generate_report(scored_f, input_f)
    assert "Recommendation" in md
