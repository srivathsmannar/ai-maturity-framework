from ai_maturity.taxonomy import DIMENSIONS, SUB_DIMENSIONS, LEVELS, dimension_for


def test_dimensions_count():
    assert len(DIMENSIONS) == 4


def test_sub_dimensions_count():
    assert len(SUB_DIMENSIONS) == 12


def test_levels_count():
    assert len(LEVELS) == 4


def test_dimension_for_valid():
    assert dimension_for("ai_tool_adoption") == "capability"
    assert dimension_for("cicd_integration") == "integration"
    assert dimension_for("quality_controls") == "governance"
    assert dimension_for("ways_of_working") == "execution_ownership"


def test_dimension_for_invalid():
    assert dimension_for("nonexistent") is None


def test_all_sub_dimensions_have_parent():
    for sd in SUB_DIMENSIONS:
        assert dimension_for(sd) is not None, f"{sd} has no parent dimension"
