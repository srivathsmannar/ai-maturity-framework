from __future__ import annotations

from typing import Optional
from ai_maturity.classifier import classify_record


def _extract_prompt_text(message: dict) -> str:
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n".join(parts)
    return ""


def _extract_tool_use_block(content: list) -> Optional[dict]:
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            name = block.get("name", "")
            if name not in ("ToolSearch", "AskUserQuestion"):
                return block
    return None


def extract_record(record: dict) -> Optional[dict]:
    record_type = classify_record(record)
    if record_type == "skip":
        return None

    base = {
        "record_type": record_type,
        "timestamp": record.get("timestamp", ""),
        "session_id": record.get("sessionId", ""),
    }

    if record_type == "prompt":
        msg = record.get("message", {})
        base["data"] = {"prompt_text": _extract_prompt_text(msg)}
        return base

    if record_type in ("tool_call", "agent_spawn", "skill_invocation"):
        msg = record.get("message", {})
        content = msg.get("content", []) if isinstance(msg, dict) else []
        block = _extract_tool_use_block(content) if isinstance(content, list) else None
        if block is None:
            return None

        name = block.get("name", "")
        inp = block.get("input", {})

        if record_type == "agent_spawn":
            # Shape to match JSONL_FORMAT agent_delegation schema
            base["data"] = {
                "tool_name": name,
                "agent_type": inp.get("subagent_type", "general-purpose"),
                "agent_description": inp.get("description", ""),
                "agent_prompt_summary": str(inp.get("prompt", ""))[:200],
                "parallel_agents": None,  # determined at pipeline level
                "input": inp,
            }
        elif record_type == "skill_invocation":
            base["data"] = {
                "tool_name": name,
                "input": inp,
            }
        else:
            # tool_call
            base["data"] = {
                "tool_name": name,
                "input": inp,
            }
        return base

    if record_type == "session_config":
        base["data"] = {
            "subtype": record.get("subtype", ""),
            "hook_count": record.get("hookCount"),
            "hooks": record.get("hookInfos", []),
            "content": record.get("content", ""),
        }
        return base

    return None
