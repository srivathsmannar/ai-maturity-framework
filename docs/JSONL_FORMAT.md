# JSONL File Format Reference

This document defines the JSONL schemas used by the AI Maturity Framework: the source session JSONL produced by Claude Code, the ground truth format, assessment input, and assessment output.

## Why JSONL

JSONL (JSON Lines) stores one JSON object per line, newline-delimited. Each line is independently parseable, making files streamable, appendable, and easy to process with standard CLI tools (`wc -l`, `head`, `jq`, `grep`).

## Conventions

- File extension: `.jsonl`
- Encoding: UTF-8
- One JSON object per line — no multi-line objects, no trailing commas
- Field names: `snake_case`
- Every assessment record includes a `category` field
- Timestamps: ISO 8601 (`2026-04-25T14:30:00Z`)
- Dates: ISO 8601 (`2026-04-25`)
- File paths in this document are relative to the repository root

## Directory Layout

```
data/
  ground-truth/
    ai_tool_adoption.jsonl                 # labeled examples for AI Tool Adoption
    prompt_context_engineering.jsonl        # labeled examples for Prompt & Context Engineering
    agent_configuration.jsonl              # ...one file per sub-dimension (12 total)
    cicd_integration.jsonl
    ticketing_planning.jsonl
    cross_system_connectivity.jsonl
    quality_controls.jsonl
    security_compliance.jsonl
    measurement_kpis.jsonl
    ways_of_working.jsonl
    accountability_ownership.jsonl
    scalability_knowledge_transfer.jsonl
  input/
    {team}_{user}_{YYYY-MM-DD}.jsonl       # extracted records ready to score
  output/
    {team}_{user}_{YYYY-MM-DD}_scored.jsonl # assessment results
```

Ground truth files are organized **per sub-dimension**, not per record type. Each file contains labeled examples at all 4 levels, mixing record types (prompts, tool calls, agent spawns) since a sub-dimension may be evidenced by different record types at different maturity levels.

---

## Source: Claude Code Session JSONL

The raw input to the framework is a Claude Code session log. Understanding this structure is essential because all assessment categories are extracted from it.

### File Layout

```
~/.claude/projects/{project_path}/
  {session_id}.jsonl                       # main session log
  {session_id}/
    subagents/
      agent-{id}.jsonl                     # sub-agent session (same JSONL format)
      agent-{id}.meta.json                 # {"agentType": "...", "description": "..."}
    tool-results/
      {tool_use_id}.json                   # large MCP/search results
      {tool_use_id}.txt                    # large Bash output, query results
```

### Record Types

Every line in a session JSONL has a `type` field. The full set:

| `type` | Description | Key Fields | Assessment Category |
|---|---|---|---|
| `user` | User message (prompt or tool result) | `message.content`, `toolUseResult`, `isMeta`, `cwd` | `prompts`, `tool_results` |
| `assistant` | Assistant response | `message.content[]` (blocks of `thinking`, `text`, `tool_use`) | `tool_usage`, `tool_inputs`, `thinking`, `agent_delegation` |
| `system` | System events | `subtype`, `content` | `session_metadata` |
| `progress` | Streaming progress | `data.type` (`hook_progress`, `agent_progress`) | `session_metadata` |
| `file-history-snapshot` | File backup checkpoint | `snapshot.trackedFileBackups` | — |
| `queue-operation` | Background task completion | `operation`, `content` | — |
| `permission-mode` | Permission setting | `permissionMode` | — |
| `last-prompt` | Final prompt of session | `lastPrompt` | — |

### Common Fields on Every Record

| Field | Type | Description |
|---|---|---|
| `type` | string | Record type (see table above) |
| `uuid` | string | Unique record identifier |
| `parentUuid` | string | Parent record in conversation tree |
| `timestamp` | string | ISO 8601 timestamp |
| `sessionId` | string | Session identifier |
| `cwd` | string | Working directory at time of record |
| `version` | string | Claude Code version |
| `entrypoint` | string | How Claude was invoked (`cli`, etc.) |

### Content Blocks in Assistant Messages

`assistant` records contain `message.content`, an array of typed blocks:

**`thinking` block** — Claude's internal reasoning:
```json
{"type": "thinking", "thinking": "The user wants me to implement..."}
```

**`text` block** — Visible response text:
```json
{"type": "text", "text": "I'll start by reading the config file."}
```

**`tool_use` block** — Tool invocation:
```json
{"type": "tool_use", "id": "toolu_vrtx_01...", "name": "Bash", "input": {"command": "git status", "description": "Check repo status"}}
```

