# Maturity Assessment Ground Truth — Prompt Quality Signals

Prompt patterns that indicate maturity level (L1-L4) for each of the 12 sub-dimensions.

---

## 1. Capability Dimension

### 1.1 AI Tool Adoption

Measures: How intentionally are AI tools selected, licensed, and standardized? Do prompts show awareness of tool trade-offs?

**L1 — Assisted: Ad-hoc tool use; no awareness of trade-offs**

*Example L1 prompt:*
- "Help me debug this"
- Uses whatever tool is closest; no mention of other options
- No context about why this tool
- Pattern: Generic request, no tool awareness

**L2 — Integrated: Standardized tool choice; conscious selection**

*Example L2 prompt:*
- "Use Claude Code to set up the Git integration—we standardize on Claude for AI work"
- Shows awareness that tool choice is deliberate and team-wide
- Acknowledges licensing/standardization ("we standardize on")
- Pattern: Prompt mentions "our team uses X" or "we standardized on X"

**L3 — Agentic: Multi-tool selection based on task context**

*Example L3 prompt:*
- "For this refactoring, dispatch to Claude Code since it has better git integration; for the test suite, Copilot handles that better. Route based on capability."
- Explicitly chooses tool based on task fit
- Shows knowledge of tool strengths/weaknesses
- Pattern: Prompt routes different work to different tools ("for X use Y because")

**L4 — Autonomous: Agents autonomously select and orchestrate toolchains**

*Example L4 prompt:*
- "Orchestrate this task: Code analysis via Claude Code, security checks via Copilot, compliance via Gemini. Routing rules: use C for refactoring, Co for security, G for compliance. Maintain consistency across all outputs."
- Agents make selection based on defined routing rules
- No human per-task selection needed
- Pattern: Prompt defines autonomous routing policy; mentions agents making decisions

---

### 1.2 Prompt & Context Engineering

Measures: Do prompts load and reference shared context? How much context is built in each session vs. reused?

**L1 — Assisted: One-off prompts; no context reuse**

*Example L1 prompt:*
- "Build an API endpoint for user login"
- No reference to architecture, conventions, or prior work
- Rebuilds context from scratch each time
- Pattern: Generic request with no context references

**L2 — Integrated: Shared templates and conventions referenced**

*Example L2 prompt:*
- "Build an API endpoint for user login following our REST conventions from CLAUDE.md. Use the auth pattern from the session context I loaded."
- References shared documents (CLAUDE.md)
- Mentions loaded context
- Pattern: Prompt mentions "per our conventions" or "using the context I loaded"

**L3 — Agentic: Structured artifacts automatically feed prompts**

*Example L3 prompt:*
- "Based on the architecture doc you auto-loaded from /docs/architecture.md and the conventions cache from my last session, build the login endpoint."
- Assumes structured artifacts are auto-loaded
- References specific artifact sources
- Pattern: Prompt assumes artifacts are pre-loaded ("you auto-loaded", "based on the cached conventions")

**L4 — Autonomous: Agents maintain and evolve context documents**

*Example L4 prompt:*
- "This breaks our API conventions. Update /docs/api-patterns.md with the new pattern. Agent should auto-evolve context when patterns change."
- Agents update shared context automatically
- Prompts reference agent-maintained documents
- Pattern: Prompt assumes agents are maintaining/updating context ("agent should auto-evolve")

---

### 1.3 Agent Configuration

Measures: Are custom agents/skills being defined and used? How multi-step are they?

**L1 — Assisted: Only built-in tools; no custom agents**

*Example L1 prompt:*
- "Run the test suite using Bash, then read the output using Read, then fix the errors manually"
- Uses only standard tools (Bash, Read, etc.)
- Multi-step work is manual
- Pattern: No mention of custom commands or skills

**L2 — Integrated: Basic custom commands configured**

*Example L2 prompt:*
- "Use /review to check my PR for style issues before I merge"
- References a custom slash command
- Simple, single-purpose
- Pattern: Prompt mentions /command_name or "custom instruction"

