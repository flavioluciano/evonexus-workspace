---
name: dev-team
description: On-demand spawning of multiple engineering agents in parallel for large-context work. Use when a task is too big for a single agent and the work can be split into independent streams.
---

# Dev Team

Derived from oh-my-claudecode (MIT, Yeachan Heo). Adapted for the EvoNexus Engineering Layer.

On-demand parallel agent spawning. When a task is too big for one agent and the work can be split into independent streams, spin up multiple engineering agents working in parallel.

## Use When
- Multi-file refactor across 10+ files in different modules
- Codebase audit that benefits from parallel exploration
- Performance investigation across multiple subsystems
- Documentation pass across many files

## Do Not Use When
- Sequential dependencies (B needs A's output)
- Single-file change
- Task fits within a single agent's context

## Workflow

1. **Decompose** the task into N independent streams
2. **Assign** each stream to the most appropriate agent (apex / bolt / lens / etc.)
3. **Spawn** agents in parallel via Task tool
4. **Collect** results as they return
5. **Synthesize** into a unified output
6. Save to `workspace/development/research/[C]team-{topic}-{date}.md`

## Streams Example

For "audit the entire auth module":
- **Stream 1:** `@scout-explorer` → map all auth files
- **Stream 2:** `@vault-security` → security audit
- **Stream 3:** `@lens-reviewer` → code quality review
- **Stream 4:** `@grid-tester` → test coverage analysis
- **Stream 5:** `@apex-architect` → architecture analysis

All spawn in parallel, results combine into one report.

## Output

```markdown
## Team Investigation — {topic}

### Streams
1. {stream 1 result summary}
2. {stream 2 result summary}
...

### Cross-stream Findings
[Insights that emerged from combining results]

### Recommendation
[Unified next step]
```

## Pairs With
- Any of the 19 engineering agents (you pick which to spawn)
- `dev-autopilot` (which can spawn its own team internally)
- `@compass-planner` (often the consumer of team output)
