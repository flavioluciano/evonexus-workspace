# Goals — 4-Level Cascade (Mission → Project → Goal → Task)

Every piece of work traces back to a measurable outcome. Agents receive goal context automatically when `goal_id` is set.

## Hierarchy

```
Mission: Evolution MRR $1M Q4 2026
├── Project: Evo AI
│   ├── Goal: 100 paying customers by Jun 30 (count)
│   ├── Goal: Ship billing v2 (boolean)
│   └── Tasks...
├── Project: Evolution Summit
│   ├── Goal: Sell 200 tickets
│   └── Goal: Close 3 sponsors
└── Project: Evo Academy
    └── Goal: 50 beta students
```

## Data Model

SQLite tables (in `dashboard.db`):

| Table | Purpose |
|---|---|
| `missions` | Top-level purpose (v1 = single mission) |
| `projects` | Work group under a mission; links to `workspace/project/` folders |
| `goals` | Measurable target within a project |
| `goal_tasks` | Unit of work; `status='done'` triggers `current_value += 1` |

Indexes on FKs + `status`. Foreign keys: `projects.mission_id ON DELETE CASCADE`, `goals.project_id ON DELETE CASCADE`, `goal_tasks.goal_id ON DELETE SET NULL`.

## Metric Types

Goals declare `metric_type`:
- `count` — integer counter (e.g., "100 customers")
- `currency` — USD / BRL value
- `percentage` — 0.0 to 100.0
- `boolean` — target_value=1, current_value=0|1

UI formats display accordingly.

## Auto-Progress

SQLite trigger `trg_task_done_updates_goal` on `UPDATE OF status ON goal_tasks`:
- When `NEW.status = 'done' AND OLD.status != 'done'` and `goal_id IS NOT NULL`:
  - `goals.current_value += 1`
  - If `current_value >= target_value AND status = 'active'`: set `status = 'achieved'`
- Idempotent — achieved goals don't regress

Drift correction: `POST /api/goals/{id}/recalculate` recomputes from `goal_progress_v` view.

## Linking Work to Goals

### In routines (`config/routines.yaml`)
```yaml
- name: financial-weekly
  schedule: "0 9 * * 5"
  script: financial_weekly.py
  goal_id: evo-revenue-1m-q4-2026   # optional
```

### In heartbeats (`config/heartbeats.yaml`)
```yaml
- id: atlas-4h
  agent: atlas-project
  goal_id: evo-ai-100-customers     # optional
  ...
```

### In tickets
```bash
POST /api/tickets
{
  "title": "...",
  "goal_id": "evo-ai-100-customers"
}
```

## Context Injection

When a routine / heartbeat / agent action has `goal_id` set, the prompt gains:

```
## Goal Context
Mission: Evolution MRR $1M Q4 2026
Project: Evo AI
Goal: 100 paying customers by Jun 30 (progress: 23/100 tasks done, 45 days left)

---

{original prompt}
```

Implemented in `dashboard/backend/goal_context.py` (`inject_into_prompt`). Falls back to original prompt if goal not found — zero regression.

## UI

`/goals` — tree view:
- Mission card at top with overall %
- Project cards with % progress
- Goals list with progress bars
- Tasks collapsible per goal
- Filters: status (active / achieved / on-hold / cancelled), due_date (overdue / this-week / this-month)

## How to Create

### Via UI
`/goals` → **New Mission** / **New Project** / **New Goal** buttons.

### Via skill
`/create-goal` — interactive: choose mission → project → define goal (title, metric_type, target_value, due_date).

### Via API
```
POST /api/missions
POST /api/projects       (body: mission_id)
POST /api/goals          (body: project_id, target_metric, metric_type, target_value, due_date)
POST /api/goal-tasks     (body: goal_id, title, priority, assignee_agent)
```

## Integration Points

- **Heartbeats (F1.1)** — step 6 calls `goal_context.inject_into_prompt()` if `goal_id` set
- **Routines** — optional `goal_id` / `project_id` in YAML; runner injects context
- **Tickets (F1.3)** — optional `goal_id`; resolving a ticket can close a related task

## Related Rules

- `heartbeats.md` — consumes goal context in step 6
- `tickets.md` — can link to goals
- `routines.md` — optional goal linking
