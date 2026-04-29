from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List


def load_exemplars(
    input_path: Path,
    max_per_subdim: int = 3,
) -> Dict[str, List[dict]]:
    by_sd: dict[str, list[dict]] = defaultdict(list)

    with open(input_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            sd = record.get("sub_dimension", "")
            if sd:
                by_sd[sd].append(record)

    result = {}
    for sd, records in by_sd.items():
        prompts = [r for r in records if r.get("category") == "prompts"]
        others = [r for r in records if r.get("category") != "prompts"]
        prioritized = prompts + others
        result[sd] = prioritized[:max_per_subdim]

    return result
