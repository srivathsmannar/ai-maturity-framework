# Maturity Assessment Ground Truth — Multi-Signal Evidence

Signal patterns that indicate maturity level (L1-L4) for each of the 12 sub-dimensions. Each level shows **realistic examples** drawn from actual Claude Code session data: developer prompts, tool usage patterns, tool inputs, agent delegation, and session configuration.

**Key principle**: Not all sub-dimensions are best assessed from prompt text. Some (like Agent Configuration) are primarily assessed from tool usage patterns. Each sub-dimension below identifies its **primary signal source** and shows what real evidence looks like.

---

## 1. Capability Dimension

### 1.1 AI Tool Adoption

Measures: How intentionally are AI tools selected and used? Do interactions show awareness of tool capabilities within the platform?

**Primary signal**: Prompt text (how the developer frames requests)
**Supporting signals**: Tool usage diversity, session metadata

**Important**: "Tool adoption" at L3+ is NOT about choosing between competing AI providers (Claude vs. Copilot). It's about selecting the right tools, MCPs, skills, and capabilities _within_ the AI platform for each task.

**L1 — Assisted: Ad-hoc use; generic requests**

*Prompt evidence:*
- "help me debug this"
- "fix the tests"
- "what does this code do?"
- Generic requests with no indication of why this tool or approach

*Tool evidence:*
- Only basic tools used (Bash, Read)
- No Skill or Agent invocations
- Session shows single-tool interaction

*Pattern*: Developer treats AI as a search box. No awareness of capabilities beyond basic Q&A.

**L2 — Integrated: Deliberate tool choice; team standardization**

*Prompt evidence:*
- "can you run the query in notebook?"
- "use the sql-query skill for this"
- "look into the systems/docs if necessary"
- Developer knows specific tools exist and asks for them by name

*Tool evidence:*
- Uses appropriate tools for tasks (Read for files, Bash for commands)
- Invokes specific MCP tools or skills by name
- Session version is current (active tool management)

*Pattern*: Developer knows what tools are available and selects them consciously. Uses `Read` instead of `Bash cat`.

**L3 — Agentic: Right tool for right task; capability-aware routing**

*Prompt evidence:*
- "use subagents to answer different" (tasks dispatched to parallel agents)
- "please put both queries in a new md file" (uses Write for docs, Bash for queries)
- "can you create a document... don't share just create" (uses Google Docs MCP for doc creation, not Write for .md)

*Tool evidence:*
- Uses `Agent` tool with specialized `subagent_type` values (e.g., `codebase-search` for code search, `Plan` for planning)
- Routes to the right Skill for each task (`sql-query` for SQL, `google-docs` for docs, `docs-search` for wikis)
- MCP tools used for cross-system access rather than manual curl/WebFetch

*Pattern*: Developer picks the right tool _within_ the platform based on task. Sends code search to code-search agents, SQL to query skills, docs to Google Docs MCP.

**L4 — Autonomous: Tools selected automatically based on policy**

*Prompt evidence:*
- "implement the following plan:" (hands off a complete plan for autonomous execution)
- "do these three tasks (no need to coordinate)" (trusts autonomous task decomposition)

*Tool evidence:*
- Agent tool dispatches with `run_in_background: true` (async task execution)
- Multiple Agent calls in a single assistant turn (parallel autonomous dispatch)
- Agents themselves spawn sub-agents in their sessions
- Session uses 5+ distinct tool types with clear purpose separation

*Pattern*: Developer sets intent and constraints; tool selection happens autonomously. Session shows sophisticated tool orchestration without per-tool prompting.

---

### 1.2 Prompt & Context Engineering

Measures: Do prompts load and reference shared context, or start from scratch each time?

**Primary signal**: Prompt text (context references)
**Supporting signals**: Tool inputs (Read of context files), file paths accessed

**L1 — Assisted: One-off prompts; no context reuse**

*Prompt evidence:*
- "build an API endpoint for user login"
- "how do i add files to put as context?"
- "where do i run, my terminal? or somewhere else"
- No reference to existing docs, architecture, or prior work

*Tool evidence:*
- No reads of CLAUDE.md, README, or architecture files
- No context loaded at session start
- Developer provides all context inline (pasting code/text into prompts)

*Pattern*: Every session starts cold. Developer manually provides all context or asks basic setup questions.

**L2 — Integrated: Shared docs and conventions referenced**