### System Record Subtypes

| `subtype` | Description | Assessment Signal |
|---|---|---|
| `turn_duration` | Time for one assistant turn (ms) | Session efficiency |
| `api_error` | API call failure | Error patterns |
| `stop_hook_summary` | Hooks that ran at turn end | Hook configuration maturity |
| `compact_boundary` | Context window compaction event | Session complexity |
| `local_command` | Slash command invocation | Skill/command usage |

### Sub-Agent Meta Files

`agent-{id}.meta.json` contains:
```json
{"agentType": "general-purpose", "description": "Review code changes"}
```

Agent types seen in the wild: `general-purpose`, `codebase-search`, `Plan`, `Explore`, `code-reviewer`.

---

## Schema: Ground Truth

**Path**: `data/ground-truth/{sub_dimension}.jsonl`

Each file contains labeled examples for a single sub-dimension across all 4 levels. Examples may be different record types (prompts, tool calls, agent spawns) since different maturity levels may be best evidenced by different record types. The scorer uses these as few-shot examples and calibration anchors.

### Common Fields (all categories)

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier. Convention: `gt-{dim_short}-{subdim}-L{n}-{seq}` |
| `category` | string | yes | Assessment category |
| `dimension` | string | yes | One of: `capability`, `integration`, `governance`, `execution_ownership` |
| `sub_dimension` | string | yes | One of the 12 canonical identifiers (see [RUBRIC_OVERVIEW.md](RUBRIC_OVERVIEW.md)) |
| `level` | integer | yes | Maturity level: `1`, `2`, `3`, or `4` |
| `level_label` | string | yes | Human-readable: `Assisted`, `Integrated`, `Agentic`, or `Autonomous` |
| `signals` | string[] | yes | Pattern keywords present that indicate this level |
| `anti_signals` | string[] | yes | Patterns that would disqualify this level (empty if none) |
| `notes` | string | no | Free-text annotation explaining why this example fits the level |

### Category-Specific Fields

**`prompts`** — The developer's raw prompt text:

| Field | Type | Required | Description |
|---|---|---|---|
| `prompt_text` | string | yes | The example prompt text |

```json
{"id": "gt-cap-ai_tool_adoption-L3-001", "category": "prompts", "dimension": "capability", "sub_dimension": "ai_tool_adoption", "level": 3, "level_label": "Agentic", "prompt_text": "For this refactoring, dispatch to Claude Code since it has better git integration; for the test suite, Copilot handles that better.", "signals": ["multi-tool routing", "task-based selection", "tool capability awareness"], "anti_signals": [], "notes": "Explicitly chooses tool based on task fit."}
```

**`tool_usage`** — Tool call patterns from assistant messages:

| Field | Type | Required | Description |
|---|---|---|---|
| `tool_names` | string[] | yes | Tools used (e.g., `["Bash", "Agent", "Skill"]`) |
| `tool_counts` | object | yes | Map of tool name to call count |
| `has_agents` | boolean | yes | Whether Agent tool was used |
| `agent_types` | string[] | no | Sub-agent types spawned |
| `skills_invoked` | string[] | no | Skill names invoked |

```json
{"id": "gt-cap-agent_configuration-L3-001", "category": "tool_usage", "dimension": "capability", "sub_dimension": "agent_configuration", "level": 3, "level_label": "Agentic", "tool_names": ["Bash", "Read", "Agent", "Skill"], "tool_counts": {"Bash": 12, "Read": 5, "Agent": 4, "Skill": 3}, "has_agents": true, "agent_types": ["general-purpose", "Plan"], "skills_invoked": ["task-executor", "ci-data"], "signals": ["multi-agent dispatch", "specialized agent types", "skill chaining"], "anti_signals": [], "notes": "Uses Agent tool with multiple specialized types and invokes workflow skills."}
```

**`tool_inputs`** — Parameters passed to tools, revealing workflow patterns:

| Field | Type | Required | Description |
|---|---|---|---|
| `tool_name` | string | yes | Tool that was called |
| `input_summary` | string | yes | Summarized input (e.g., the Bash command or file path) |
| `input_data` | object | yes | The raw `input` object from the `tool_use` block |

