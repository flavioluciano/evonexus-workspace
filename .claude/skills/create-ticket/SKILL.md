---
name: create-ticket
description: "Create a new ticket (persistent conversation/work thread) in EvoNexus. Assigns to an agent, sets priority, optionally links to a goal or project. Writes via POST /api/tickets. Use when the user says 'create a ticket', 'open an issue', 'add to Zara's queue', 'track this topic for later', 'assign X to Y agent', or wants to turn an ad-hoc conversation into persistent work."
---

# Create Ticket

Create a ticket — persistent conversation/work thread with state and assignee.

## When to use

Use tickets when:
- The topic will come up again (customer retention, recurring bug, ongoing partnership)
- The work needs an assignee and status workflow
- A heartbeat should pull it from an inbox (tickets are the inbox)
- Multiple people / agents will discuss over time (threaded comments)

Don't use tickets for:
- Ephemeral questions (use a chat session)
- Deterministic scheduled work (use a routine)
- State-checking protocols (use a heartbeat + decision prompt)

## Step 1: Collect fields

Ask the user:
1. **Title** — short, specific ("Cliente X reclama de latência")
2. **Description** — context (optional but recommended)
3. **Priority** — `urgent`, `high`, `medium` (default), `low`
4. **Assignee agent** — which agent handles this? Common picks:
   - `zara-cs` — support / CS
   - `flux-finance` — billing / payments
   - `atlas-project` — project blockers
   - `aria-hr` — HR / hiring
   - `lex-legal` — contracts / compliance
5. **Goal link?** Optional `goal_id` if this work moves a specific goal. Skip if not.
6. **Project link?** Optional `project_id` for grouping without a specific goal.

## Step 2: Call the API

Use `from dashboard.backend.sdk_client import evo` — auto-handles URL + auth.

The runtime injects the current agent slug and session id into your system prompt — pass them through so the ticket records provenance.

```python
import json
from dashboard.backend.sdk_client import evo
ticket = evo.post("/api/tickets", {
    "title": "Cliente X reclama de latência",
    "description": "Print anexado no Intercom, 4s para carregar /dashboard",
    "priority": "high",
    "assignee_agent": "zara-cs",
    "goal_id": 3,
    "source_agent": "<agent-slug>",         # injected via system prompt at runtime
    "source_session_id": "<session-uuid>",  # injected via system prompt at runtime
})
print(json.dumps(ticket))   # use json.dumps, NOT print(ticket) — the UI auto-binds the session to the ticket when it sees a valid JSON ticket in stdout
```

Response includes the created ticket with `id`, `status=open`, `created_at`.

## Step 3: Show what happens next

Explain to the user:

1. Ticket appears in `/issues?assignee=zara-cs` inbox
2. Zara's next heartbeat (step 3 — query inbox) will see it
3. If priority is `urgent`, it jumps to front of queue
4. When Zara acts, the ticket gets:
   - `locked_at` / `locked_by` = zara-cs (atomic checkout)
   - Comments added by Zara showing what was done
   - Status eventually changes (in_progress → review → resolved → closed)
5. Auto-release after `lock_timeout_seconds` (default 1800s) if Zara crashes mid-work

## Step 4: Mentions (optional)

If the user says "and tell Flux to check billing", add a comment with:

```python
from dashboard.backend.sdk_client import evo
evo.post(f"/api/tickets/{ticket['id']}/comments", {
    "body": "@flux-finance please confirm this customer's billing status",
})
```

The `@flux-finance` is parsed and fires a wake trigger — Flux's heartbeat wakes (within 30s debounce window) and picks up the ticket.

## Step 5: Direct user to UI

- `/issues` — global list with filters and search
- `/tickets/<id>` — detail view with full timeline (comments + activity + status changes)
- Bulk actions in `/issues`: close, reopen, delete, reassign, relink_goal

## Notes

- Tickets vs sessions: tickets persist (days/weeks), sessions are ephemeral. A session can bind to a ticket.
- Closing a ticket doesn't delete comments or activity — the timeline remains.
- Priority order: `urgent` > `high` > `medium` > `low` (enum with internal rank).

Related: `.claude/rules/tickets.md`, `.claude/rules/heartbeats.md`, `.claude/rules/goals.md`.
