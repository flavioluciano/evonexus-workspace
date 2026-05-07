# Heartbeats — Proactive Agents (9-Step Protocol)

Agents that wake up on a schedule, check workspace state, and decide whether to act.

## What vs Routines

| | Routine | Heartbeat |
|---|---|---|
| Execution | Always runs on schedule | Runs 9-step protocol; decides if work needed |
| Config | `config/routines.yaml` | `config/heartbeats.yaml` |
| Cost if idle | Still spends tokens | Can decide to skip → low cost |
| Use when | Recurring output always wanted (reports) | State check + conditional action |

## The 9-Step Protocol

1. **Load identity** — read `.claude/agents/{agent}.md`
2. **Check approvals** — pending approvals table
3. **Check inbox** — tickets assigned to the agent (F1.3)
4. **Pick priority** — apply decision prompt
5. **Atomic checkout** — `UPDATE WHERE locked_at IS NULL` on the picked ticket
6. **Assemble context** — identity + goal chain (F1.2) + inbox + decision prompt
7. **Work** — invoke Claude via subprocess with `max_turns` + `timeout_seconds`
8. **Persist** — write `heartbeat_runs` row + JSONL log
9. **Release checkout** — clear `locked_at`

## Wake Triggers

- `interval` — every N seconds (required)
- `manual` — `POST /api/heartbeats/{id}/run` from UI
- `new_task` — when a ticket assigned to agent becomes open
- `mention` — `@agent-slug` in a ticket comment
- `approval_decision` — when an approval assigned to agent resolves

Multiple triggers per heartbeat. Debounced 30s to prevent thrashing.

## Config: `config/heartbeats.yaml`

Gitignored. Source of truth for CRUD; DB mirrors for run history.

```yaml
heartbeats:
  - id: atlas-4h
    agent: atlas-project
    interval_seconds: 14400       # 4h
    max_turns: 10
    timeout_seconds: 600
    lock_timeout_seconds: 1800
    wake_triggers: [interval, manual, mention]
    enabled: false                # opt-in per heartbeat
    goal_id: null
    required_secrets: [LINEAR_API_KEY]
    decision_prompt: |
      Check Linear for blockers in active projects. If any are blocked > 24h or
      assigned to unresponsive person, act. Otherwise skip.
```

Bootstrap: if `config/heartbeats.yaml` is missing, loader copies from `config/heartbeats.example.yaml`.

## How to Create

### Via UI
`/scheduler` → Heartbeats tab → **New Heartbeat** wizard.

### Via skill
`/create-heartbeat` — interactive prompts, writes YAML atomically with schema validation.

### Via YAML (manual)
Edit `config/heartbeats.yaml`, run `make heartbeat-lint` to validate, then restart.

## How to Enable

1. Set `enabled: true` on the entry in YAML
2. Restart dashboard (`make dashboard-app` or `sudo systemctl restart evo-nexus`)

## Debugging

| What | Where |
|---|---|
| Run logs | `workspace/ADWs/logs/heartbeats/{id}-{YYYY-MM-DD}.jsonl` |
| DB runs | `heartbeat_runs` table (last status, duration, cost) |
| UI | `/scheduler` → Heartbeats tab → click row for detail |
| Manual trigger | Click "Run Now" on detail page |

## Example Seeds

Ship with `enabled: false` for safety. Turn on manually after testing:
- `atlas-4h` — Atlas checks Linear every 4h
- `zara-2h` — Zara scans tickets every 2h
- `flux-6h` — Flux checks Stripe/Omie every 6h

## Integration Points

- **Tickets (F1.3)** — step 3 queries `tickets` WHERE `assignee_agent = X`
- **Goals (F1.2)** — step 6 injects Mission→Project→Goal chain if `goal_id` set
- **Audit** — step 8 saves `prompt_preview` (first 1000 chars) and cost/tokens

## Related Rules

- `tickets.md` — inbox source for step 3
- `goals.md` — context injected in step 6
- `agents.md` — which agents support heartbeats
