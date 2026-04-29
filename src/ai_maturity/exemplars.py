from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

_NOISE_PATTERNS = [
    re.compile(r"<task-notification>", re.I),
    re.compile(r"<command-name>", re.I),
    re.compile(r"\[Request interrupted", re.I),
    re.compile(r"<local-command-", re.I),
    re.compile(r"<system-reminder>", re.I),
]


def is_noise(record: dict) -> bool:
    data = record.get("data", {})
    prompt_text = data.get("prompt_text", "")
    if prompt_text:
        for pattern in _NOISE_PATTERNS:
            if pattern.search(prompt_text):
                return True
        if len(prompt_text.strip()) < 5:
            return True
    return False


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
        clean = [r for r in records if not is_noise(r)]
        prompts = [r for r in clean if r.get("category") == "prompts"]
        others = [r for r in clean if r.get("category") != "prompts"]
        prioritized = prompts + others
        result[sd] = prioritized[:max_per_subdim]

    return result
