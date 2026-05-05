# Signal Grading Guide

How raw JSONL session records flow through routing, signal extraction, and grading to produce a maturity score for each of the 12 sub-dimensions.

## Core Principle: One Line → One Sub-Dimension

Every input record extracted from a session JSONL file is routed to **exactly one** of the 12 sub-dimensions. A single prompt or tool call does not produce scores across multiple sub-dimensions. This keeps grading deterministic and evidence traceable.

If a prompt contains signals for multiple sub-dimensions (e.g., mentions both CI and tickets), route it to the **strongest match** — the sub-dimension whose keywords appear most specifically. If ambiguous, prefer the sub-dimension with fewer existing evidence records in the session (balance coverage).

---

## Signal Flow Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Code Session JSONL                     │
│  {session_id}.jsonl + subagents/ + tool-results/                │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │  EXTRACT    │  Filter relevant record types
                    │             │  Discard: progress, file-history,
                    │             │  queue-operation, permission-mode
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │  CLASSIFY RECORD TYPE   │
              │                         │
              │  user (non-meta,        │──→ prompt record
              │    no toolUseResult)     │
              │                         │
              │  assistant → tool_use   │──→ tool record
              │                         │
              │  assistant → tool_use   │──→ agent record
              │    where name="Agent"   │
              │                         │
              │  user with              │──→ tool result record
              │    toolUseResult        │
              │                         │
              │  system (stop_hook_     │──→ session config record
              │    summary, local_cmd)  │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │   ROUTE     │  Each record → one sub-dimension
                    │             │  (see Routing Rules below)
                    └──────┬──────┘
                           │
              ┌────────────▼────────────┐
              │  GRADE PER SUB-DIM      │  For each sub-dimension:
              │                         │  collect all routed records,
              │  primary signals (use)  │  extract signals,
              │  noise signals (ignore) │  assign level 1-4
              │  confidence calibration │
              └────────────┬────────────┘
                           │
                    ┌──────▼──────┐
                    │  AGGREGATE  │  12 sub-dim scores → 4 dim
                    │             │  averages → 1 overall score
                    └─────────────┘