**L3 — Agentic: Multi-step agents with workflows and error handling**

*Example L3 prompt:*
- "Dispatch /plan to map out this feature, then /review validates the plan, and /commit applies changes with validation. Chain them: plan→review→commit with error handling if review fails."
- References agents with defined workflows
- Mentions error handling and sequencing
- Pattern: Prompt describes agent chains ("then... with error handling")

**L4 — Autonomous: Agents compose/decompose and spawn sub-agents**

*Example L4 prompt:*
- "Break this into sub-tasks using /decompose, assign each to a sub-agent, collect results, validate with /verify, and reassemble. If any sub-agent fails, spawn recovery agent."
- Agents spawn and manage sub-agents
- Dynamic task decomposition
- Pattern: Prompt mentions agents spawning/managing other agents ("spawn sub-agent", "sub-agents report back")

---

## 2. Integration Dimension

### 2.1 CI/CD Integration

Measures: Are AI tools connected to build systems? Do prompts reference CI logs, test results, deployments?

**L1 — Assisted: No CI/CD connection; manual workflows**

*Example L1 prompt:*
- "Run tests locally, copy the output, and help me debug"
- No mention of CI system
- Manual copy-paste of results
- Pattern: No reference to CI/CD systems (GitHub Actions, Jenkins, etc.)

**L2 — Integrated: AI reviews PR outputs; basic automation**

*Example L2 prompt:*
- "Here's my PR. The CI build output shows 3 test failures. Review the build log and suggest fixes."
- Developer manually pulls CI output and shares it
- AI reviews the results
- Pattern: Prompt mentions "CI output", "build log", "test failure from CI"

**L3 — Agentic: Agents read CI results and auto-remediate**

*Example L3 prompt:*
- "When the CI pipeline fails, Agent should read the failure from GitHub Actions, analyze root cause, fix code, and rerun the pipeline."
- Agent automatically connects to CI
- No manual output copying
- Pattern: Prompt assumes agent reads CI directly ("Agent reads from GitHub Actions", "auto-remediate from CI failure")

**L4 — Autonomous: Full closed-loop CI/CD with agent ownership**

*Example L4 prompt:*
- "Full closed-loop: Agent commits code, triggers CI, monitors the pipeline, auto-deploys on success, rolls back on failure. Target SLA: 95% pass rate with auto-remediation."
- Agents own entire CI/CD cycle
- Autonomous deployment decisions
- Pattern: Prompt describes agents managing deployments, rollbacks, SLAs

---

### 2.2 Ticketing & Planning

Measures: Do prompts reference tickets/issues? Are requirements validated before coding starts?

**L1 — Assisted: Code-first; no ticket integration**

*Example L1 prompt:*
- "Build the login feature"
- No ticket reference
- No requirements validation
- Pattern: No mention of tickets, issues, or JIRA

**L2 — Integrated: Tickets referenced and AI assists with structure**

*Example L2 prompt:*
- "I'm working on ticket ACME-234. Here's the description. Help me break down the acceptance criteria and identify missing requirements before I start."
- References specific ticket
- AI validates requirements before coding
- Pattern: Prompt mentions "ticket #XXX" or "JIRA issue" with explicit requirement review

**L3 — Agentic: Agents parse raw issues into structured implementation plans**

*Example L3 prompt:*
- "Agent: Read ACME-234 from JIRA, parse acceptance criteria, identify edge cases, generate implementation plan, and validate completeness before returning."
- Agent reads from ticketing system directly
- Structured artifact output
- Pattern: Prompt assumes agent reads from JIRA/Linear directly ("Agent reads from JIRA")

**L4 — Autonomous: Agents triage, size, and assign work automatically**

*Example L4 prompt:*
- "Agent: Monitor the backlog in JIRA. Triage new issues, estimate story points based on patterns, assign to available agents based on skill match, validate completion against acceptance criteria."
- Agents manage entire workflow lifecycle
- Autonomous assignment and validation
- Pattern: Prompt describes agents triaging, sizing, assigning without human intervention

