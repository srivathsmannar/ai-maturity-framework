from __future__ import annotations

from pathlib import Path

from ai_maturity.ground_truth import load_ground_truth
from ai_maturity.taxonomy import SUB_DIMENSIONS

GROUND_TRUTH_PATH = Path(__file__).parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"


def test_loads_all_sub_dimensions():
    gt = load_ground_truth(GROUND_TRUTH_PATH)
    for sd in SUB_DIMENSIONS:
        assert sd in gt, f"Missing ground truth for {sd}"


def test_each_section_has_levels():
    gt = load_ground_truth(GROUND_TRUTH_PATH)
    for sd, text in gt.items():
        assert "L1" in text or "Assisted" in text, f"{sd} missing L1"
        assert "L4" in text or "Autonomous" in text, f"{sd} missing L4"


def test_section_is_nonempty():
    gt = load_ground_truth(GROUND_TRUTH_PATH)
    for sd, text in gt.items():
        assert len(text) > 100, f"{sd} section too short ({len(text)} chars)"


def test_ai_tool_adoption_content():
    gt = load_ground_truth(GROUND_TRUTH_PATH)
    section = gt["ai_tool_adoption"]
    assert "Ad-hoc" in section
    assert "Deliberate tool choice" in section or "Integrated" in section