*Prompt evidence:*
- "following our REST conventions from CLAUDE.md"
- "per the design doc we wrote last week"
- "read this maybe it will give answer" (shares wiki URL for context)
- Passes URLs/file paths as structured context

*Tool evidence:*
- Read of `CLAUDE.md`, `README.md`, or `docs/` files early in session
- Developer shares Google Docs / wiki URLs for AI to read
- Prompt references "the doc" or "our conventions"

*Pattern*: Developer knows context exists and points the AI to it. Context comes from shared team resources, not just personal knowledge.

**L3 — Agentic: Structured context auto-feeds into sessions**

*Prompt evidence:*
- Prompts assume context is already available ("based on the architecture doc")
- Session starts with context already loaded (CLAUDE.md auto-read by hooks)
- Developer doesn't manually load context — it's part of the workflow

*Tool evidence:*
- Session hooks auto-load context files at start (visible in `stop_hook_summary`)
- `.claude/settings.json` configures project-level context
- Read of structured artifacts (not ad-hoc docs) happens automatically

*Pattern*: Context loading is automated. Developer's prompts assume the AI already knows the codebase conventions because context was pre-loaded.

**L4 — Autonomous: AI maintains and evolves context documents**

*Prompt evidence:*
- "update the doc with new findings" (AI writes back to shared context)
- "can you incorporate that .md file into the google doc?"
- Developer instructs AI to maintain living documents

*Tool evidence:*
- Write/Edit of CLAUDE.md, convention files, or architecture docs
- Google Docs MCP used to update shared team documentation
- Context files show edit history from AI sessions (AI is a contributor to shared knowledge)

*Pattern*: AI is not just a context consumer — it maintains and updates shared context for future sessions and team members.

---

### 1.3 Agent Configuration

Measures: Are custom agents, skills, and workflows configured? How multi-step and autonomous are they?

**Primary signal**: Tool records (Agent, Skill, hooks)
**Supporting signals**: Prompt text (references to commands/skills), session config

**L1 — Assisted: Only built-in tools; no custom configuration**

*Prompt evidence:*
- Direct instructions for each step ("run the tests, then read the output, then fix")
- No mention of /commands, skills, or workflows

*Tool evidence:*
- Only basic tools: `Bash`, `Read`, `Write`, `Edit`
- Zero `Skill` invocations
- Zero `Agent` invocations
- No hooks configured (empty `stop_hook_summary` or no hook records)

*Pattern*: Developer manually orchestrates every step. No automation beyond basic tool use.

**L2 — Integrated: Skills and slash commands in use**

*Prompt evidence:*
- "/review my changes"
- "use the sql-query skill"
- References specific skill names

*Tool evidence:*
- `Skill` tool invoked (e.g., `google-docs`, `sql-query`, `docs-search`)
- Slash commands used (visible in `local_command` system records)
- 1-3 distinct skills used per session
- `stop_hook_summary` shows hooks configured (session start/stop hooks)

*Pattern*: Developer has configured skills and uses them for specific tasks. Single-purpose invocations, not chained.

**L3 — Agentic: Multi-step agent workflows with specialized delegation**

*Prompt evidence:*
- "use subagents to answer different" (parallel task delegation)
- "can you divide the above, add in a new section" (structured multi-step workflow)
- References chained workflows or skill sequencing

*Tool evidence:*
- `Agent` tool used with specific `subagent_type` values:
  - `codebase-search` for code exploration
  - `Plan` for architecture planning
  - `code-reviewer` for review
- Multiple Agent calls in a session (3+)
- Skills chained: e.g., `brainstorming` → `task-executor` → `subagent-driven-development`
- Skill invocations with structured args

*Real example from session:*
```
Agent(subagent_type="meta_codesearch:code_search", description="Read L2 product staging pipeline")
Agent(subagent_type="general-purpose", description="Analyze specified_in_spec approximation error")  
Agent(subagent_type="general-purpose", description="Draft enhanced query with target parsing")
```

*Pattern*: Developer delegates to specialized agents. Different agent types for different tasks. Workflows have multiple steps.

**L4 — Autonomous: Agents compose tasks, spawn sub-agents, self-correct**

*Prompt evidence:*
- "implement the following plan:" (hands off entire plan)
- "do these three tasks (no need to coordinate)"
- Minimal per-step prompting; developer sets goals, not steps

