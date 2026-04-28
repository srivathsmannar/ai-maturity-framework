"""Classify raw Claude Code session JSONL records into semantic types."""

from __future__ import annotations

from typing import Any, Dict

# Record-level types that are always skipped
_SKIP_TYPES = frozenset({
    "progress",
    "file-history-snapshot",
    "queue-operation",
    "permission-mode",
    "last-prompt",
})

# System subtypes that map to session_config; all others are skipped
_SESSION_CONFIG_SUBTYPES = frozenset({"stop_hook_summary", "local_command"})

# Assistant tool names that are plumbing and should be skipped
_PLUMBING_TOOLS = frozenset({"ToolSearch", "AskUserQuestion"})


def classify_record(record: Dict[str, Any]) -> str:
    """Return the semantic type of a raw JSONL *record*.

    Possible return values:
        ``"prompt"`` | ``"tool_call"`` | ``"agent_spawn"``
        | ``"skill_invocation"`` | ``"session_config"`` | ``"skip"``
    """
    rtype = record.get("type")

    # ------------------------------------------------------------------
    # 1. Unconditional skip types
    # ------------------------------------------------------------------
    if rtype in _SKIP_TYPES:
        return "skip"

    # ------------------------------------------------------------------
    # 2. System records
    # ------------------------------------------------------------------
    if rtype == "system":
        subtype = record.get("subtype")
        if subtype in _SESSION_CONFIG_SUBTYPES:
            return "session_config"
        return "skip"

    # ------------------------------------------------------------------
    # 3. User records
    # ------------------------------------------------------------------
    if rtype == "user":
        if record.get("isMeta"):
            return "skip"
        if record.get("toolUseResult") or record.get("sourceToolUseID"):
            return "skip"
        return "prompt"

    # ------------------------------------------------------------------
    # 4. Assistant records — scan for first tool_use block
    # ------------------------------------------------------------------
    if rtype == "assistant":
        message = record.get("message", {})
        content = message.get("content", [])
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                name = block.get("name", "")
                if name == "Agent":
                    return "agent_spawn"
                if name == "Skill":
                    return "skill_invocation"
                if name in _PLUMBING_TOOLS:
                    return "skip"
                return "tool_call"
        # No tool_use blocks found (only thinking / text)
        return "skip"

    # ------------------------------------------------------------------
    # Fallback — unknown record type
    # ------------------------------------------------------------------
    return "skip"
