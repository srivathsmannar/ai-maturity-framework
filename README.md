# AI Maturity Framework

Assess how effectively developers use AI coding tools by analyzing their Claude Code session logs. Produces a maturity score across 12 sub-dimensions and a narrative assessment report.

## How It Works

The framework reads Claude Code session JSONL files — the logs that Claude Code automatically creates during every session — and evaluates the developer's AI usage patterns across 4 dimensions and 12 sub-dimensions.

```
Session JSONL → upload → classify & route → assess → grade with Claude → report
```

**Three CLI commands, three stages:**

1. **`upload`** — Extracts and classifies records from raw session logs. Each record (prompt, tool call, agent spawn, skill invocation) is routed to one of 12 sub-dimensions based on its content.

2. **`assess`** — Grades each sub-dimension L1–L4 using Claude as an LLM judge. Merges all sessions per-project into one assessment. Claude compares the developer's actual behavior against a ground truth rubric.

3. **`report`** — Generates a Markdown assessment report with Claude-written narratives. Includes project context extraction, per-dimension analysis with inline evidence quotes, and actionable recommendations.

## The Maturity Model

### 4 Dimensions, 12 Sub-Dimensions

| Dimension | Sub-Dimensions |
|---|---|
| **Capability** | AI Tool Adoption, Prompt & Context Engineering, Agent Configuration |
| **Integration** | CI/CD Integration, Ticketing & Planning, Cross-System Connectivity |
| **Governance** | Quality Controls, Security & Compliance, Measurement & KPIs |
| **Execution Ownership** | Ways of Working, Accountability & Ownership, Scalability & Knowledge Transfer |

### 4 Maturity Levels

| Level | Name | Meaning |
|---|---|---|
| L1 | Assisted | AI supports individuals; workflows are human-driven |
| L2 | Integrated | AI embedded in standard workflows; measurable efficiency |
| L3 | Agentic | Multi-step agents own defined tasks; async execution |
| L4 | Autonomous | Agents plan and execute across the SDLC with structured oversight |

## Quick Start

### Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.9+ and the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated.

### Run the Full Pipeline

```bash
# 1. Extract session logs (fast, no Claude calls)
ai-maturity upload ~/.claude/projects/my-project/ --team-name myteam --user-name alice --output-dir data/input

# 2. Grade maturity (12 Claude calls, ~2 min)
ai-maturity assess --input-dir data/input/ --output-dir data/output/ --model sonnet

# 3. Generate report (6 Claude calls, ~1 min)
ai-maturity report --scored-dir data/output/ --input-dir data/input/ --output-dir reports/

# 4. View report
open reports/*.md
```

### CLI Reference

#### `ai-maturity upload <LOGS_PATH>`

Extracts records from Claude Code session JSONL files and routes each to one of 12 sub-dimensions.

| Option | Default | Description |
|---|---|---|
| `--team-name` | `unknown` | Team name for the developer |
| `--user-name` | `unknown` | Developer's name |
| `--output-dir` | `data/input/` | Where to write assessment-input JSONL |

**Input**: A directory containing `*.jsonl` session files (e.g., `~/.claude/projects/my-project/`)

**Output**: One JSONL file per session in `data/input/`, with each record tagged with `sub_dimension` and `dimension`.

#### `ai-maturity assess`

Merges all input files and grades each sub-dimension using Claude as an LLM judge.

| Option | Default | Description |
|---|---|---|
| `--input-dir` | `data/input/` | Directory with assessment-input JSONL from `upload` |
| `--output-dir` | `data/output/` | Where to write scored JSONL |
| `--model` | `sonnet` | Claude model for grading (`sonnet`, `opus`, `haiku`) |
| `--team-name` | (all) | Filter input files by team |
| `--user-name` | (all) | Filter input files by user |
| `--save-context` | off | Write a `.context.txt` showing grading details |

**How it works**: Merges all input JSONL into one file, then makes 12 Claude subprocess calls (one per sub-dimension). Each call sends the ground truth rubric + the developer's actual records and asks Claude to assign a level.

**Output**: A single `*_scored.jsonl` with 12 records (one per sub-dimension), each containing `level`, `confidence`, `evidence`, and `reasoning`.

#### `ai-maturity report`

Generates a polished Markdown assessment report with Claude-written narratives.

| Option | Default | Description |
|---|---|---|
| `--scored-dir` | `data/output/` | Directory with scored JSONL from `assess` |
| `--input-dir` | `data/input/` | Directory with input JSONL from `upload` (for exemplars) |
| `--output-dir` | `reports/` | Where to write the report |
| `--model` | `sonnet` | Claude model for narrative writing |
| `--team-name` | (all) | Filter by team |
| `--user-name` | (all) | Filter by user |

**How it works**: Makes 6 Claude subprocess calls:
1. **Project context** (1 call) — reads all developer prompts and summarizes what they were building
2. **Dimension narratives** (4 calls) — writes contextual analysis per dimension, weaving in direct quotes from the developer's prompts
3. **Executive summary** (1 call) — synthesizes the overall assessment

