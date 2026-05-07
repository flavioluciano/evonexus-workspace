---
name: dev-plan
description: Strategic planning with optional interview workflow. Use when the user wants to plan before implementing — "plan this", "let's plan", structured requirements gathering for vague ideas. Pairs with @compass-planner agent. Supports consensus mode and review mode.
---

# Dev Plan

Derived from oh-my-claudecode (MIT, Yeachan Heo). Adapted for the EvoNexus Engineering Layer.

Plan creates comprehensive, actionable work plans through intelligent interaction. It auto-detects whether to interview the user (broad requests) or plan directly (detailed requests).

## Use When
- User wants to plan before implementing — "plan this", "plan the", "let's plan"
- User wants structured requirements gathering for a vague idea
- User wants an existing plan reviewed — "review this plan"
- User wants multi-perspective consensus on a plan — see `dev-ralplan` (Tier 1, imported in EPIC 3)
- Task is broad or vague and needs scoping before any code is written

## Do Not Use When
- User wants autonomous end-to-end execution → use `dev-autopilot` instead
- User wants to start coding immediately with a clear task → delegate to `@bolt-executor`
- User asks a simple question that can be answered directly → just answer it
- Task is a single focused fix with obvious scope → skip planning, just do it

## Why This Exists
Jumping into code without understanding requirements leads to rework, scope creep, and missed edge cases. Plan provides structured requirements gathering, expert analysis, and quality-gated plans so that execution starts from a solid foundation.

## Execution Policy
- Auto-detect interview vs direct mode based on request specificity
- Ask one question at a time during interviews — never batch multiple questions
- Gather codebase facts via `@scout-explorer` agent before asking the user about them
- Plans must meet quality standards: 80%+ claims cite file/line, 90%+ criteria are testable
- Save plans to `workspace/projects/plans/{name}.md`

## Mode Selection

| Mode | Trigger | Behavior |
|------|---------|----------|
| Interview | Default for broad requests | Interactive requirements gathering |
| Direct | `--direct`, or detailed request | Skip interview, generate plan directly |
| Review | `--review` | Critic evaluation of an existing plan |

## Quality Gates
- All claims about the codebase must cite file:line
- All acceptance criteria must be testable
- Open questions must be explicitly listed
- Trade-offs must be documented for non-trivial decisions

## Handoff
After plan is approved by user:
- Pass plan path to `@bolt-executor` for implementation
- Or chain to `dev-autopilot` for full lifecycle execution

## Delegation
For deeper structured planning, hand off to `@compass-planner` agent — it runs a tighter interview workflow with mandatory user confirmation gates.