*Tool evidence:*
- Agents spawn their own sub-agents (visible in sub-agent JSONL files containing further Agent calls)
- `run_in_background: true` used for parallel execution
- 5+ Agent calls per session
- Agent descriptions show task decomposition ("Fix enhanced query column alias error" — agent self-identified the problem)
- Skills invoke other skills or spawn agent workflows
- Session shows extended autonomous execution spans (many tool calls between user prompts)

*Pattern*: Developer gives a goal; agents decompose, delegate, and self-correct. Sub-agents in sub-agents. Background execution. Minimal human steering after initial prompt.

---

## 2. Integration Dimension

### 2.1 CI/CD Integration

Measures: Is AI connected to build, test, and deployment systems?

**Primary signal**: Tool inputs (Bash commands related to CI/CD)
**Supporting signals**: Prompt text (CI references), tool results

**L1 — Assisted: No CI/CD connection; manual workflows**

*Prompt evidence:*
- "run tests locally and help me debug"
- "this test is failing, here's the output: [paste]"
- Developer manually copies test output into the prompt

*Tool evidence:*
- No CI-related Bash commands (`pytest`, `gh pr create`, `npm test`)
- No references to CI systems in any tool input
- Developer pastes error output directly into prompts

*Pattern*: AI is disconnected from build systems. Developer is the bridge between CI and AI.

**L2 — Integrated: AI runs tests and reads CI output**

*Prompt evidence:*
- "the CI is failing, can you look at it?"
- "i'm trying to run the query but is extremely slow"
- Developer references CI/test systems but still manually directs

*Tool evidence:*
- Bash commands run tests: `pytest tests/`, `npm test`
- Bash reads build logs or test output
- Developer triggers test runs through AI but reviews results manually

*Pattern*: AI can execute test/build commands. Developer still interprets results and decides next steps.

**L3 — Agentic: Agents interact with CI pipeline autonomously**

*Prompt evidence:*
- "run the tests and if they fail, fix the issues"
- "can you try running it yourself?" (trusts AI to execute CI commands)
- Prompt assumes AI will handle the test→fix→retest cycle

*Tool evidence:*
- Bash chains: `pytest tests/ && gh pr create --draft` (test + submit pipeline)
- Agent spawned to run and fix tests: `Agent(description="Fix enhanced query column alias error")`
- Tool results show test output parsed and acted upon
- Skill invocations: `ci-signals`, `fix-diff`, `ci-data`

*Real example from session:*
```
Bash: "pytest tests/ && gh pr create --draft"
Agent: description="Run Citadel target query"
Agent: description="Run JSON parsing query"  
```

*Pattern*: AI reads CI output, diagnoses failures, and applies fixes without developer manually interpreting logs.

**L4 — Autonomous: Closed-loop CI/CD with agent ownership**

*Prompt evidence:*
- "implement the following plan" (entire CI workflow delegated)
- Developer sets SLA targets, not step-by-step instructions
- Rollback/monitoring mentioned as agent responsibilities

*Tool evidence:*
- Full commit → test → submit → monitor cycle in tool records
- Agents handle CI failures autonomously (spawning fix agents on failure)
- `gh pr create`, `gh pr merge`, deployment commands in Bash
- Background agents monitoring for CI results

*Pattern*: Developer defines the desired outcome and quality bar. Agents handle the full commit-test-deploy-monitor cycle with self-remediation on failure.

---

### 2.2 Ticketing & Planning

Measures: Do interactions reference tickets/issues? Are requirements connected to implementation?

**Primary signal**: Prompt text (ticket references)
**Supporting signals**: Tool inputs (task/ticket commands), tool results

**L1 — Assisted: Code-first; no ticket connection**

*Prompt evidence:*
- "build the login feature"
- "fix the tests"
- No ticket IDs, no requirements, no acceptance criteria
- Developer jumps straight to coding

*Tool evidence:*
- No TaskCreate/TaskUpdate calls
- No task management commands
- No JIRA/Linear URLs in any input

*Pattern*: AI work is disconnected from project tracking. No traceability between tasks and code.

**L2 — Integrated: Tickets referenced; requirements inform work**

*Prompt evidence:*
- "I'm working on ENG-1234" (references specific task ID)
- "https://linear.app/team/issue/ENG-1234" (links to task)
- "per the design doc" (work linked to planning artifact)
- Developer connects implementation to a ticket/task

*Tool evidence:*
- WebFetch/MCP of ticket URLs
- Prompt contains task ID patterns (T\d+, ACME-\d+)
- Read of requirements/spec documents