```json
{"id": "gt-int-cicd_integration-L3-001", "category": "tool_inputs", "dimension": "integration", "sub_dimension": "cicd_integration", "level": 3, "level_label": "Agentic", "tool_name": "Bash", "input_summary": "pytest tests/ && gh pr create --draft", "input_data": {"command": "pytest tests/ && gh pr create --draft", "description": "Run tests and submit PR"}, "signals": ["CI command chaining", "test-before-merge", "automated pipeline interaction"], "anti_signals": [], "notes": "Agent chains test execution directly into PR submission."}
```

**`agent_delegation`** — Sub-agent spawning patterns:

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_type` | string | yes | The `subagent_type` or default `general-purpose` |
| `agent_description` | string | yes | The `description` field from the Agent call |
| `agent_prompt_summary` | string | yes | First 200 chars of the agent prompt |
| `parallel_agents` | integer | no | Number of agents spawned in same turn |

```json
{"id": "gt-cap-agent_configuration-L4-001", "category": "agent_delegation", "dimension": "capability", "sub_dimension": "agent_configuration", "level": 4, "level_label": "Autonomous", "agent_type": "Plan", "agent_description": "Design implementation approach", "agent_prompt_summary": "Design the implementation for the new pipeline based on the reference...", "parallel_agents": 3, "signals": ["parallel agent dispatch", "specialized agent types", "task decomposition"], "anti_signals": [], "notes": "Spawns 3 parallel agents with distinct roles for task decomposition."}
```

### ID Convention

Format: `gt-{dim_short}-{sub_dimension}-L{level}-{seq}`

Dimension short codes:
- `cap` = capability
- `int` = integration
- `gov` = governance
- `exe` = execution_ownership

Example: `gt-cap-ai_tool_adoption-L2-003` is the 3rd ground truth example for AI Tool Adoption at Level 2.

---

## Schema: Assessment Input

**Path**: `data/input/{team}_{user}_{YYYY-MM-DD}.jsonl`

Records extracted from session logs, ready for the scorer to analyze. Each record belongs to one category.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier. Convention: `in-{seq}` |
| `category` | string | yes | Record type: `prompts`, `tool_usage`, `agent_delegation`, `session_metadata` |
| `sub_dimension` | string | yes | The sub-dimension this record was routed to |
| `dimension` | string | yes | Parent dimension of the sub-dimension |
| `team` | string | yes | Team name |
| `user` | string | yes | Developer username |
| `session_id` | string | yes | Source session identifier |
| `timestamp` | string | yes | ISO 8601 timestamp |
| `source` | string | yes | Where extracted from (e.g., `"claude_session_log"`) |
| `data` | object | yes | Category-specific payload (see below) |
| `metadata` | object | no | Additional context (cwd, version, etc.) |

### Category-Specific `data` Payloads

**`prompts`**: `{"prompt_text": "..."}`

**`tool_usage`** (per-record, one per tool call or skill invocation):
`{"tool_name": "Bash", "input": {"command": "pytest tests/", "description": "Run tests"}}`

**`agent_delegation`** (per-record, one per Agent spawn):
`{"tool_name": "Agent", "agent_type": "Plan", "agent_description": "Design approach", "agent_prompt_summary": "...", "parallel_agents": null, "input": {...}}`

**`session_metadata`**: `{"subtype": "stop_hook_summary", "hook_count": 2, "hooks": [...], "content": ""}` or `{"subtype": "local_command", ...}`

### Example

```json
{"id": "in-001", "category": "prompts", "sub_dimension": "ai_tool_adoption", "dimension": "capability", "team": "platform", "user": "alice", "session_id": "14197ef1-946b-4963-bd74-ffae249ef0ee", "timestamp": "2026-04-25T14:30:00Z", "source": "claude_session_log", "data": {"prompt_text": "Use Claude Code to set up the Git integration — we standardize on Claude for AI work"}, "metadata": {"cwd": "/Users/alice/myproject"}}
```

```json
{"id": "in-042", "category": "tool_usage", "sub_dimension": "cicd_integration", "dimension": "integration", "team": "platform", "user": "alice", "session_id": "14197ef1-946b-4963-bd74-ffae249ef0ee", "timestamp": "2026-04-25T14:30:00Z", "source": "claude_session_log", "data": {"tool_name": "Bash", "input": {"command": "pytest tests/test_foo.py", "description": "Run tests"}}, "metadata": {}}
```

---

## Schema: Assessment Output

**Path**: `data/output/{team}_{user}_{YYYY-MM-DD}_scored.jsonl`

Scored results produced by the `assess` command. One line per sub-dimension per assessment run.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Unique identifier. Convention: `out-{input_seq}-{sub_dimension}` |
| `category` | string | yes | Assessment category (e.g., `"prompts"`) |
| `input_id` | string | yes | ID of the input record that provided the strongest evidence |
| `team` | string | yes | Team name |
| `user` | string | yes | Developer username |
| `assessed_at` | string | yes | ISO 8601 timestamp of when the assessment ran |
| `dimension` | string | yes | Parent dimension identifier |
| `sub_dimension` | string | yes | Sub-dimension identifier |
| `level` | integer | yes | Assigned maturity level: `1`, `2`, `3`, or `4` |
| `level_label` | string | yes | Human-readable level name |
| `confidence` | string | yes | `high`, `medium`, or `low` |
| `evidence` | string[] | yes | Prompt excerpts or observations that justify the score |
| `matched_signals` | string[] | yes | Signals from ground truth that were detected |
| `reasoning` | string | yes | Free-text explanation of why this level was assigned |
| `record_count` | integer | yes | Number of input records routed to this sub-dimension |

### Example

```json
{"id": "out-001-ai_tool_adoption", "category": "prompts", "input_id": "in-001", "team": "platform", "user": "alice", "assessed_at": "2026-04-26T10:00:00Z", "dimension": "capability", "sub_dimension": "ai_tool_adoption", "level": 2, "level_label": "Integrated", "confidence": "high", "evidence": ["Prompt references standardized tool choice: 'we standardize on Claude for AI work'"], "matched_signals": ["standardized tool selection"], "reasoning": "Developer explicitly mentions team standardization on a specific AI tool, matching L2 pattern."}
```

### Composite Scoring

The output file contains one record per sub-dimension (12 records per assessment run). To compute aggregate scores:

- **Dimension score**: Average of the 3 sub-dimension `level` values within a dimension
- **Overall score**: Average of all 12 `level` values
- **Maturity label**: Apply thresholds from [RUBRIC_OVERVIEW.md](RUBRIC_OVERVIEW.md#scoring-model)

---

## Adding a New Assessment Category

All categories are extracted from the same Claude Code session JSONL files. To add a new one:

1. **Identify the source data**: Determine which record type(s) and content blocks in the session JSONL contain the signal. See the [Source: Claude Code Session JSONL](#source-claude-code-session-jsonl) section for the full record type reference.

2. **Create ground truth**: Add `data/ground-truth/{new_category}.jsonl` with labeled examples. Use the common fields (`id`, `category`, `dimension`, `sub_dimension`, `level`, `level_label`, `signals`, `anti_signals`) plus category-specific fields for the artifact being analyzed.

3. **Add extraction logic**: Build the extractor that reads session JSONL files, filters for the relevant record types, and produces `data/input/` JSONL records with `"category": "{new_category}"` and the appropriate `data` payload.

4. **Score and output**: The scoring pipeline and output schema remain identical. The `category` field distinguishes results across assessment types.

## Validation Rules

When producing or consuming JSONL files, enforce these constraints:

- `dimension` must be one of: `capability`, `integration`, `governance`, `execution_ownership`
- `sub_dimension` must be one of the 12 canonical values (see [RUBRIC_OVERVIEW.md](RUBRIC_OVERVIEW.md#dimensions-and-sub-dimensions))
- `sub_dimension` must belong to its parent `dimension`:
  - `capability`: `ai_tool_adoption`, `prompt_context_engineering`, `agent_configuration`
  - `integration`: `cicd_integration`, `ticketing_planning`, `cross_system_connectivity`
  - `governance`: `quality_controls`, `security_compliance`, `measurement_kpis`
  - `execution_ownership`: `ways_of_working`, `accountability_ownership`, `scalability_knowledge_transfer`
- `level` must be an integer from 1 to 4
- `confidence` must be one of: `high`, `medium`, `low`
- `category` must be one of: `prompts`, `tool_usage`, `agent_delegation`, `tool_results`, `session_metadata`

## Related Files

- [RUBRIC_OVERVIEW.md](RUBRIC_OVERVIEW.md) — Category taxonomy, level definitions, and scoring model
- [SIGNAL_GRADING_GUIDE.md](SIGNAL_GRADING_GUIDE.md) — How signals flow from raw JSONL records through routing and grading to produce scores
- [MATURITY_ASSESSMENT_GROUND_TRUTH.md](MATURITY_ASSESSMENT_GROUND_TRUTH.md) — Full rubric with example prompts for all 12 × 4 combinations
- [AI_Maturity_Scorecard.xlsx](AI_Maturity_Scorecard.xlsx) — Excel scorecard with rubric matrix and scorecards
