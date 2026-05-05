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
git clone https://github.com/srivathsmannar/ai-maturity-framework.git
cd ai-maturity-framework
pip install -e .
```

This registers the `ai-maturity` CLI command on your system. Requires Python 3.9+ and the [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated.

### Run the Full Pipeline

```bash
# 1. Submit session logs (fast, no Claude calls)
ai-maturity submit ~/.claude/projects/my-project/ --name alice --team platform

# 2. Grade maturity (12 Claude calls, ~2 min)
ai-maturity assess alice

# 3. Generate report (6 Claude calls, ~1 min)
ai-maturity report alice

# 4. See all developers
ai-maturity list
```

Reports are saved to `~/.ai-maturity/reports/`. All data is stored in `~/.ai-maturity/store.db`.

### CLI Reference

#### `ai-maturity submit <LOGS_PATH>`

Extracts records from Claude Code session JSONL files, classifies and routes each to one of 12 sub-dimensions, and saves them to the local store.

| Option | Default | Description |
|---|---|---|
| `--name` | (required) | Developer name |
| `--team` | (required) | Team name |

**Input**: A directory containing `*.jsonl` session files (e.g., `~/.claude/projects/my-project/`)

Re-submitting for the same name replaces previous records.

#### `ai-maturity assess <NAME>`

Grades a developer's AI maturity across all 12 sub-dimensions using Claude as an LLM judge.

| Option | Default | Description |
|---|---|---|
| `--model` | `sonnet` | Claude model for grading (`sonnet`, `opus`, `haiku`) |

**How it works**: Reads the developer's records from the store, makes 12 Claude subprocess calls (one per sub-dimension), and saves the scored results back to the store.

#### `ai-maturity report <NAME>`

Generates a polished assessment report with Claude-written narratives.

| Option | Default | Description |
|---|---|---|
| `--format` | `both` | Output format: `md`, `html`, or `both` |
| `--model` | `sonnet` | Claude model for narrative writing |
| `--output-dir` | `~/.ai-maturity/reports/` | Custom output directory |

**How it works**: Makes 6 Claude subprocess calls:
1. **Project context** (1 call) — reads all developer prompts and summarizes what they were building
2. **Dimension narratives** (4 calls) — writes contextual analysis per dimension, weaving in direct quotes from the developer's prompts
3. **Executive summary** (1 call) — synthesizes the overall assessment

**Output**: Markdown and/or HTML report with project context, score matrix, dimension narratives with inline evidence, and actionable recommendations.

#### `ai-maturity list`

Shows all submitted developers and their assessment status.

```
Name                 Team            Submitted    Assessed
------------------------------------------------------------
alice                platform        2026-05-01   Yes
bob                  infra           2026-04-30   No
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  SUBMIT (extract & route → store)                               │
│                                                                 │
│  classifier.py → extractor.py → router.py → pipeline.py        │
│  Classify each    Pull data      Route to 1    Orchestrate      │
│  JSONL record     payload        of 12 sub-    full flow        │
│  into type        from record    dimensions                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │ store.py (SQLite)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  ASSESS (grade with Claude → store)                             │
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
                           │ store.py (SQLite)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  REPORT (generate narrative → files)                            │
│                                                                 │
│  context_extractor.py → narrative_prompts.py → claude_writer.py │
│  Summarize what       Build prompts that      Call claude -p     │
│  developer was        ask for contextual      with --output-     │
│  building             analysis + quotes       format text        │
│                                                                 │
│  exemplars.py → report.py → html_report.py                      │
│  Select top      Assemble       Convert to                      │
│  evidence        Markdown       polished HTML                   │
└─────────────────────────────────────────────────────────────────┘

Storage: ~/.ai-maturity/store.db (SQLite) + ~/.ai-maturity/reports/
```

### Key Design Decisions

- **Claude CLI subprocess, not SDK** — No Python dependency on the Anthropic SDK. Uses `claude -p` via subprocess stdin. Two modes: `--json-schema` for structured grading output, `--output-format text` for narrative writing.
- **One record → one sub-dimension** — Every extracted record routes to exactly one of 12 sub-dimensions. Routing is deterministic via keyword matching (prompts) and tool/skill pattern matching (tool calls).
- **Ground truth in markdown** — The rubric lives in a human-readable markdown file (`docs/MATURITY_ASSESSMENT_GROUND_TRUTH.md`), parsed at runtime. Easy to edit and version.
- **SQLite store** — All data lives in `~/.ai-maturity/store.db`. No directory juggling. Submit once, assess and report by name.
- **Per-project assessment** — All sessions for a developer are merged before grading, producing one comprehensive assessment.
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

### Assess a Developer

```bash
ai-maturity submit ~/.claude/projects/my-project/ --name alice --team platform
ai-maturity assess alice
ai-maturity report alice
```

### Re-generate Report with Different Model

The `report` command doesn't re-grade — it just rewrites narratives from existing scores:

```bash
ai-maturity report alice --model opus
```

### HTML Report

```bash
ai-maturity report alice --format html
open ~/.ai-maturity/reports/alice_report.html
```

### Run Tests

```bash
pip install -e ".[dev]"   # installs pytest
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