---

### 2.3 Cross-System Connectivity

Measures: Do prompts reference multiple systems (GitHub, JIRA, Slack, Confluence)? Is context pulled automatically or manually?

**L1 — Assisted: Isolated; manual context gathering**

*Example L1 prompt:*
- "I'm working on the authentication feature. Here's what I found: [manually pastes from Confluence, GitHub, Slack, JIRA]"
- All context manually gathered
- No system integration
- Pattern: Developer manually copies/pastes from multiple sources

**L2 — Integrated: AI reads from repos and docs; limited write**

*Example L2 prompt:*
- "Read the architecture from GitHub/docs/ARCHITECTURE.md and the ticket from JIRA ACME-234 and Slack thread #feature-auth. Synthesize into an implementation plan."
- References specific system sources
- AI reads from multiple sources
- Pattern: Prompt lists system names explicitly ("from GitHub, JIRA, and Slack")

**L3 — Agentic: Agents read/write across systems with context pulling**

*Example L3 prompt:*
- "Agent: Pull context from GitHub (repo structure, existing patterns), JIRA (ticket + acceptance criteria), Confluence (auth design doc), and Slack (#security-review). Cross-check all sources and flag contradictions."
- Agents autonomously connect to systems
- Cross-system reconciliation
- Pattern: Prompt describes agents pulling from systems ("Agent pulls from GitHub, JIRA, Confluence")

**L4 — Autonomous: Full bi-directional integration across all SDLC systems**

*Example L4 prompt:*
- "Agents maintain cross-system state: when JIRA status changes, update GitHub PR labels; when code ships, update Slack #deploys and mark JIRA complete; if Confluence doc updates, re-validate against code."
- Bi-directional system syncing
- Autonomous event-driven workflows
- Pattern: Prompt describes agents maintaining system state across tools ("when X happens in Y, update Z")

---

## 3. Governance Dimension

### 3.1 Quality Controls

Measures: Are AI outputs held to quality standards? Do prompts mention review gates, test coverage, eval criteria?

**L1 — Assisted: No quality gates; manual review only**

*Example L1 prompt:*
- "Review this code for style issues"
- No mention of quality standards
- Manual, subjective review
- Pattern: Generic review request with no criteria

**L2 — Integrated: Quality checklist exists; basic checks**

*Example L2 prompt:*
- "Review this PR against our checklist: [lists: linting, types, docstrings, test coverage > 80%]. Check each item."
- Explicit quality criteria
- Checklist-based
- Pattern: Prompt lists specific quality criteria or references a checklist

**L3 — Agentic: Automated eval harnesses validate before merge**

*Example L3 prompt:*
- "Before merge, run our eval harness: [code complexity < 10, type coverage 100%, test coverage 85%, no security warnings]. Reject if any criterion fails. Auto-request fixes."
- Hardened quality gates
- Automated eval harness
- Pattern: Prompt describes automated gates ("eval harness", "auto-reject if")

**L4 — Autonomous: Continuous quality scoring with auto-remediation**

*Example L4 prompt:*
- "Maintain quality score across every commit: track complexity, coverage, security, performance. On score drop, auto-spawn remediation agent. On persistent gaps, escalate to human with full diagnostic."
- Continuous monitoring
- Autonomous remediation
- Pattern: Prompt describes continuous scoring and autonomous fixing ("maintain score", "auto-spawn remediation agent")

---

### 3.2 Security & Compliance

Measures: Is AI usage governed? Do prompts mention data restrictions, audit trails, compliance policies?

**L1 — Assisted: No policy; shadow AI use**

*Example L1 prompt:*
- "Help me debug the payment processing code"
- No mention of data sensitivity
- No restrictions visible
- Pattern: No mention of compliance, data handling, or security policy

**L2 — Integrated: AI usage policy exists; basic rules acknowledged**

*Example L2 prompt:*
- "Review this code for security (per our AI usage policy: no PII, no API keys, no customer data). Flag any violations."
- References explicit policy
- Lists restricted data types
- Pattern: Prompt mentions "per our policy" or lists restricted data

