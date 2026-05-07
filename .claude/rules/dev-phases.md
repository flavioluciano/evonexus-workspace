# Engineering Layer — Development Phases

Canonical workflow for the 21 engineering agents. This is a **guide**, not a rigid gate. Simple changes can skip phases; complex features should follow them in order. Each phase has an **owner**, **inputs**, **outputs**, and an **exit criterion**.

## The 6 phases

```
Discovery → Planning → Solutioning → Build → Verify → Retro
```

### Phase 1 — Discovery
**Owner:** `@echo-analyst`
**Also involved:** `@scout-explorer` (parallel codebase facts), `@trail-tracer` (causal investigation when symptom → cause is unclear)
**Inputs:** vague user request, problem statement, or bug report
**Outputs:** `[C]discovery-{feature}.md` in the feature folder — surfaces gaps, unstated assumptions, hidden constraints, open questions
**Exit criterion:** list of open questions answered or explicitly deferred; problem space is crisp enough that a PRD can be written.

**Skip when:** the request is already crisp and scoped (e.g., "add timeout param with default 5000ms").

### Phase 2 — Planning
**Owner:** `@compass-planner`
**Also involved:** `@nova-product` (business-layer PM) when the feature has external stakeholders or user-facing trade-offs
**Inputs:** discovery output (or direct request for small tasks)
**Outputs:**
1. `[C]prd-{feature}.md` — Product Requirements Document (what and why; acceptance criteria in Given/When/Then)
2. `[C]plan-{feature}.md` — 3-6 step executable plan (how; derived from the PRD)

**Exit criterion:** user explicit approval on the plan. No implementation begins without it.

**Skip when:** trivial changes where a PRD adds no value — go direct to a minimal plan.

### Phase 3 — Solutioning
**Owner:** `@apex-architect`
**Also involved:** `@raven-critic` (adversarial review for high-stakes decisions), `@scroll-docs` (external SDK/API lookups), `@vault-security` (security implications of the design)
**Inputs:** PRD + plan
**Outputs:** `[C]architecture-{feature}.md` in ADR format — Decision, Drivers, Alternatives, Consequences, Follow-ups
**Exit criterion:** architectural decisions documented and (for high-stakes) critiqued by Raven.

**Skip when:** change fits cleanly into existing patterns with no new decisions to make.

### Phase 4 — Build
**Owner:** `@bolt-executor`
**Also involved:** `@grid-tester` (TDD when tests come first), `@canvas-designer` (UI/UX work), `@hawk-debugger` (when bugs surface), `@flow-git` (atomic commits)
**Inputs:** plan + architecture (if any)
**Outputs:** working code + tests + commits
**Exit criterion:** all plan steps implemented, tests green, self-verification passed.

**Circuit breaker:** 3 failed attempts on the same issue → Bolt escalates to `@apex-architect` (do not try variation #4).

### Phase 5 — Verify
**Owner:** `@oath-verifier`
**Also involved:** `@lens-reviewer` (2-stage code review: spec compliance + quality), `@probe-qa` (interactive end-to-end testing), `@vault-security` (security audit on security-sensitive changes)
**Inputs:** build output + original PRD/plan (for spec compliance check)
**Outputs:** `[C]verification-{feature}.md` — evidence-based PASS/FAIL/INCOMPLETE with fresh test runs, build status, and acceptance criteria coverage
**Exit criterion:** all acceptance criteria from the PRD are mapped to evidence. No "should work" — actual output.

**Never skipped** for non-trivial changes.

### Phase 6 — Retro
**Owner:** `@mirror-retro`
**Inputs:** all artifacts from phases 1-5 in the feature folder
**Outputs:** `[C]retro-{feature}.md` — what worked, what didn't, patterns to reuse, patterns to avoid, memory updates to propose
**Exit criterion:** retro saved; proposed memory updates reviewed by user; closed feedback loop.

**Skip when:** change was tiny and there are no lessons to extract.

---

## Cycle orchestration

The **`@helm-conductor`** agent sits above these phases. Its job is not to do the work of any phase, but to answer:

- "What's the next thing to work on?"
- "Which feature is blocked and why?"
- "Who should I call for this task?"
- "Are we respecting dependencies between features?"

Call `@helm-conductor` when you have multiple active features or are unsure which phase a task is in.

---

## Feature folders — the unit of work

Every non-trivial piece of work lives in its own feature folder:

```
workspace/development/features/{feature-slug}/
├── [C]discovery-{feature}.md       ← Phase 1 (Echo)
├── [C]prd-{feature}.md             ← Phase 2 (Compass)
├── [C]plan-{feature}.md            ← Phase 2 (Compass)
├── [C]architecture-{feature}.md    ← Phase 3 (Apex, ADR format)
├── [C]code-review-{feature}.md     ← Phase 5 (Lens)
├── [C]verification-{feature}.md    ← Phase 5 (Oath)
└── [C]retro-{feature}.md           ← Phase 6 (Mirror)
```

**Slug convention:** `{kebab-case-name}` — e.g., `dark-mode`, `pg15-migration`, `auth-refactor`.

**Why feature folders in addition to `workspace/development/{type}/`:**
- Feature folders give **coherent context** — one place to find everything about a feature
- Type folders (`plans/`, `reviews/`, etc.) are still useful for cross-feature views and remain the canonical location for standalone artifacts (one-off debug sessions, global audits, etc.)

**Rule of thumb:**
- **Feature folder** when the work spans 2+ phases and has a clear name ("dark mode", "pg15 migration")
- **Type folder** when the work is a one-off (a single plan, a standalone review, an ad-hoc debug) or spans no specific feature

---

## Inherited Context — how agents read prior artifacts

Before starting work, every engineering agent should check for prior artifacts in the active feature folder:

1. **Is there a feature folder for this work?** Look for `workspace/development/features/{slug}/`
2. **If yes**, read in order: discovery → PRD → plan → architecture → any prior reviews/verifications
3. **Inherit** constraints, decisions, and open questions — don't re-litigate them
4. **If unclear** which feature this is, ask the user or call `@helm-conductor`

This is how EvoNexus avoids each agent being an island: context flows forward through the feature folder.

---

## Handoff protocol

When one agent hands off to another, the handoff includes:

- **Source artifact:** path to the file produced (PRD, plan, architecture, etc.)
- **What was done:** 1-2 sentences
- **What's open:** unresolved questions or decisions deferred
- **Expected output:** what the next agent should produce and where

Example handoff:
> "Compass → Bolt: plan saved to `workspace/development/features/dark-mode/[C]plan-dark-mode.md`. Architecture pending (Apex). Open question: token storage strategy (see plan §Open Questions). Expected: implementation against steps 1-5 + self-verification."

---

## When to skip phases

Not every change deserves all 6 phases. Use judgment:

| Change type | Phases to use |
|---|---|
| Typo, comment fix, rename | Build only |
| Small bug fix with clear repro | Build → Verify |
| Feature with clear acceptance criteria | Planning → Build → Verify |
| New feature with ambiguity | Discovery → Planning → Build → Verify |
| High-stakes architectural change | All 6 phases |
| Post-incident fix | Discovery (trail-tracer) → Build → Verify → Retro |

**Default:** when in doubt, ask `@helm-conductor` or `@compass-planner` which phases apply.