*Real example from session:*
```
Prompt: "this is all a bit too complex. all i need is a query that breaks down CI demand by team. https://linear.app/team/issue/ENG-1234"
```

*Pattern*: Developer grounds AI work in tracked tasks. Implementation connects back to requirements.

**L3 — Agentic: AI reads and structures tasks from ticketing systems**

*Prompt evidence:*
- "read the task and break down the acceptance criteria"
- "implement the following plan: # Plan: ENG-1234" (task ID embedded in structured plan)
- Developer provides task, AI structures the implementation

*Tool evidence:*
- Agent spawned to parse requirements: `Agent(description="Revise pipeline plan with L2 logic")`
- TaskCreate/TaskUpdate used to track sub-tasks
- MCP tools access ticketing system directly
- Skill: `tasks` used for task management

*Pattern*: AI reads requirements from the system and produces structured implementation artifacts (plans, breakdowns, acceptance criteria).

**L4 — Autonomous: AI triages, plans, and validates against requirements**

*Prompt evidence:*
- "do these three tasks" (hands off multiple work items)
- "make sure to incorporate those pieces into one entire big query" (validates completeness)
- Developer sets goals; AI manages the work breakdown

*Tool evidence:*
- Multiple task tracking calls in session
- Agent validates output against original requirements
- Automated test validation tied to acceptance criteria
- Work items created, assigned to agents, and marked complete within session

*Pattern*: AI manages the full task lifecycle — from understanding requirements to validating completion against acceptance criteria.

---

### 2.3 Cross-System Connectivity

Measures: Does the session interact with multiple external systems? Is data pulled/pushed across boundaries?

**Primary signal**: Tool records (MCP calls, WebFetch, multi-system Bash)
**Supporting signals**: Prompt text (system names), tool results

**L1 — Assisted: Single-system; manual context bridging**

*Prompt evidence:*
- All context pasted into prompts
- "here's what I found: [paste]"
- Developer manually copies between systems

*Tool evidence:*
- Only local file operations (Read, Write, Bash on local files)
- No MCP tool calls
- No WebFetch/WebSearch
- No external CLI commands

*Pattern*: AI works in isolation. Developer manually bridges information between systems.

**L2 — Integrated: AI reads from 2+ systems**

*Prompt evidence:*
- "read this maybe it will give answer" (shares wiki URL)
- "can you create a document" + "run the query" (two different systems)
- Developer points AI at multiple system endpoints

*Tool evidence:*
- MCP tools for reading: `mcp__postgres` (database), `mcp__github` (PRs/issues), `mcp__notion` (docs), `mcp__slack` (messages)
- WebFetch to Google Docs, wiki pages, or external URLs
- Bash with `gh` commands (source control system)
- 2-3 distinct external system interactions

*Real example from session:*
```
WebFetch: "https://docs.google.com/document/d/1hw.../export?format=txt"
Skill: "sql-query" (SQL data warehouse)
Skill: "wiki-query" (internal wiki)
```

*Pattern*: AI reads from multiple systems in a single session. Developer directs which systems to access.

**L3 — Agentic: AI reads and writes across systems; data flows between them**

*Prompt evidence:*
- "can you update the google doc?" (write-back to external system)
- "incorporate that .md file into the google doc" (cross-system data transfer)
- "run the queries in the doc inside this query notebook" (data flows between systems)

*Tool evidence:*
- MCP tools for both read AND write: `mcp__postgres` (query) + `mcp__notion` (write results), `mcp__github` (read PR) + `mcp__jira` (update ticket), `mcp__slack` (post summary)
- Data flows between systems: query result → Google Doc, database → Notion, GitHub PR → Jira ticket
- 4+ distinct system integrations
- Agent spawned for cross-system task: `Agent(description="Combine Google Docs into one")`

*Real example from session:*
```
Skill: "google-docs" → Create new document
Skill: "sql-query" → Run CI demand query  
Skill: "notebook" → Run queries in query notebook
Skill: "wiki-query" → Read Citadel docs
Agent: "Combine Google Docs into one"
```

*Pattern*: AI acts as a data conduit between systems. Information flows in both directions. Multiple system writes, not just reads.

**L4 — Autonomous: Bi-directional sync; event-driven cross-system workflows**

*Prompt evidence:*
- Minimal system-specific instructions; AI infers which systems to use
- "update the doc with new findings" (AI decides where and how)