**L3 — Agentic: Guardrails enforced in code; actions logged and auditable**

*Example L3 prompt:*
- "Agent should refuse any prompt containing PII (SSN, email, credit card). Log all refusals to audit trail. Implement hook that blocks input at prompt parse time."
- Guardrails built into agent code
- Logging and audit trail
- Pattern: Prompt describes guardrails ("Agent should refuse", "log to audit trail")

**L4 — Autonomous: Policy-as-code; agents self-enforce; real-time detection**

*Example L4 prompt:*
- "Embed compliance policy in agent code: detect PII regex, block regulatory-restricted data, scan for secrets (credentials, tokens). Real-time violation alerts. Self-remediate by redacting and logging."
- Policy embedded in agent logic
- Real-time enforcement
- Pattern: Prompt describes automated policy enforcement ("Policy-as-code", "self-enforce", "real-time detection")

---

### 3.3 Measurement & KPIs

Measures: Are AI outcomes measured? Do prompts reference metrics, dashboards, or KPI tracking?

**L1 — Assisted: No metrics; only anecdotal feedback**

*Example L1 prompt:*
- "Is Claude helping the team? I think so, but not sure"
- No concrete metrics
- Anecdotal assessment
- Pattern: No mention of metrics, dashboards, or KPIs

**L2 — Integrated: Basic metrics tracked; manual reporting**

*Example L2 prompt:*
- "Track adoption (% of team using AI), usage frequency (sessions/day), and report monthly to leadership"
- Defines specific metrics
- Manual reporting process
- Pattern: Prompt lists specific metrics ("adoption rate", "sessions per day", "manual report")

**L3 — Agentic: DORA-aligned KPIs automatically tracked**

*Example L3 prompt:*
- "Automatically track: deployment frequency, lead time, MTTR, change fail rate. Compare pre-AI vs post-AI baselines. Dashboard auto-updates daily."
- DORA framework
- Automated collection
- Pattern: Prompt mentions specific frameworks ("DORA-aligned") or assumes automated dashboards

**L4 — Autonomous: AI-driven dashboards; agents optimize based on KPI feedback**

*Example L4 prompt:*
- "Agent monitors KPI dashboard. If velocity drops, agent analyzes root cause (tool adoption? skill gaps? process friction?). Automatically recommends and tests optimizations. Updates strategy based on weekly KPI trends."
- Agents react to KPIs
- Autonomous optimization
- Pattern: Prompt describes agents optimizing based on KPI feedback ("agents optimize based on KPI feedback")

---

## 4. Execution Ownership Dimension

### 4.1 Ways of Working

Measures: Are AI workflows documented? Do prompts show standardized protocols vs. ad-hoc approaches?

**L1 — Assisted: Each engineer uses AI independently; no team conventions**

*Example L1 prompt:*
- "Claude, help me debug this" (said to whatever tool is available)
- No standardized session protocol
- No documentation
- Pattern: Ad-hoc, individual usage with no team conventions mentioned

**L2 — Integrated: Team conventions documented; shared playbooks exist**

*Example L2 prompt:*
- "Following our team's Ways of Working (documented in README): start session by loading CLAUDE.md, reference last 3 commits, then /plan if multi-step"
- References shared documentation
- Follows protocol
- Pattern: Prompt mentions "per our Ways of Working" or references documented protocol

**L3 — Agentic: Review gates and handoff protocols defined**

*Example L3 prompt:*
- "Agent workflow: code → /review gate → merge approval required → deploy. Handoff: when /review fails, alert on Slack #code-review and escalate to human."
- Defined handoff points
- Review gates mentioned
- Pattern: Prompt describes workflow gates and escalation ("when X, escalate to Y")

**L4 — Autonomous: Team and agents share accountability; structured oversight**

