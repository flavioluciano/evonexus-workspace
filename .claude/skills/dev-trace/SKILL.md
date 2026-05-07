---
name: dev-trace
description: Evidence-driven causal tracing with competing hypotheses. Use when an observation has multiple plausible explanations and you need to systematically rank them with evidence FOR and AGAINST each. Pairs with @trail-tracer.
---

# Dev Trace

Derived from oh-my-claudecode (MIT, Yeachan Heo). Adapted for the EvoNexus Engineering Layer.

Causal investigation with multi-hypothesis discipline. Generate at least 2 explanations, collect evidence FOR and AGAINST, rank by strength, end with a discriminating probe.

## Use When
- Observation has multiple plausible causes
- "Why did this happen?" — and you don't want to jump to the first answer
- Multi-causal problem (intermittent bugs, regional anomalies, performance puzzles)
- Need to preserve uncertainty rather than collapse to one answer prematurely

## Do Not Use When
- Cause is obvious → just fix it via `@hawk-debugger`
- Single-cause bug with clear stack trace → `@hawk-debugger`
- Just needs codebase search → `@scout-explorer`

## Workflow
Delegate to `@trail-tracer`:

1. **OBSERVE** — restate the observation precisely, no interpretation
2. **FRAME** — define the exact "why" question
3. **HYPOTHESIZE** — generate 2+ competing explanations
4. **GATHER EVIDENCE** — for each, collect evidence FOR and AGAINST in parallel
5. **APPLY LENSES** — systems / premortem / science
6. **REBUT** — strongest alternative challenges the leader
7. **RANK** — down-rank contradicted, weak-assumption, failed-prediction explanations
8. **SYNTHESIZE** — best explanation, explicitly provisional if needed
9. **PROBE** — name the critical unknown and the discriminating next experiment

## Output
Saved to `workspace/development/debug/[C]trace-{topic}-{date}.md` using the `dev-trace-report.md` template.

## Pairs With
- `@trail-tracer` (the executor)
- `@hawk-debugger` (when trace converges to a clear bug)
- `@apex-architect` (when trace reveals architectural issues)