*Tool evidence:*
- 5+ distinct systems accessed in session
- Automated workflows that span systems (query data → analyze → write results → update docs)
- Agent sub-sessions that access different systems for their tasks
- Cross-system state maintenance (e.g., query results update docs, docs inform next queries)

*Pattern*: AI autonomously decides which systems to access and maintains state across them. Systems are not just accessed — they're orchestrated.

---

## 3. Governance Dimension

### 3.1 Quality Controls

Measures: Are AI outputs held to quality standards? Are there review gates, test requirements, or eval criteria?

**Primary signal**: Tool inputs (lint/review commands)
**Supporting signals**: Prompt text (quality criteria), skill invocations

**L1 — Assisted: No quality gates; accept AI output as-is**

*Prompt evidence:*
- "looks good" (accepts without review)
- "fix this bug" (no quality criteria specified)
- No mention of review, testing, or validation requirements

*Tool evidence:*
- No lint/format commands
- No `review-diff`, `code-reviewer`, or `simplify` skills
- No test commands before committing

*Pattern*: AI output is accepted without structured review. Developer eyeballs it and moves on.

**L2 — Integrated: Quality checks run; criteria exist**

*Prompt evidence:*
- "make sure tests pass before we commit"
- "run lint on these changes"
- "check that the types are correct"
- Developer specifies quality checks to run

*Tool evidence:*
- Bash with `eslint`, `mypy`, `flake8`, `black`, `prettier`
- Test commands run: `pytest`, `npm test`
- Skill: `review-diff` or `simplify` invoked
- Quality checks happen before final output

*Pattern*: Developer has quality criteria and asks AI to check against them. Lint, type-check, test before finalizing.

**L3 — Agentic: Automated review gates in workflow**

*Prompt evidence:*
- "please stop and write a report on what you tried and why it didn't work" (demands accountability)
- Prompt structures workflows with checkpoints
- References eval criteria or acceptance thresholds

*Tool evidence:*
- Skill: `code-reviewer` or `review-diff` used automatically
- Agent spawned specifically for review: `Agent(subagent_type="code-reviewer")`
- Test → review → commit sequence enforced in tool records
- `verification` skill used

*Pattern*: Review gates are built into the workflow. AI runs quality checks as part of its process, not because developer asked each time.

**L4 — Autonomous: Continuous quality with auto-remediation**

*Prompt evidence:*
- Quality targets set once, enforced throughout session
- Developer sets SLAs or quality bars; AI maintains them

*Tool evidence:*
- Agents self-spawn to fix quality issues (visible in agent chains)
- Quality skills run automatically at session hooks
- Failed quality checks trigger automatic fix → recheck cycles
- `stop_hook_summary` includes quality-checking hooks

*Pattern*: Quality is enforced by policy, not per-request. AI detects regressions and fixes them without developer prompting.

---

### 3.2 Security & Compliance

Measures: Is AI usage governed? Do interactions show awareness of data restrictions and compliance?

**Primary signal**: Prompt text (policy references)
**Supporting signals**: Tool inputs (security commands), session hooks

**L1 — Assisted: No policy awareness; potential shadow AI**

*Prompt evidence:*
- "help me debug the payment processing code" (no data sensitivity awareness)
- No mention of restrictions, PII, or compliance
- Developer pastes potentially sensitive data without flagging it

*Tool evidence:*
- No security scanning tools used
- No hooks related to security
- No `.gitignore` or secrets-related file operations

*Pattern*: No evidence of security consciousness in the AI workflow.

**L2 — Integrated: Policy exists and is referenced**

*Prompt evidence:*
- "make sure there's no PII in the output"
- "don't include API keys in the response"
- "per our security policy, redact customer IDs"
- Developer explicitly calls out restrictions

*Tool evidence:*
- Bash with `git-secrets`, `trufflehog`, or `bandit`
- Read of `.env.example` (not `.env` — knows to keep secrets out)
- Prompt avoids pasting credentials directly

*Pattern*: Developer knows the rules and mentions them. Security is manual but conscious.

**L3 — Agentic: Guardrails enforced programmatically**

*Prompt evidence:*
- References hooks or automated checks for security
- "implement a hook that blocks sensitive data"

*Tool evidence:*
- Session hooks include security scanning (visible in `stop_hook_summary`)
- Agent-security-guardrails plugin active
- Automated pre-commit hooks that check for secrets
- Security-related skills invoked as part of workflow

*Pattern*: Security checks are automated — hooks, plugins, or agents enforce them without developer manually requesting each time.