*Example L4 prompt:*
- "Agents and humans share accountability for delivery. Agent commits code, human spot-checks weekly. Both flagged in commit metadata. Escalation: if agent commits 5 consecutive PRs with human-requested changes, disable autonomous commits until human reviews process."
- Shared accountability
- Structured human oversight
- Pattern: Prompt describes shared ownership ("team and agents share accountability")

---

### 4.2 Accountability & Ownership

Measures: Is there a named AI owner? Do prompts show clear decision authority and responsibility?

**L1 — Assisted: No ownership; results are individual**

*Example L1 prompt:*
- "Everyone uses Claude as they see fit; no one is responsible for how well it works"
- No owner identified
- Responsibility undefined
- Pattern: No mention of ownership, champions, or decision authority

**L2 — Integrated: Tech lead or champion owns adoption**

*Example L2 prompt:*
- "Sarah is our AI Champion. She maintains CLAUDE.md, approves new skills, trains the team. Questions go to Sarah."
- Named owner identified
- Clear responsibilities
- Pattern: Prompt mentions "AI Champion: [name]" or "owned by [role]"

**L3 — Agentic: Team owns agentic output; KPIs tied to team performance**

*Example L3 prompt:*
- "The team collectively owns agent output quality. Agent commits are tracked in our sprint metrics. If agent defect rate rises above 5%, team's velocity score drops—team owns the fix."
- Collective ownership
- KPI linkage
- Pattern: Prompt ties ownership to team metrics ("team owns quality", "KPIs tied to team performance")

**L4 — Autonomous: End-to-end delivery owned by team+agents; measurable SLAs**

*Example L4 prompt:*
- "Team + Agents own feature delivery end-to-end: planning, coding, testing, deployment, monitoring. SLA: 99% uptime, <5min MTTR, all owned by team+agent partnership. Bonuses tied to SLA."
- Shared team+agent ownership
- Measurable SLAs
- Pattern: Prompt describes shared ownership with SLAs ("team+agents own", "SLA:", "measurable accountability")

---

### 4.3 Scalability & Knowledge Transfer

Measures: Can new developers ramp up on AI quickly? Do prompts reference playbooks, prompt libraries, or structured onboarding?

**L1 — Assisted: Knowledge tribal; nothing documented**

*Example L1 prompt:*
- New dev joins: "Just watch how I use Claude and pick it up"
- No onboarding
- No playbooks
- Pattern: No reference to training, documentation, or knowledge transfer

**L2 — Integrated: Onboarding materials exist; some documentation**

*Example L2 prompt:*
- "New dev checklist: (1) Read README on Claude setup, (2) Review 3 example prompts, (3) Pair with Sarah on first AI task, (4) Contribute one example prompt to library"
- Structured onboarding
- Example prompts exist
- Pattern: Prompt references onboarding checklist or "prompt library"

**L3 — Agentic: Reusable playbooks and patterns documented and shared**

*Example L3 prompt:*
- "New dev gets access to prompt library (/prompts), playbooks for common tasks (/review-playbook, /refactor-playbook), and module configs. Can self-serve in 1 week vs. 4 weeks manual ramp."
- Self-service access
- Playbooks documented
- Pattern: Prompt mentions "playbooks", "pattern library", self-service ramp

**L4 — Autonomous: Self-service enablement; new teams adopt independently**

*Example L4 prompt:*
- "New team: download CLAUDE.md template + agent configs. Agents guide initial setup. Within 1 day, team is productive. Agents teach patterns via feedback on prompts."
- Fully self-service
- Agents teach new teams
- Pattern: Prompt describes agents enabling new teams ("agents guide setup", "minimal support needed")

---

## How to Use This Ground Truth

### Assessing Developer Maturity from Prompts

For each developer/session, read through their prompts and look for patterns that match L1, L2, L3, or L4 indicators.

**Process:**
1. Pick a sub-dimension (e.g., "AI Tool Adoption")
2. Read their prompts from the session log
3. Match patterns against the L1, L2, L3, L4 examples
4. Assign the level that best matches their average behavior (not peak)
5. Repeat for all 12 sub-dimensions

### Key Signals to Look For