```

---

## What to Extract, What to Skip

### Extract (these are assessable records)

| Source | Record Filter | What to Pull |
|---|---|---|
| **Prompts** | `type: "user"` where `isMeta: false` AND no `toolUseResult` AND no `sourceToolUseID` | `message.content` (the text the developer typed) |
| **Tool calls** | `type: "assistant"` → `message.content[]` where block `type: "tool_use"` | `name`, `input` object |
| **Agent spawns** | Tool calls where `name: "Agent"` | `input.subagent_type`, `input.description`, `input.prompt`, `input.run_in_background` |
| **Skill invocations** | Tool calls where `name: "Skill"` | `input.skill`, `input.args` |
| **Tool results** | `type: "user"` with `toolUseResult` field, plus `tool-results/*.txt/*.json` files | Result content, success/failure |
| **Session config** | `type: "system"` with `subtype: "stop_hook_summary"` | `hookInfos[]` — what hooks are configured |
| **Slash commands** | `type: "system"` with `subtype: "local_command"` | Command name and args |
| **Sub-agent metadata** | `subagents/agent-{id}.meta.json` files | `agentType`, `description` |

### Skip (not assessable / noise)

| Source | Why Skip |
|---|---|
| `type: "progress"` | Streaming chunks — no complete signal, just partial delivery |
| `type: "file-history-snapshot"` | Internal bookkeeping, not developer behavior |
| `type: "queue-operation"` | Background task plumbing |
| `type: "permission-mode"` | One-time session setup |
| `type: "last-prompt"` | Duplicate of a `user` record |
| `type: "system"` with `subtype: "api_error"` | Infrastructure failures, not developer maturity |
| `type: "system"` with `subtype: "turn_duration"` | Latency metric, not a maturity signal |
| `type: "system"` with `subtype: "compact_boundary"` | Context window management, not developer behavior |
| `type: "assistant"` → `content[].type: "thinking"` | Claude's internal reasoning — reflects model capability, not developer maturity |
| `type: "assistant"` → `content[].type: "text"` | Claude's response text — we're grading the developer, not the assistant |
| `type: "user"` with `isMeta: true` | System-injected context (hook output, system reminders), not developer-authored |

---

## Routing Rules: Record → Sub-Dimension

### Prompt Records (developer-typed messages)

Route based on **keyword/pattern matching** against the prompt text. Check in this priority order (first match wins):

| Priority | Route To | Match Patterns |
|---|---|---|
| 1 | `security_compliance` | PII, compliance, policy, data handling, secrets, credentials, audit, GDPR, SOC2, redact |
| 2 | `measurement_kpis` | metric, KPI, dashboard, adoption rate, DORA, velocity, throughput, cycle time, MTTR, measure |
| 3 | `ticketing_planning` | ticket, JIRA, Linear, issue, ACME-\d+, T\d{6,}, backlog, sprint, story point, acceptance criteria |
| 4 | `cicd_integration` | CI, CD, pipeline, deploy, build log, test failure, GitHub Actions, Jenkins, rollback, merge gate |
| 5 | `cross_system_connectivity` | (names 2+ systems): GitHub+JIRA, Slack+Confluence, repo+ticketing, monitoring+alerting |
| 6 | `quality_controls` | quality, lint, checklist, test coverage, eval harness, code review criteria, auto-reject |
| 7 | `accountability_ownership` | owner, champion, responsible, team owns, SLA, accountability |
| 8 | `ways_of_working` | ways of working, protocol, convention, team process, documented workflow, README, wiki |
| 9 | `scalability_knowledge_transfer` | onboarding, playbook, knowledge transfer, ramp-up, template library, new team |
| 10 | `agent_configuration` | /command, skill, slash command, custom agent, workflow chain, error handling, spawn sub-agent |
| 11 | `prompt_context_engineering` | CLAUDE.md, context, convention, architecture doc, loaded from, per our, template, shared prompt |
| 12 | `ai_tool_adoption` | (default) — any prompt that doesn't match above routes here |

**Why this priority order?** Specific domain signals (security, metrics, tickets) are unambiguous and should be captured before general patterns. `ai_tool_adoption` is the catch-all because every prompt implicitly demonstrates _some_ level of tool adoption.

**Why `ai_tool_adoption` is last/default?** Every developer interaction with Claude is itself a tool adoption signal. A prompt that says "help me debug this" (no other signals) tells us the developer uses AI ad-hoc (L1). A prompt that says "use Claude Code for this because we standardize on it" has an explicit tool adoption signal _and_ would also match `ai_tool_adoption` patterns. By making it the default, we ensure no prompt is unrouted while keeping the more specific sub-dimensions from being starved of evidence.

### Tool Records (tool_use blocks from assistant messages)

Route based on **tool name and input content**:

| Tool Name | Route To | Condition |
|---|---|---|
| `Agent` | `agent_configuration` | Always — sub-agent spawning is the core agent config signal |
| `Skill` | Varies by skill name | Domain-specific skills route to their domain (see Skill routing table below) |
| `Bash` | `cicd_integration` | If command matches: `pytest`, `bazel`, `make test`, `npm test`, `jest`, `gh pr`, `git push`, deploy-related commands |
| `Bash` | `quality_controls` | If command matches: `lint`, `mypy`, `eslint`, `flake8`, `black`, `prettier`, coverage commands |
| `Bash` | `cross_system_connectivity` | If command matches: `gh`, `git`, `curl` to APIs |
| `Bash` | `prompt_context_engineering` | If command reads context files: `cat CLAUDE.md`, reads from `docs/`, `architecture` |
| `Bash` | `ai_tool_adoption` | Default for other Bash commands |
| `Read` | `prompt_context_engineering` | If reading: `CLAUDE.md`, `docs/`, `README`, convention/architecture files |
| `Read` | Route by file content | Otherwise route based on what the file relates to |
| `Write`/`Edit` | `prompt_context_engineering` | If writing to: `CLAUDE.md`, `.claude/`, convention files |
| `Write`/`Edit` | Route by file path | Otherwise route based on what the file relates to |
| `ToolSearch` | Skip | Infrastructure plumbing, not a maturity signal |
| `TaskCreate`/`TaskUpdate`/etc. | `ticketing_planning` | Task management = planning workflow |
| `mcp__*` | `cross_system_connectivity` | MCP tool use = cross-system integration (e.g., `mcp__postgres`, `mcp__github`, `mcp__slack`, `mcp__linear`, `mcp__jira`, `mcp__notion`, `mcp__sentry`) |
| `WebFetch`/`WebSearch` | `cross_system_connectivity` | External system access |
| `AskUserQuestion` | Skip | Clarification plumbing |

### Skill Routing Table

Domain-specific skills route to their relevant sub-dimension. The _presence and diversity_ of Skill usage (across a session) is itself an `agent_configuration` signal, but each individual invocation routes to its domain:

| Skill Name Pattern | Route To |
|---|---|
| `sql-query`, `notebook`, `analytics`, `analytics-cli`, `data-explorer` | `cross_system_connectivity` |
| `google-docs`, `wiki-query` | `cross_system_connectivity` |
| `ci-signals`, `fix-diff`, `ci-data` | `cicd_integration` |
| `review-diff`, `code-reviewer`, `simplify` | `quality_controls` |
| `tasks`, `diff-search` | `ticketing_planning` |
| `security-review`, `agent-security-guardrails` | `security_compliance` |
| `grafana-metrics`, `datadog`, `prometheus-helper`, `metrics-cli` | `measurement_kpis` |
| `init` (CLAUDE.md creation) | `prompt_context_engineering` |
| Everything else (`brainstorming`, `writing-plans`, `executing-plans`, `overnight`, etc.) | `agent_configuration` |

### Agent Records (Agent tool_use blocks)

Always route to `agent_configuration`. The agent spawn itself is the signal. Extract:
- `input.subagent_type` — specialized vs. generic
- `input.description` — task granularity
- `input.prompt` — delegation sophistication
- `input.run_in_background` — async execution
- Whether multiple Agent calls appear in the same assistant turn (parallel dispatch)

### Session Config Records

| Record | Route To | Signal |
|---|---|---|
| `stop_hook_summary` with hooks | `agent_configuration` | Hooks = custom agent configuration |
| `local_command` (slash commands) | `agent_configuration` | Slash command usage |

**Note on hooks as supporting context**: The `stop_hook_summary` record routes to `agent_configuration`. However, when grading _other_ sub-dimensions, the grader may inspect the _content_ of hooks (e.g., a security-scanning hook supports `security_compliance`, a context-loading hook supports `prompt_context_engineering`). This is not re-routing — it's the grader using session-wide context to calibrate confidence for its sub-dimension.

### Tool Result Records

Tool results are **not routed independently**. Instead, they are attached as supporting context to the tool call record they correspond to (matched via `sourceToolUseID`). They strengthen or weaken the confidence of the parent record's grade.

---

## Grading Logic: Per Sub-Dimension

For each sub-dimension, the grader collects all records routed to it and determines a level (1-4). The grader uses **primary signals** (must be present) and may use **supporting signals** (boost confidence). It ignores **noise** (present but irrelevant).

---

### 1. AI Tool Adoption (`ai_tool_adoption`)

**What we're measuring**: How intentionally are AI tools selected? Does the developer show awareness of tool trade-offs?

**Primary signals** (from prompt text):
- L1: Generic requests with no tool awareness ("help me debug this", "write a test")
- L2: Mentions standardized tool choice ("we use Claude for", "our team standardizes on")
- L3: Routes tasks to different tools by capability ("use X for this because", "dispatch to Y for that")
- L4: Defines autonomous routing policies ("routing rules: use X for refactoring, Y for security")

**Supporting signals** (from tool_usage):
- Number of distinct tools used in session
- Whether tools are used for their intended purpose (e.g., Read for reading vs. Bash cat)
- Session version field — newer versions suggest active tool management

**Noise (ignore)**:
- Tool call volume (more calls ≠ more mature)
- Specific commands run (that's CI/CD or quality territory)
- Whether Claude succeeded or failed

**Grading rule**: Score based on the **highest consistent level** seen across prompts. A single L3 prompt in a sea of L1 prompts = L1 (we grade average behavior, not peak).

---

### 2. Prompt & Context Engineering (`prompt_context_engineering`)

**What we're measuring**: Does the developer load, reference, and reuse structured context? Or start from scratch each time?

**Primary signals** (from prompt text):
- L1: No context references, rebuilds from scratch ("build an API endpoint for login")
- L2: References shared docs ("following our REST conventions from CLAUDE.md", "per our guidelines")
- L3: Assumes artifacts are pre-loaded ("based on the architecture doc you auto-loaded", "using the cached conventions")
- L4: Instructs agent to update/maintain context docs ("update /docs/api-patterns.md with the new pattern")

**Supporting signals** (from tool records):
- `Read` of `CLAUDE.md`, `docs/`, architecture files — confirms context loading
- `Write`/`Edit` of context files — confirms L4 context maintenance
- `Bash` commands that cat/read convention files

**Noise (ignore)**:
- Prompt length (long prompts ≠ good context)
- Number of files read (breadth ≠ context engineering)
- Thinking block content (Claude's planning, not developer's)

**Grading rule**: Look for **patterns of reuse**. A developer who references CLAUDE.md in 5/10 prompts is L2. A developer who mentions "auto-loaded" in 1 prompt but has no Read of CLAUDE.md in tool records = low confidence.

---

### 3. Agent Configuration (`agent_configuration`)

**What we're measuring**: Are custom agents, skills, and workflows configured? How sophisticated is the multi-step automation?

**Primary signals** (from tool records):
- L1: Only built-in tools used (Bash, Read, Write, Edit). No Skill, no Agent, no hooks.
- L2: Skill invocations present (Skill tool calls), slash commands used (local_command records)
- L3: Agent tool calls with chained workflows, error handling referenced in prompts, multiple skill invocations in sequence
- L4: Parallel Agent dispatch (multiple Agent calls in same assistant turn), specialized subagent_types (Plan, code-reviewer, etc.), sub-agents spawning further sub-agents

**Supporting signals**:
- `stop_hook_summary` — hooks configured = L2+ (custom session behavior)
- `subagents/*.meta.json` — variety of `agentType` values
- `input.run_in_background: true` — async execution = L3+
- Prompt text mentioning "/command", "skill", "workflow"

**Noise (ignore)**:
- ToolSearch calls (internal plumbing)
- Tool result content (what matters is that agents were used, not what they returned)
- Thinking blocks

**Grading rule**: This is the one sub-dimension where **tool records are primary** and prompts are supporting. Count distinct agent types, parallel dispatches, and skill diversity. A session with 0 Agent/Skill calls = L1 regardless of what prompts say.

---

### 4. CI/CD Integration (`cicd_integration`)

**What we're measuring**: Is AI connected to build systems? Do interactions reference CI pipelines, test results, deployments?

**Primary signals** (from prompt text):
- L1: No CI/CD mention ("run tests locally and help me debug")
- L2: References CI output ("here's the CI build log", "3 test failures from CI")
- L3: Instructs agent to interact with CI ("when CI fails, analyze and fix", "agent reads from GitHub Actions")
- L4: Defines closed-loop automation ("commit, test, deploy, monitor, rollback", "target SLA: 95% pass")

**Supporting signals** (from tool records):
- Bash commands: `pytest`, `npm test`, `jest`, `make test` → confirms CI awareness
- Bash commands: `gh pr create`, `git push` → confirms pipeline interaction
- Bash commands: deploy scripts → confirms deployment integration
- Tool results from CI commands (pass/fail patterns)

**Noise (ignore)**:
- Local-only test runs with no CI context (developer might just be debugging)
- `git status`, `git diff` (source control ≠ CI/CD)
- Read of test files (writing tests ≠ CI integration)

**Grading rule**: **Tool inputs** (Bash CI commands) are the primary signal — they show what actually happened. Prompts provide supporting context for intent. A Bash `pytest && gh pr create` chain = L3 regardless of prompt language. A prompt saying "fix CI failures" with no CI tool calls = low confidence (intent without action).

---

### 5. Ticketing & Planning (`ticketing_planning`)

**What we're measuring**: Do prompts reference tickets/issues? Are requirements validated before coding?

**Primary signals** (from prompt text):
- L1: No ticket references, code-first ("build the login feature")
- L2: References specific tickets ("working on ACME-234", "per the JIRA description")
- L3: Instructs agent to read from ticketing ("Agent: read ACME-234 from JIRA, parse acceptance criteria")
- L4: Autonomous triage ("monitor backlog, triage new issues, estimate story points")

**Supporting signals** (from tool records):
- TaskCreate/TaskUpdate calls (task management in session)
- Bash with task management CLI commands
- Bash/WebFetch to JIRA/Linear URLs
- MCP tool calls to ticketing systems

**Noise (ignore)**:
- Plan-mode artifacts (those are Claude's planning, not ticketing integration)
- General "plan" mentions in prompts without ticket references
- Todo items in prompts (informal ≠ ticketing system)

**Grading rule**: Look for **specific ticket identifiers** (ACME-123, T260669092) or **ticketing system names** (JIRA, Linear, Asana). Vague "plan" language without system references = L1.

---

### 6. Cross-System Connectivity (`cross_system_connectivity`)

**What we're measuring**: Does the session interact with multiple external systems? Is data pulled/pushed across system boundaries?

**Primary signals** (from prompt text):
- L1: All context manually pasted ("here's what I found: [paste from Confluence, GitHub, Slack]")
- L2: Names systems for AI to read ("read the architecture from GitHub and the ticket from JIRA")
- L3: Agent pulls from multiple systems automatically ("pull context from GitHub, JIRA, Confluence, and Slack")
- L4: Bi-directional sync ("when JIRA status changes, update GitHub PR labels")

**Supporting signals** (from tool records):
- MCP tool calls (`mcp__*`) — cross-system by definition. Common MCP servers: `postgres` (database), `github` (PRs/issues), `slack` (messaging), `linear`/`jira` (ticketing), `notion`/`confluence` (docs), `sentry` (error tracking), `grafana` (monitoring)
- WebFetch to external URLs (Google Docs, wikis, APIs)
- Bash with `gh`, `git`, `docker`, `curl` (source control, containers, APIs)
- Multiple distinct system integrations in one session

**Noise (ignore)**:
- Single-system interactions (just Git, just Bash)
- File reads within the repo (local ≠ cross-system)
- ToolSearch calls

**Grading rule**: Count **distinct external systems** accessed. 0 = L1, 1 = L1/L2 depending on prompt, 2+ = L2+, automated multi-system = L3+. The prompt determines the integration _intent_ while tool records confirm actual system access.

---

### 7. Quality Controls (`quality_controls`)

**What we're measuring**: Are AI outputs held to quality standards? Do prompts mention review gates, coverage targets, eval criteria?

**Primary signals** (from prompt text):
- L1: Generic review requests ("review this code")
- L2: Explicit quality criteria ("check against our checklist: linting, types, docstrings, coverage > 80%")
- L3: Automated eval harnesses ("run eval harness: complexity < 10, type coverage 100%, reject if fails")
- L4: Continuous scoring ("maintain quality score across every commit, auto-spawn remediation on drop")

**Supporting signals** (from tool records):
- Bash with lint/format commands: `eslint`, `flake8`, `mypy`, `black`, `prettier`, `clippy`
- Bash with coverage commands: `coverage run`, `--cov`
- Skill invocations: `review-diff`, `code-reviewer`, `simplify`
- Agent spawns for review purposes (description mentions "review")

**Noise (ignore)**:
- Test commands (testing ≠ quality gates, that's CI/CD)
- File writes (writing code ≠ quality control)
- General "fix" requests (bug fixing ≠ quality governance)

**Grading rule**: The **specificity of quality criteria** determines the level. "Review this" (vague) = L1. "Check against X, Y, Z" (criteria-based) = L2. "Auto-reject if criteria fail" (automated gates) = L3.

---

### 8. Security & Compliance (`security_compliance`)

**What we're measuring**: Is AI usage governed? Do prompts show awareness of data restrictions, compliance policies?

**Primary signals** (from prompt text):
- L1: No security mentions, potential shadow AI use
- L2: References policy ("per our AI usage policy: no PII, no API keys")
- L3: Guardrails in code ("agent should refuse PII, log to audit trail, implement blocking hook")
- L4: Policy-as-code ("embed compliance policy, detect PII regex, real-time alerts, self-remediate")

**Supporting signals** (from tool records):
- Bash with security scanning: `git-secrets`, `trufflehog`, `bandit`, `snyk`
- Hooks configured that mention security (from `stop_hook_summary`)
- Read/Write of `.gitignore`, `.env.example`, security policy files

**Noise (ignore)**:
- General code review (quality, not security)
- Permission mode settings (session plumbing)
- Authentication commands (`gcloud auth`, `ssh-keygen`) — infra setup, not policy governance

**Grading rule**: This sub-dimension is often **sparse** — most sessions won't have security-relevant prompts. Absence of security mentions = L1 (not penalizing, just default). When present, the prompt text is almost always sufficient to grade. Mark confidence as `low` if only 1 signal found.

---

### 9. Measurement & KPIs (`measurement_kpis`)

**What we're measuring**: Are AI outcomes measured? Do prompts reference metrics, dashboards, tracking?

**Primary signals** (from prompt text):
- L1: Anecdotal assessment ("I think Claude is helping the team")
- L2: Specific metrics named ("track adoption %, usage frequency, sessions/day")
- L3: Framework-level metrics ("DORA: deployment frequency, lead time, MTTR, change fail rate")
- L4: Agent-driven optimization ("agent monitors KPIs, analyzes root cause, recommends optimizations")

**Supporting signals** (from tool records):
- MCP calls to Grafana, Datadog, dashboards, or similar analytics systems
- Bash/WebFetch to dashboards or metrics endpoints
- Tool results containing metric data

**Noise (ignore)**:
- Session duration/turn_duration (infrastructure metrics, not AI outcome metrics)
- API error counts (infrastructure, not developer measurement maturity)
- Token usage (cost metric, not outcome metric)

**Grading rule**: Like security, this is **sparse** — most coding sessions won't discuss KPIs. Default to L1 with `low` confidence if no signals found. Prompts are the primary signal.

---

### 10. Ways of Working (`ways_of_working`)

**What we're measuring**: Does the developer follow documented team conventions for AI use?

**Primary signals** (from prompt text):
- L1: Ad-hoc, individual usage ("Claude, help me debug this")
- L2: References team conventions ("per our Ways of Working documented in README: start by loading CLAUDE.md")
- L3: Defines review gates and escalation ("code → /review gate → merge approval → deploy; on failure, alert Slack")
- L4: Shared accountability ("agents and humans share accountability; human spot-checks weekly")

**Supporting signals** (from session config):
- Hooks configured (from `stop_hook_summary`) — implies structured workflow
- Skill usage patterns — consistent skill invocation suggests team conventions
- Slash commands used — suggests documented workflow

**Supporting signals** (from tool records):
- Read of README, CONTRIBUTING, CLAUDE.md at session start — suggests following a protocol
- Consistent patterns across multiple sessions from same user

**Noise (ignore)**:
- Prompt style/formatting (some people are terse, doesn't mean no conventions)
- Number of tool calls (workflow volume ≠ documented ways of working)
- Session length

**Grading rule**: Look for **explicit references to documentation or process**. "Per our docs" = L2. "Review gate → escalation" = L3. Pure ad-hoc usage with no process references = L1.

---

### 11. Accountability & Ownership (`accountability_ownership`)

**What we're measuring**: Is there a named AI owner? Do prompts show clear decision authority?

**Primary signals** (from prompt text):
- L1: No ownership mentioned, individual results
- L2: Names an owner ("Sarah is our AI Champion", "owned by tech lead")
- L3: Team ownership with KPIs ("team collectively owns agent output quality; tied to sprint metrics")
- L4: Team+agent SLAs ("team + agents own delivery end-to-end; SLA: 99% uptime, <5min MTTR")

**Supporting signals** (from session config):
- `user-name` / `team-name` parameters used consistently (identity-aware usage)
- Session entrypoint patterns (CLI vs. IDE — different organizational maturity)

**Noise (ignore)**:
- Git author info (identity ≠ ownership accountability)
- Who ran the session (presence ≠ ownership)
- Tool results

**Grading rule**: This is **almost entirely prompt-based**. The developer either mentions ownership structures or they don't. Very sparse in most sessions — default L1 with `low` confidence.

---

### 12. Scalability & Knowledge Transfer (`scalability_knowledge_transfer`)

**What we're measuring**: Can new developers ramp up quickly? Are playbooks, prompt libraries, and structured onboarding in place?

**Primary signals** (from prompt text):
- L1: Tribal knowledge, no documentation ("just watch how I use Claude")
- L2: Onboarding materials referenced ("new dev checklist: read README, review example prompts, pair with Sarah")
- L3: Reusable playbooks ("access prompt library, playbooks, module configs; self-serve in 1 week")
- L4: Agent-guided onboarding ("new team: download CLAUDE.md template + configs; agents guide setup")

**Supporting signals** (from tool records):
- Agent delegation with `description` mentioning reusable patterns
- Write to shared docs/playbooks/templates
- Read of onboarding/getting-started files
- Skill invocations that reference shared team skills

**Noise (ignore)**:
- Personal notes or one-off docs
- Agent count (more agents ≠ better knowledge transfer)
- Session complexity

**Grading rule**: Look for **references to reusable artifacts** (playbooks, templates, libraries, onboarding docs). Most sessions won't mention these — default L1 with `low` confidence.

---

## Confidence Calibration

After grading, assign confidence based on evidence quality:

| Confidence | Criteria |
|---|---|
| `high` | 3+ records routed to this sub-dimension, with explicit keyword matches. Primary signal is clear and unambiguous. Supporting signals corroborate. |
| `medium` | 1-2 records with explicit matches, OR 3+ records with implied/indirect signals. Primary and supporting signals may not fully align. |
| `low` | 0 records routed (using default L1), OR 1 record with ambiguous signal. No supporting signals available. |

### Cross-Validation Rules

When a prompt claims a practice but tool records contradict it:
- Prompt says "we standardize on Claude" but session shows only ad-hoc usage → `medium` confidence, don't downgrade level (they may standardize outside this session)
- Prompt says "agent reads CI" but no CI tool calls exist in session → `low` confidence, keep the level (the capability may exist even if not exercised this session)
- Tool records show heavy Agent/Skill use but prompts never mention workflows → bump `agent_configuration` to at least L2 (actions speak louder than words)

### Sparse Sub-Dimensions

Some sub-dimensions will have **zero routed records** in most sessions. This is expected and normal:
- `security_compliance` — only relevant when working with sensitive data
- `measurement_kpis` — only relevant when discussing metrics/tracking
- `accountability_ownership` — only relevant when discussing team structure
- `scalability_knowledge_transfer` — only relevant when discussing onboarding/scaling

For these, assign **L1 with `low` confidence** and note: "No signals observed in this session." Do NOT penalize — absence of evidence is not evidence of absence.

---

## Summary: What Each Grader Needs

| Sub-Dimension | Primary Source | What To Look For | What To Ignore |
|---|---|---|---|
| `ai_tool_adoption` | Prompts (default bucket) | Tool selection reasoning, standardization mentions | Tool call volume, session length |
| `prompt_context_engineering` | Prompts + Read tool calls | Context file references, convention mentions, doc loading | Prompt length, file count |
| `agent_configuration` | Tool records (Agent, Skill, hooks) | Agent/Skill diversity, parallel dispatch, hook config | ToolSearch calls, tool result content |
| `cicd_integration` | Prompts + Bash CI commands | CI system mentions, test/deploy commands | Local git commands, file edits |
| `ticketing_planning` | Prompts + Task tool calls | Ticket IDs, system names (JIRA, Linear), requirements | Vague "plan" language, todo lists |
| `cross_system_connectivity` | Tool records (MCP, WebFetch) + Prompts | Distinct systems accessed, multi-system mentions | Single-repo file operations |
| `quality_controls` | Prompts + lint/review tool calls | Quality criteria specificity, review gates | General "fix" requests, test runs |
| `security_compliance` | Prompts (sparse) | Policy references, PII mentions, guardrail design | Auth commands, permission settings |
| `measurement_kpis` | Prompts (sparse) | Named metrics, frameworks, dashboards | Token/latency infra metrics |
| `ways_of_working` | Prompts + session config | Process references, documentation mentions | Prompt style, session volume |
| `accountability_ownership` | Prompts (sparse) | Named owners, SLAs, team responsibility | Git author, session user |
| `scalability_knowledge_transfer` | Prompts (sparse) | Playbooks, templates, onboarding references | Personal notes, agent count |