**L4 — Autonomous: Policy-as-code; real-time enforcement**

*Tool evidence:*
- Security hooks block and remediate automatically
- Agents detect policy violations and self-correct
- Audit trail of blocked/redacted content in session
- Compliance checks integrated into every tool call

*Pattern*: Security is embedded in the infrastructure. Violations are detected, blocked, and remediated automatically.

---

### 3.3 Measurement & KPIs

Measures: Are AI outcomes measured? Do prompts reference metrics, dashboards, or performance tracking?

**Primary signal**: Prompt text (metric references)
**Supporting signals**: Tool results (dashboard/metric data)

**Note**: This sub-dimension is **sparse** in most sessions. Absence = L1 with low confidence.

**L1 — Assisted: No metrics; anecdotal**

*Prompt evidence:*
- No mention of measuring AI effectiveness
- "is this tool helpful?" (anecdotal, no data)

*Pattern*: No measurement. AI value is assumed, not quantified.

**L2 — Integrated: Specific metrics named and tracked**

*Prompt evidence:*
- "how many sessions did the team run this week?"
- "track adoption rate across the team"
- Developer asks about or references specific metrics

*Tool evidence:*
- MCP tools: `mcp__grafana` (dashboard queries), `mcp__sentry` (error tracking), Datadog API via WebFetch
- Bash commands that query session counts or usage stats

*Pattern*: Developer thinks about AI effectiveness in measurable terms.

**L3 — Agentic: Framework-level KPIs tracked automatically**

*Prompt evidence:*
- References DORA metrics, velocity, cycle time
- "compare pre-AI vs post-AI baselines"
- Metrics connected to engineering outcomes, not just adoption

*Tool evidence:*
- Automated dashboard queries
- Skill: `grafana-metrics`, `analytics`, `datadog` for AI-related metrics
- KPI data flows into reports or documents

*Pattern*: AI outcomes are measured with engineering frameworks. Data collection is automated.

**L4 — Autonomous: AI optimizes based on KPI feedback**

*Tool evidence:*
- Agents query metrics and adjust behavior based on results
- Feedback loops visible in session (metric check → action → re-check)
- AI recommends process changes based on KPI trends

*Pattern*: AI is not just measured — it uses its own metrics to improve.

---

## 4. Execution Ownership Dimension

### 4.1 Ways of Working

Measures: Does the developer follow documented team conventions for AI use?

**Primary signal**: Prompt text (process references)
**Supporting signals**: Session config (hooks), tool usage patterns

**L1 — Assisted: Ad-hoc, individual usage**

*Prompt evidence:*
- "help me debug this"
- "how do i add files to put as context?" (learning as they go)
- No references to team process or documentation

*Tool evidence:*
- No consistent pattern across prompts
- No hooks configured
- No CLAUDE.md loaded
- Session structure is reactive (respond to errors, not follow a plan)

*Pattern*: Developer uses AI opportunistically with no structured approach.

**L2 — Integrated: Team conventions exist and are followed**

*Prompt evidence:*
- "per our guidelines" or "following our team's process"
- References README, CLAUDE.md, or team wiki
- Consistent session structure (context loading → planning → execution)

*Tool evidence:*
- CLAUDE.md read at session start
- Hooks configured for consistent session behavior
- Multiple sessions from same user show consistent patterns

*Pattern*: Developer follows a documented workflow. Sessions have predictable structure.

**L3 — Agentic: Review gates and escalation protocols**

*Prompt evidence:*
- "please stop and write a report on what you tried and why it didn't work" (structured accountability)
- Workflow has explicit checkpoints and review steps
- Escalation paths mentioned ("if this fails, do X")

*Tool evidence:*
- Skill: `review-diff` or `code-reviewer` used at defined points
- Agent workflow follows plan → implement → review → commit pattern
- `verification` used
- Handoff protocols visible (code → review → approval gates)

*Pattern*: Workflow has defined gates. Work doesn't proceed without review. Failures trigger escalation, not ad-hoc retry.

**L4 — Autonomous: Shared human-agent accountability**

*Prompt evidence:*
- Developer sets oversight intervals, not per-step instructions
- "implement the following plan" with structured checkpoints built in
- Human reviews are periodic spot-checks, not per-action approvals

*Tool evidence:*
- Agent workflows run autonomously for extended periods
- Background execution (`run_in_background: true`)
- Context compaction boundaries show long autonomous runs
- Session hooks enforce oversight at defined intervals