**Output**: A Markdown report with project context, score matrix, dimension narratives with inline evidence, and actionable recommendations.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  UPLOAD (extract & route)                                       │
│                                                                 │
│  classifier.py → extractor.py → router.py → pipeline.py        │
│  Classify each    Pull data      Route to 1    Orchestrate      │
│  JSONL record     payload        of 12 sub-    full flow        │
│  into type        from record    dimensions                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ data/input/*.jsonl
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ASSESS (grade with Claude)                                     │
│                                                                 │
│  ground_truth.py → prompt_builder.py → claude_judge.py          │
│  Parse rubric      Combine rubric +    Call claude -p            │
│  from markdown     evidence into       with --json-schema       │
│                    grading prompt       via subprocess stdin     │
│                                                                 │
│  grader.py → scorer.py                                          │
│  Orchestrate   Aggregate 12 scores → 4 dims → overall          │
│  12 calls                                                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ data/output/*_scored.jsonl
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  REPORT (generate narrative)                                    │
│                                                                 │
│  context_extractor.py → narrative_prompts.py → claude_writer.py │
│  Summarize what       Build prompts that      Call claude -p     │
│  developer was        ask for contextual      with --output-     │
│  building             analysis + quotes       format text        │
│                                                                 │
│  exemplars.py → report.py                                       │
│  Select top      Assemble full Markdown report                  │
│  evidence                                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Key Design Decisions

- **Claude CLI subprocess, not SDK** — No Python dependency on the Anthropic SDK. Uses `claude -p` via subprocess stdin. Two modes: `--json-schema` for structured grading output, `--output-format text` for narrative writing.
- **One record → one sub-dimension** — Every extracted record routes to exactly one of 12 sub-dimensions. Routing is deterministic via keyword matching (prompts) and tool/skill pattern matching (tool calls).
- **Ground truth in markdown** — The rubric lives in a human-readable markdown file (`docs/MATURITY_ASSESSMENT_GROUND_TRUTH.md`), parsed at runtime. Easy to edit and version.
- **Per-project assessment** — Sessions are merged before grading so the developer gets one comprehensive assessment across all their sessions, not per-session fragments.
- **Graceful fallback** — If any Claude subprocess call fails (timeout, bad response), the system defaults to L1/low confidence rather than crashing.

### What Gets Routed Where

The router classifies records by content. Examples:

| Record | Routes To |
|---|---|
| Prompt mentioning "JIRA", "Linear", ticket IDs | `ticketing_planning` |
| Bash running `pytest`, `npm test` | `cicd_integration` |
| Agent spawn with specialized `subagent_type` | `agent_configuration` |
| Skill invocation: `google-docs`, `sql-query` | `cross_system_connectivity` |
| MCP tool: `mcp__jira__*`, `mcp__linear__*` | `ticketing_planning` |
| MCP tool: `mcp__grafana__*`, `mcp__sentry__*` | `measurement_kpis` |
| MCP tool: `mcp__postgres__*`, `mcp__slack__*` | `cross_system_connectivity` |
| Prompt mentioning "PII", "compliance", "policy" | `security_compliance` |
| Generic prompt with no specific signals | `ai_tool_adoption` (default) |

## Workflows

### Assess a Single Project

```bash
ai-maturity upload ~/.claude/projects/my-project/ --team-name eng --user-name alice --output-dir data/input
ai-maturity assess --input-dir data/input/ --output-dir data/output/ --model sonnet
ai-maturity report --scored-dir data/output/ --input-dir data/input/ --output-dir reports/
```

### Re-generate Report with Different Model

The `report` command doesn't re-grade — it just rewrites narratives from existing scores:

```bash
ai-maturity report --scored-dir data/output/ --input-dir data/input/ --output-dir reports/ --model opus
```

### Assess with Debug Context

See exactly what the grader sent to Claude for each sub-dimension:

```bash
ai-maturity assess --input-dir data/input/ --output-dir data/output/ --save-context
cat data/output/*_context.txt
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Documentation

| Document | Description |
|---|---|
| [`docs/RUBRIC_OVERVIEW.md`](docs/RUBRIC_OVERVIEW.md) | Taxonomy, scoring model, maturity thresholds |
| [`docs/MATURITY_ASSESSMENT_GROUND_TRUTH.md`](docs/MATURITY_ASSESSMENT_GROUND_TRUTH.md) | Full rubric with L1–L4 examples for all 12 sub-dimensions |
| [`docs/SIGNAL_GRADING_GUIDE.md`](docs/SIGNAL_GRADING_GUIDE.md) | How records are routed and graded |
| [`docs/JSONL_FORMAT.md`](docs/JSONL_FORMAT.md) | JSONL schemas for input, output, and ground truth |

## Requirements

- Python 3.9+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated
- No additional Python dependencies beyond `click` (used for CLI)
