---
author: claude
agent: raven-critic
type: critique
date: {{YYYY-MM-DD}}
target: {{plan-or-spec-name}}
verdict: REJECT | REVISE | ACCEPT-WITH-RESERVATIONS | ACCEPT
---

# Critique — {{Target}}

## VERDICT
**{{REJECT | REVISE | ACCEPT-WITH-RESERVATIONS | ACCEPT}}**

## Overall Assessment
[2-3 sentences]

## Pre-commitment Predictions
- **Predicted:** [3-5 problem areas you expected to find]
- **Found:** [what you actually found]

## Critical Findings
### [CRITICAL] {Title}
- **Evidence:** `file:line` or `"quote from artifact"`
- **Issue:** [what's wrong]
- **Fix:** [concrete recommendation]

## Major Findings
### [MAJOR] {Title}
- evidence + fix

## Minor Findings
- [MINOR] {title} + fix

## What's Missing
- [Gap 1] — [why it matters]
- [Gap 2] — [why it matters]

## Ambiguity Risks
- "{quote}" — could mean A or B, must clarify

## Multi-Perspective Notes
**For plans:**
- **Executor:** [perspective]
- **Stakeholder:** [perspective]
- **Skeptic:** [perspective]

**For code:**
- **Security engineer:** [perspective]
- **New-hire:** [perspective]
- **Ops engineer:** [perspective]

## Verdict Justification
[Why this verdict, what would change it, escalation rationale, Realist Check recalibrations]

## Open Questions
- [Low-confidence findings parked here]