**Capability Dimension:**
- Tool Adoption: Mentions tool selection criteria? Aware of tradeoffs? ("we use X because Y")
- Context Engineering: References CLAUDE.md or shared templates? ("per our conventions")
- Agent Configuration: Mentions custom skills or commands? (/review, /plan, etc.)

**Integration Dimension:**
- CI/CD: References CI logs, pipeline, or build systems?
- Ticketing: Mentions specific tickets (ACME-234) or JIRA?
- Cross-System: Names multiple systems (GitHub, JIRA, Slack, Confluence)?

**Governance Dimension:**
- Quality: Mentions quality criteria, checklists, eval harnesses?
- Security: References data restrictions, PII, compliance policy?
- Measurement: Mentions metrics, dashboards, KPIs?

**Execution Ownership Dimension:**
- Ways of Working: References documented team protocols?
- Accountability: Names an owner, champion, or team responsibility?
- Knowledge Transfer: Mentions onboarding, playbooks, or knowledge sharing?

### What This Is NOT

- **Not a test.** Developers don't "pass" or "fail"—they're at different levels per dimension.
- **Not a tool count.** High tool usage doesn't mean high maturity. L4 might use fewer tools more strategically.
- **Not a skill invocation count.** An L1 developer calling /review once doesn't mean they're L2. L2 shows consistent, documented practice.
- **Not a PR review.** We're assessing strategic thinking from prompts, not code quality.

### Confidence Levels

- **High confidence:** Prompt explicitly mentions a practice ("we standardized on", "per our policy", "/review gate")
- **Medium confidence:** Prompt implies a practice without stating it ("the CI failed" suggests CI awareness)
- **Low confidence:** Single prompt may not represent typical behavior; look for patterns across multiple sessions

---

## Summary: The 12 Sub-Dimensions at a Glance

### Capability

#### AI Tool Adoption
- **L1:** Ad-hoc
- **L2:** "We standardize on"
- **L3:** Routes by task
- **L4:** Autonomous routing

#### Prompt & Context Engineering
- **L1:** One-off prompts
- **L2:** "Per our conventions"
- **L3:** "Auto-loaded artifacts"
- **L4:** "Agent maintains context"

#### Agent Configuration
- **L1:** No custom tools
- **L2:** Mentions /command
- **L3:** Agent chains
- **L4:** Sub-agent orchestration

---

### Integration

#### CI/CD Integration
- **L1:** Manual copy-paste
- **L2:** "CI build log shows"
- **L3:** "Agent reads CI"
- **L4:** Full closed-loop + SLA

#### Ticketing & Planning
- **L1:** No ticket mention
- **L2:** "Ticket ACME-234"
- **L3:** "Agent reads JIRA"
- **L4:** Autonomous triaging

#### Cross-System Connectivity
- **L1:** Manual gathering
- **L2:** Lists systems explicitly
- **L3:** "Agent pulls from all"
- **L4:** Bi-directional sync

---

### Governance

#### Quality Controls
- **L1:** Subjective review
- **L2:** Quality checklist
- **L3:** Eval harness
- **L4:** Continuous scoring

#### Security & Compliance
- **L1:** No policy mention
- **L2:** "Per our policy"
- **L3:** Guardrails in code
- **L4:** Policy-as-code

#### Measurement & KPIs
- **L1:** Anecdotal
- **L2:** Lists metrics
- **L3:** DORA framework
- **L4:** Agents optimize KPIs

---

### Execution Ownership

#### Ways of Working
- **L1:** Ad-hoc usage
- **L2:** "Per our Ways of Working"
- **L3:** Review gates + escalation
- **L4:** Shared accountability

#### Accountability & Ownership
- **L1:** No owner
- **L2:** "AI Champion: [name]"
- **L3:** "Team owns quality"
- **L4:** "Team+Agent SLA"

#### Scalability & Knowledge Transfer
- **L1:** Tribal knowledge
- **L2:** Onboarding checklist
- **L3:** Playbooks + library
- **L4:** Agents teach new teams

---
