# AI Maturity Framework — Rubric Overview

The AI Maturity Framework assesses how effectively developers and teams use AI tools across the software development lifecycle. It scores 12 sub-dimensions grouped into 4 dimensions, each rated on a 4-level maturity scale. For the full rubric with example prompts and signal patterns, see [MATURITY_ASSESSMENT_GROUND_TRUTH.md](MATURITY_ASSESSMENT_GROUND_TRUTH.md).

## Dimensions and Sub-Dimensions

The canonical machine-readable identifiers used in all JSONL files and code:

| Dimension | `dimension` | Sub-Dimension | `sub_dimension` |
|---|---|---|---|
| Capability | `capability` | AI Tool Adoption | `ai_tool_adoption` |
| Capability | `capability` | Prompt & Context Engineering | `prompt_context_engineering` |
| Capability | `capability` | Agent Configuration | `agent_configuration` |
| Integration | `integration` | CI/CD Integration | `cicd_integration` |
| Integration | `integration` | Ticketing & Planning | `ticketing_planning` |
| Integration | `integration` | Cross-System Connectivity | `cross_system_connectivity` |
| Governance | `governance` | Quality Controls | `quality_controls` |
| Governance | `governance` | Security & Compliance | `security_compliance` |
| Governance | `governance` | Measurement & KPIs | `measurement_kpis` |
| Execution Ownership | `execution_ownership` | Ways of Working | `ways_of_working` |
| Execution Ownership | `execution_ownership` | Accountability & Ownership | `accountability_ownership` |
| Execution Ownership | `execution_ownership` | Scalability & Knowledge Transfer | `scalability_knowledge_transfer` |

## Maturity Levels

| `level` | `level_label` | Meaning |
|---|---|---|
| 1 | Assisted | AI supports individuals; workflows are human-driven. No standards or measurement. |
| 2 | Integrated | AI embedded in standard workflows. Measurable team efficiency. Still synchronous. |
| 3 | Agentic | Multi-step agents own defined tasks. Async execution. Structured governance. |
| 4 | Autonomous | Agents plan and execute across the SDLC with structured oversight. 24/7 delivery. |

Levels are scored per sub-dimension. A team can be L3 on AI Tool Adoption and L1 on Security & Compliance.

## Assessment Categories

An **assessment category** maps to a specific record type or data structure inside Claude Code session JSONL files. Each category extracts different maturity signals from the same session data. All categories share the same 12 sub-dimensions and 4 levels.

### Source: Claude Code Session JSONL Structure

A Claude Code session produces a `{session_id}.jsonl` file plus optional companion directories:

```
{session_id}.jsonl              # main session log (all record types)
{session_id}/
  subagents/                    # sub-agent sessions
    agent-{id}.jsonl            # full JSONL for each sub-agent
    agent-{id}.meta.json        # agent type and description
  tool-results/                 # large tool outputs stored externally
    {tool_use_id}.json          # MCP/knowledge search results
    {tool_use_id}.txt           # Bash stdout, query results, etc.
```

### Record Types in Session Data

Each JSONL record has a `type` field. Records are classified into types, then each record is **routed to exactly one sub-dimension** based on its content:

| Record Type | `category` value | Source | What It Contains |
|---|---|---|---|
| Prompt | `prompts` | `type: "user"` (non-meta, no `toolUseResult`) | Developer prompt text — routed by keyword matching |
| Tool Call | `tool_usage` | `type: "assistant"` → `content[].type: "tool_use"` | Tool name + input — routed by tool name and command content |
| Agent Spawn | `agent_delegation` | `tool_use` where `name: "Agent"` | Agent type, description, prompt — always routes to `agent_configuration` |
| Skill Invocation | `tool_usage` | `tool_use` where `name: "Skill"` | Skill name, args — routed by skill name to relevant sub-dimension |
| Session Config | `session_metadata` | `type: "system"` with `subtype: "stop_hook_summary"` or `"local_command"` | Hook configuration, slash commands — routes to `agent_configuration` |
| Tool Result | `tool_results` | `type: "user"` with `toolUseResult` | Tool outputs — attached as supporting context to parent tool call, not routed independently |

**Skipped** (not assessable): `progress`, `file-history-snapshot`, `queue-operation`, `permission-mode`, `last-prompt`, `thinking` blocks (reflect model capability, not developer maturity), `text` blocks (assistant responses), system subtypes `turn_duration`, `api_error`, `compact_boundary`.

### How Categories Map to Sub-Dimensions

Not every category provides signals for every sub-dimension. The primary signal sources:

| Sub-Dimension | Primary Category | Supporting Categories |
|---|---|---|
| AI Tool Adoption | `prompts` | `tool_usage`, `session_metadata` |
| Prompt & Context Engineering | `prompts` | `tool_inputs` (file paths loaded) |
| Agent Configuration | `tool_usage` | `agent_delegation`, `prompts` |
| CI/CD Integration | `tool_inputs` | `tool_results`, `prompts` |
| Ticketing & Planning | `prompts` | `tool_inputs` |
| Cross-System Connectivity | `tool_usage` | `tool_inputs`, `tool_results` |
| Quality Controls | `tool_inputs` | `prompts`, `tool_results` |
| Security & Compliance | `prompts` | `tool_inputs`, `session_metadata` |
| Measurement & KPIs | `prompts` | `tool_results` |
| Ways of Working | `prompts` | `session_metadata`, `tool_usage` |
| Accountability & Ownership | `prompts` | `session_metadata` |
| Scalability & Knowledge Transfer | `prompts` | `agent_delegation`, `tool_inputs` |

Ground truth files live at `data/ground-truth/{sub_dimension}.jsonl` — one per sub-dimension. See [JSONL_FORMAT.md](JSONL_FORMAT.md) for schema details.

## Scoring Model

**Per sub-dimension**: Each of the 12 sub-dimensions receives:
- A **level** (1-4)
- A **confidence** (`high`, `medium`, or `low`)
- **Evidence** — the specific artifacts that justified the score

**Per dimension**: Average of its 3 sub-dimension scores.

**Overall score**: Average of all 12 sub-dimension scores.

**Maturity label thresholds** (matching the scorecard formulas):

| Score Range | Maturity Label |
|---|---|
| < 1.5 | L1: Assisted |
| 1.5 – 2.49 | L2: Integrated |
| 2.5 – 3.49 | L3: Agentic |
| >= 3.5 | L4: Autonomous |

## Related Files

- [MATURITY_ASSESSMENT_GROUND_TRUTH.md](MATURITY_ASSESSMENT_GROUND_TRUTH.md) — Full rubric with example prompts, signals, and patterns for all 12 × 4 combinations
- [SIGNAL_GRADING_GUIDE.md](SIGNAL_GRADING_GUIDE.md) — How signals flow from raw JSONL records through routing and grading to produce scores
- [JSONL_FORMAT.md](JSONL_FORMAT.md) — Technical reference for JSONL file schemas (ground truth, input, output)
- [AI_Maturity_Scorecard.xlsx](AI_Maturity_Scorecard.xlsx) — Excel scorecard with rubric matrix, individual and team scorecards
