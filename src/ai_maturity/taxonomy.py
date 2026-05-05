from __future__ import annotations

from typing import Optional

DIMENSIONS = {
    "capability": ["ai_tool_adoption", "prompt_context_engineering", "agent_configuration"],
    "integration": ["cicd_integration", "ticketing_planning", "cross_system_connectivity"],
    "governance": ["quality_controls", "security_compliance", "measurement_kpis"],
    "execution_ownership": ["ways_of_working", "accountability_ownership", "scalability_knowledge_transfer"],
}

SUB_DIMENSIONS = [sd for sds in DIMENSIONS.values() for sd in sds]

LEVELS = {
    1: "Assisted",
    2: "Integrated",
    3: "Agentic",
    4: "Autonomous",
}

_SD_TO_DIM = {sd: dim for dim, sds in DIMENSIONS.items() for sd in sds}


def dimension_for(sub_dimension: str) -> Optional[str]:
    return _SD_TO_DIM.get(sub_dimension)
