---
name: create-routine
description: "Create a new automated routine (ADW) for the scheduler. Guides the user through defining what the routine does, the type (AI or systematic), the schedule, and generates the Python script + Makefile target. Use when the user says 'create a routine', 'add a routine', 'automate this', 'schedule this task', 'new ADW', 'I want this to run automatically', or wants to turn any manual task into a scheduled automation."
---

# Create Custom Routine

Guide the user through creating a new automated routine that runs on schedule via the EvoNexus scheduler.

## What You're Building

A routine is a Python script in `ADWs/routines/custom/` that runs on a schedule (daily, weekly, monthly, or interval). There are two types:

- **AI routines** — invoke Claude Code CLI with an agent to perform reasoning tasks (reports, analysis, decisions). Cost tokens and ~30-120s per run.
- **Systematic routines** — pure Python scripts that perform deterministic operations (API calls, file ops, data transforms). No AI, no tokens, no cost, ~1-5s per run.

## Step 1: Understand the Task

Ask the user:
1. **What should this routine do?** (e.g., "check my GitHub repos every morning", "ping API endpoints every 5 minutes")
2. **AI or systematic?** Help the user decide:
   - **Use AI when:** the task needs reasoning, analysis, writing, or decisions (generate a report, analyze sentiment, summarize data, make recommendations)
   - **Use systematic when:** the task is deterministic and repeatable (HTTP health checks, file cleanup, data snapshots, metric logging, backups, CSV exports)
3. **When should it run?** (daily at X, every N minutes, weekly on day, monthly on day 1)
4. **What output?** (HTML report, markdown file, CSV, JSON, Telegram notification, log entry, or just action)

If AI routine, also ask:
- **Which agent should run it?**
  - `clawdia-assistant` — ops, daily tasks, email, meetings
  - `flux-finance` — financial reports, Stripe, ERP
  - `atlas-project` — GitHub, Linear, project tracking
  - `pulse-community` — Discord, WhatsApp, community
  - `pixel-social-media` — social media, content, analytics
  - `sage-strategy` — OKRs, strategy, competitive analysis
  - `nex-sales` — pipeline, proposals, leads
  - `mentor-courses` — courses, learning paths
  - `kai-personal-assistant` — health, habits, personal

## Step 2: Generate the Script

### AI routine

Create the routine script at `ADWs/routines/custom/{name}.py`:

```python
#!/usr/bin/env python3
"""ADW: {Routine Name} — {brief description}. Agent: @{agent-name}"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_skill, run_claude, banner, summary

def main():
    banner("{Routine Name}", "{description} | @{agent}")
    results = []
    results.append(run_skill(
        "{skill-name}",
        log_name="{routine-id}",
        timeout=600,
        agent="{agent-name}"
    ))
    summary(results, "{Routine Name}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
```

Key rules for AI routines:
- Use `run_skill()` when there's an existing skill, or `run_claude()` for inline prompts
- Specify the agent name for context loading
- Set a reasonable timeout (300-900s depending on complexity)

### Systematic routine

Create the routine script at `ADWs/routines/custom/{name}.py`:

```python
#!/usr/bin/env python3
"""ADW: {Routine Name} — {brief description}. Type: systematic"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from runner import run_script, banner, summary

def do_task():
    """Pure Python logic — no Claude CLI, no AI, no tokens."""
    # YOUR CODE HERE: API calls, file ops, data transforms
    # ...
    return {
        "ok": True,  # or False on failure
        "summary": "Short description of what happened",
        "data": {}   # optional structured data for logs
    }

def main():
    banner("{Routine Name}", "{description} | systematic")
    results = []
    results.append(run_script(do_task, log_name="{routine-id}", timeout=60))
    summary(results, "{Routine Name}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
```

Key rules for systematic routines:
- Write the actual Python logic in the `do_task()` function — this is where YOU (Claude) generate the implementation code
- Use stdlib + `requests` for HTTP calls (already in pyproject.toml dependencies)
- Return `{"ok": bool, "summary": str}` so the runner can log success/failure
- Keep timeout short (30-120s) — these should be fast
- No `agent` parameter — systematic routines don't use agents
- Common patterns: `requests.get()` for API polling, `os.walk()` for file ops, `csv.writer()` for data export, `shutil` for backups

## Step 3: Run It

No Makefile changes needed — routines are discovered dynamically from scripts.

```bash
make run R={routine-id}      # Run by ID
make list-routines           # List all available
```

## Step 4: Add to Scheduler (Optional)

If the user wants it automated, add to `scheduler.py` in the appropriate section:

```python
# Daily
schedule.every().day.at("{HH:MM}").do(run_adw, "{Routine Name}", "custom/{script_name}.py")

# Weekly
schedule.every().{day}.at("{HH:MM}").do(run_adw, "{Routine Name}", "custom/{script_name}.py")

# Monthly (in the monthly block)
run_adw("{Routine Name}", "custom/{script_name}.py")

# Interval
schedule.every({N}).minutes.do(run_adw, "{Routine Name}", "custom/{script_name}.py")
```

## Step 5: Test

Run the routine manually:
```bash
make run R={routine-id}
```

Check the output and adjust the prompt if needed.

## Step 6: Create HTML Template (Optional)

If the routine generates an HTML report, create a template at `.claude/templates/html/{name}.html` following the pattern of existing templates:
- Dark theme (bg #0C111D, green #00FFA7)
- Evolution Foundation logo in header
- Footer: "Automatically generated by EvoNexus — Evolution Foundation"
- Use `{{PLACEHOLDER}}` for dynamic content

## Examples

### AI routine: Daily competitor check
```
Name: competitor-check
Type: AI
Agent: sage-strategy
Schedule: daily at 09:00
Why AI: needs reasoning to analyze competitor changes and compare positioning
```

### AI routine: Weekly content performance
```
Name: content-performance
Type: AI
Agent: pixel-social-media
Schedule: weekly on friday at 17:00
Why AI: needs analysis to identify trends and make recommendations
```

### Systematic routine: API health check
```
Name: api-health-check
Type: systematic
Schedule: every 5 minutes
Why systematic: just pings endpoints and checks HTTP status codes — no reasoning needed
```

### Systematic routine: Metric snapshot
```
Name: metric-snapshot
Type: systematic
Schedule: daily at 23:55
Why systematic: reads metrics.json and appends a row to a CSV — pure data transform
```

### Systematic routine: Log cleanup
```
Name: log-cleanup
Type: systematic
Schedule: weekly on sunday at 03:00
Why systematic: deletes files older than 30 days — deterministic file operation
```

## Important Notes

- Custom routines go in `ADWs/routines/custom/` (gitignored — they're personal to your workspace)
- Core routines in `ADWs/routines/` are shipped with the repo and should not be modified
- The `runner.py` handles logging, metrics, and Telegram notifications automatically for both types
- Systematic routines log with `tokens=0` and `cost=0` in metrics
- Systematic routines can run at high frequency (every 1-5 minutes) since they cost nothing
- Restart the scheduler after adding new routines: stop and `make scheduler`