*Pattern*: Agents execute autonomously within guardrails. Human oversight is structured and periodic, not constant.

---

### 4.2 Accountability & Ownership

Measures: Is there clear ownership of AI-assisted work?

**Primary signal**: Prompt text (ownership references)
**Supporting signals**: Session metadata (user/team identity)

**Note**: This sub-dimension is **sparse** in most sessions. Absence = L1 with low confidence.

**L1 — Assisted: No ownership structure**

*Prompt evidence:*
- No mention of who owns AI outcomes
- Individual usage with no team context
- No `--team-name` or `--user-name` consistency

*Pattern*: AI work is unattributed. No one is accountable for quality.

**L2 — Integrated: Named owner or champion**

*Prompt evidence:*
- "Sarah manages our CLAUDE.md"
- "check with the team lead before merging AI-generated code"
- References a person responsible for AI practices

*Tool evidence:*
- Consistent `--user-name` and `--team-name` usage across sessions
- Session patterns show centralized CLAUDE.md management

*Pattern*: Someone owns AI practices for the team. Clear decision authority.

**L3 — Agentic: Team-level ownership with metrics**

*Prompt evidence:*
- "the team owns the quality of agent output"
- AI work tracked in team metrics/sprint boards
- Quality tied to team performance, not individual

*Tool evidence:*
- Task/ticket creation tied to team projects
- Review workflows involve team-level gates
- Agent output quality tracked systematically

*Pattern*: Team collectively owns AI output quality. KPIs and metrics create accountability.

**L4 — Autonomous: Team+agent partnership with SLAs**

*Prompt evidence:*
- SLAs defined for AI-assisted delivery
- Structured escalation when quality degrades
- Shared ownership model explicitly described

*Pattern*: Measured accountability with SLAs. Team and agents share responsibility for outcomes.

---

### 4.3 Scalability & Knowledge Transfer

Measures: Can new developers ramp up on AI usage quickly? Are practices shareable?

**Primary signal**: Prompt text (onboarding/playbook references)
**Supporting signals**: Tool inputs (shared artifact creation), agent delegation patterns

**Note**: This sub-dimension is **sparse** in most sessions. Absence = L1 with low confidence.

**L1 — Assisted: Tribal knowledge; nothing documented**

*Prompt evidence:*
- "how do i add files to put as context?" (basic discovery)
- "trying to confirm i installed 10x engineer" (trial-and-error onboarding)
- Knowledge lives in individuals, not artifacts

*Tool evidence:*
- No reads of onboarding docs or playbooks
- No writes to shared knowledge artifacts
- Session shows learning-by-doing, not following a guide

*Pattern*: New users figure things out on their own. No structured path.

**L2 — Integrated: Onboarding materials and examples exist**

*Prompt evidence:*
- References setup guide or getting-started docs
- "follow the README for Claude setup"
- Shared example prompts or templates mentioned

*Tool evidence:*
- Read of onboarding docs, CLAUDE.md templates, or team wikis
- Writes to shared documentation (contributing back)
- Skill: `init` used to create CLAUDE.md from template

*Pattern*: Documentation exists and new users can follow it. Examples are shared.

**L3 — Agentic: Reusable playbooks and pattern libraries**

*Prompt evidence:*
- References /playbook, /template, or shared skill library
- "new dev gets access to the prompt library"
- Self-service ramp-up path documented

*Tool evidence:*
- Multiple shared skills used consistently
- Agent descriptions reference reusable patterns
- Writes to shared playbooks or pattern libraries
- Skill: `skill-builder` or `skill-sharing` used

*Pattern*: Patterns are codified into reusable artifacts (skills, playbooks). New developers can self-serve.

**L4 — Autonomous: Self-service enablement; AI guides new users**

*Prompt evidence:*
- "agents guide initial setup"
- "within 1 day, team is productive"
- AI itself helps new users ramp up

*Tool evidence:*
- Agents configured to assist with onboarding
- Template CLAUDE.md and skill configs downloadable and self-contained
- New team sessions show productivity within first session (no multi-session ramp)

*Pattern*: Onboarding is automated. Agents teach new users. Teams adopt independently with minimal human handholding.

---

## How to Use This Ground Truth

### Multi-Signal Assessment Process

For each developer/session, extract and analyze evidence across signal types:

1. **Extract prompt records**: All non-meta `user` messages without `toolUseResult`
2. **Extract tool records**: All `tool_use` blocks from `assistant` messages
3. **Extract agent records**: All `Agent` tool calls + sub-agent meta files
4. **Extract session config**: Hook summaries, slash commands, permission settings
5. **Route each record** to one sub-dimension per the [Signal Grading Guide](SIGNAL_GRADING_GUIDE.md)
6. **Grade each sub-dimension** based on routed evidence
7. **Assign confidence** based on evidence quantity and quality

### Realistic Calibration Notes

- **Developers don't narrate their maturity.** A L3 developer doesn't say "I'm routing tasks to specialized agents" — they just say "use subagents to answer different." The maturity signal is in _what they do_, not how they describe it.
- **Tool records often carry stronger signal than prompts.** For `agent_configuration`, `cicd_integration`, and `cross_system_connectivity`, the tool usage pattern is more reliable than prompt text.
- **Most sessions are sparse for Governance and Execution Ownership.** These sub-dimensions require specific contexts (security discussions, metric reviews, onboarding). Default to L1 with low confidence, not penalizing.
- **Grade average behavior, not peak.** One L3 prompt in a session of L1 prompts = L1. Look for consistent patterns.
- **Absence ≠ low maturity.** A session focused on debugging won't show ticketing signals. That doesn't mean the developer doesn't use tickets — it means this session doesn't provide evidence.

### Confidence Levels

- **High**: 3+ records routed to this sub-dimension with explicit, unambiguous signals. Primary and supporting evidence align.
- **Medium**: 1-2 records with clear signals, OR 3+ records with indirect/implied signals. Some alignment between primary and supporting.
- **Low**: 0 records routed (default L1), OR 1 record with ambiguous signal. No supporting evidence.

---

## Summary: The 12 Sub-Dimensions at a Glance

### Capability

#### AI Tool Adoption
- **L1:** Generic requests, single tool
- **L2:** Names specific tools/skills
- **L3:** Right tool for right task (specialized agents, MCP routing)
- **L4:** Autonomous tool orchestration

#### Prompt & Context Engineering
- **L1:** Starts from scratch every session
- **L2:** References CLAUDE.md, shared docs, URLs
- **L3:** Context auto-loaded by hooks/config
- **L4:** AI maintains and updates context docs

#### Agent Configuration
- **L1:** Bash + Read only, no agents/skills
- **L2:** Skills invoked, hooks configured
- **L3:** Specialized agents, chained workflows
- **L4:** Sub-agents spawn sub-agents, background execution

---

### Integration

#### CI/CD Integration
- **L1:** Developer pastes test output manually
- **L2:** AI runs test/build commands
- **L3:** Agent handles test→fix→retest cycle
- **L4:** Full commit→test→deploy→monitor cycle

#### Ticketing & Planning
- **L1:** No ticket references
- **L2:** Task ID in prompt (ENG-1234)
- **L3:** AI reads/structures requirements from tasks
- **L4:** AI manages task lifecycle end-to-end

#### Cross-System Connectivity
- **L1:** Local files only
- **L2:** 2+ systems accessed (Google Docs + SQL)
- **L3:** Read/write across systems, data flows between them
- **L4:** Autonomous multi-system orchestration

---

### Governance

#### Quality Controls
- **L1:** No quality checks
- **L2:** Lint/test commands run, criteria exist
- **L3:** Review gates in workflow (code-reviewer agent)
- **L4:** Continuous quality with auto-remediation

#### Security & Compliance
- **L1:** No policy awareness
- **L2:** References restrictions ("no PII")
- **L3:** Hooks/plugins enforce guardrails
- **L4:** Policy-as-code, real-time enforcement

#### Measurement & KPIs
- **L1:** Anecdotal or absent
- **L2:** Specific metrics named
- **L3:** Framework-level KPIs (DORA), automated
- **L4:** AI optimizes based on KPI feedback

---

### Execution Ownership

#### Ways of Working
- **L1:** Ad-hoc, learning as they go
- **L2:** Follows documented conventions
- **L3:** Review gates, escalation protocols
- **L4:** Autonomous execution with periodic oversight

#### Accountability & Ownership
- **L1:** No ownership structure
- **L2:** Named AI champion/owner
- **L3:** Team owns quality, metrics-linked
- **L4:** Team+agent SLAs

#### Scalability & Knowledge Transfer
- **L1:** Trial-and-error onboarding
- **L2:** Setup guides and examples exist
- **L3:** Reusable playbooks and skill libraries
- **L4:** AI-guided onboarding, self-service enablement

---
