from __future__ import annotations

from typing import Dict, List

from ai_maturity.taxonomy import DIMENSIONS


def compute_scores(results: List[dict]) -> Dict:
    by_sd = {r["sub_dimension"]: r["level"] for r in results}

    dimensions = {}
    for dim, sds in DIMENSIONS.items():
        sd_scores = {sd: by_sd.get(sd, 1) for sd in sds}
        avg = sum(sd_scores.values()) / len(sd_scores)
        dimensions[dim] = {
            "average": round(avg, 2),
            "sub_dimensions": sd_scores,
        }

    all_sds = [sd for sds in DIMENSIONS.values() for sd in sds]
    all_levels = [by_sd.get(sd, 1) for sd in all_sds]
    overall = sum(all_levels) / len(all_levels)

    if overall < 1.5:
        label = "L1: Assisted"
    elif overall < 2.5:
        label = "L2: Integrated"
    elif overall < 3.5:
        label = "L3: Agentic"
    else:
        label = "L4: Autonomous"

    return {
        "overall_score": round(overall, 2),
        "maturity_label": label,
        "dimensions": dimensions,
    }
