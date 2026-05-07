# Agents (17 business + 21 engineering core + custom)

Defined in `.claude/agents/`. Each agent has an isolated domain and can be invoked via command. EvoNexus organizes agents in **two ortogonal layers**:

- **Business Layer** — 17 agents for operations, finance, community, marketing, HR, legal, product, data, sales, learning retention.
- **Engineering Layer** — 21 agents for software development, most derived from [oh-my-claudecode](https://github.com/yeachan-heo/oh-my-claudecode) (MIT). See [NOTICE.md](../../NOTICE.md). The canonical 6-phase workflow is documented in `.claude/rules/dev-phases.md`.

Custom agents use `custom-` prefix and are gitignored.

---

## Business Layer (17)

| Agent | Command | Domain |
|--------|---------|---------|
| **Clawdia** | `/clawdia` | Operational hub — calendar, emails, tasks, decisions |
| **Flux** | `/flux` | Finance — cash flow, metrics, Stripe, Omie |
| **Atlas** | `/atlas` | Projects — status, milestones, blockers, Linear, GitHub, Licensing |
| **Kai** | `/kai` | Personal — health, habits, routine (isolated domain) |
| **Pulse** | `/pulse` | Community — Discord, WhatsApp, sentiment, FAQ |
| **Sage** | `/sage` | Strategy — OKRs, roadmap, prioritization, scenarios |
| **Pixel** | `/pixel` | Social media — content, calendar, analysis, reports |
| **Nex** | `/nex` | Sales — pipeline, proposals, qualification |
| **Mentor** | `/mentor` | Courses — learning paths, modules, Evo Academy |
| **Lumen** | `/lumen-learning` | Learning retention — spaced repetition (SM-2), fact capture, quizzes, retention stats |
| **Oracle** | `/oracle` | **Entry point** — onboarding, business discovery, implementation plan, workspace knowledge |
| **Mako** | `/mako` | Marketing — campaigns, content strategy, SEO, email, brand |
| **Aria** | `/aria` | HR / People — recruiting, onboarding, performance, compensation |
| **Zara** | `/zara` | Customer Success — triage, escalation, health scores, KB |
| **Lex** | `/lex` | Legal / Compliance — contracts, NDA, LGPD, risk assessment |
| **Nova** | `/nova` | Product — specs, roadmaps, metrics, research, prioritization |
| **Dex** | `/dex` | Data / BI — analysis, SQL, dashboards, visualizations |

---

## Engineering Layer (21) — 19 derived from oh-my-claudecode + 2 native

*Imported in phases — see `workspace/projects/specs/[C]omc-integration-quick-spec.md` roadmap. The 6-phase workflow is canonical — see `.claude/rules/dev-phases.md`.*

### Reasoning (opus)
| Agent | Command | Role |
|---|---|---|
| **Apex** | `/apex` | Architect — architectural design, read-only debugging, tradeoffs |
| **Echo** | `/echo` | Analyst — discovery, requirements gaps, hidden assumptions |
| **Compass** | `/compass` | Planner — tactical 3-6 step planning with interview |
| **Raven** | `/raven` | Critic — challenges plans before execution, multi-perspective |
| **Lens** | `/lens` | Code Reviewer — 2-stage review (spec + quality), OWASP, SOLID |
| **Zen** | `/zen` | Code Simplifier — deslop, refactoring, clarity |
| **Vault** | `/vault` | Security Reviewer — OWASP Top 10, secrets, dependency audit |

### Execution (sonnet)
| Agent | Command | Role |
|---|---|---|
| **Bolt** | `/bolt` | Executor — precise multi-file implementation |
| **Hawk** | `/hawk` | Debugger — root cause, regressions, stack traces |
| **Grid** | `/grid` | Test Engineer — TDD, strategy pyramid, coverage |
| **Probe** | `/probe` | QA Tester — interactive testing, flaky diagnosis |
| **Oath** | `/oath` | Verifier — evidence-based completion verification |
| **Trail** | `/trail` | Tracer — causal tracing, competing hypotheses |
| **Flow** | `/flow` | Git Master — atomic commits, rebase, history cleanup |
| **Scroll** | `/scroll` | Document Specialist — external docs (SDKs, APIs) via web |
| **Canvas** | `/canvas` | Designer — UI/UX for product (Evo AI CRM, dashboards) |
| **Prism** | `/prism` | Scientist — formal statistical analysis, hypothesis testing |
| **Helm** ⭐ | `/helm` | Conductor — cycle orchestration, sequencing, routing to phase owners (native) |
| **Mirror** ⭐ | `/mirror` | Retrospective — lessons learned, blameless post-mortem, memory updates (native) |

### Speed (haiku)
| Agent | Command | Role |
|---|---|---|
| **Scout** | `/scout` | Explorer — parallel codebase search (Glob/Grep/AST) |
| **Quill** | `/quill` | Writer — quick technical docs, README, comments |

---

## Custom Agents

Users can create custom agents with `custom-` prefix:
- Files: `.claude/agents/custom-{name}.md` + `.claude/commands/custom-{name}.md`
- Memory: `.claude/agent-memory/custom-{name}/`
- All gitignored (personal to workspace)
- Use the `create-agent` skill to create one

---

## How to Use

- Use the correct agent for each domain. Do not mix responsibilities across layers when avoidable.
- **Business tasks** (emails, finance, community, etc.) → Business Layer
- **Engineering tasks** (code, tests, reviews, debug) → Engineering Layer
- Each agent has a dedicated `agent-memory/` for persistence between sessions.
- Business agents default to `sonnet`; engineering agents inherit model tier from OMC (opus / sonnet / haiku) calibrated per role.
- To invoke, use the corresponding slash command (e.g., `/clawdia`, `/apex`, `/bolt`).
- Cross-layer handoffs are allowed: e.g., `/nova` can delegate an implementation spec to `/apex` + `/bolt` + `/oath`.

---

## Shared Capabilities (all agents)

All 38 agents can leverage these workspace features regardless of layer:

### Heartbeats — proactive scheduling

Any agent can be configured as a heartbeat (`config/heartbeats.yaml`) that wakes periodically and decides whether to act. Best for state-checking work (Atlas→Linear, Zara→support queue, Flux→payments). Fully detailed in `.claude/rules/heartbeats.md`.

### Goals — outcome-linked context

Work that traces back to a measurable Mission→Project→Goal→Task gets automatic context injection. Set `goal_id` on any routine, heartbeat, or ticket. Agent receives the full cascade in its prompt. See `.claude/rules/goals.md`.

### Tickets — persistent work inbox

Assignable tickets with atomic checkout. When `assignee_agent=<slug>` is set, the ticket shows up in that agent's inbox. Heartbeats pull from this inbox automatically. Mentions (`@agent-slug`) in comments wake the mentioned agent. See `.claude/rules/tickets.md`.

**Which agents benefit most:**
- **Heartbeats**: atlas, flux, zara, pulse, pixel, mako, nex, aria, lex — anyone who monitors a state
- **Goals**: all business agents (every business action maps to an outcome)
- **Tickets**: zara, nex, aria, lex — anyone with a queue of incoming work

**Engineering agents** (apex, bolt, lens, etc.) generally don't need heartbeats directly (they're session-bound), but DO benefit from tickets (bug tracking, PRD backlog) and goals (tracking feature delivery against Mission targets).

See the skill registry for `/create-heartbeat`, `/create-goal`, `/create-ticket`, `/manage-heartbeats`.

---

## Calling Dashboard APIs

When an agent needs to call the dashboard API (creating tickets, goals, querying heartbeats, etc.), use the `EvoClient` SDK — it auto-resolves the base URL and injects the Bearer token:

```python
from dashboard.backend.sdk_client import evo

# Examples:
ticket = evo.post("/api/tickets", {"title": "...", "assignee_agent": "zara-cs"})
hbs    = evo.get("/api/heartbeats")
evo.patch(f"/api/heartbeats/{hb_id}", {"enabled": True})
evo.delete(f"/api/shares/{token}")
```

URL resolution order: `EVONEXUS_API_URL` → `FLASK_PORT` → `localhost:8080`. Token comes from `DASHBOARD_API_TOKEN` in `.env`.
