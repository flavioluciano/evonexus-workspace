---
author: claude
agent: oath-verifier
type: verification-report
date: {{YYYY-MM-DD}}
target: {{feature-or-task-name}}
verdict: PASS | FAIL | INCOMPLETE
confidence: high | medium | low
---

# Verification Report — {{Target}}

## Verdict

**Status:** {{PASS | FAIL | INCOMPLETE}}
**Confidence:** {{high | medium | low}}
**Blockers:** {{count — 0 means PASS}}

## Evidence

| Check | Result | Command/Source | Output |
|-------|--------|----------------|--------|
| Tests | ✅ pass / ❌ fail | `npm test` | X passed, Y failed |
| Types | ✅ pass / ❌ fail | `tsc --noEmit` | N errors |
| Lint | ✅ pass / ❌ fail | `npm run lint` | N warnings |
| Build | ✅ pass / ❌ fail | `npm run build` | exit code |
| Runtime | ✅ pass / ❌ fail | [manual check] | [observation] |

## Acceptance Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [criterion text] | ✅ VERIFIED / ⚠️ PARTIAL / ❌ MISSING | [specific evidence] |
| 2 | [criterion text] | ✅ / ⚠️ / ❌ | [specific evidence] |
| 3 | [criterion text] | ✅ / ⚠️ / ❌ | [specific evidence] |

## Gaps
- [Gap description] — **Risk:** high/medium/low — **Suggestion:** [how to close]

## Regression Risk Assessment
- **Related features checked:** [list]
- **Potentially affected:** [list]
- **Verified unaffected:** [list]

## Recommendation
**{{APPROVE | REQUEST_CHANGES | NEEDS_MORE_EVIDENCE}}**

[One-sentence justification]

## Follow-ups
- [ ] [action item if not PASS]
