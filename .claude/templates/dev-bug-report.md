---
author: claude
agent: hawk-debugger
type: bug-report
date: {{YYYY-MM-DD}}
component: {{component-or-file}}
severity: critical | high | medium | low
status: investigating | root-caused | fix-proposed | fixed | wontfix
---

# Bug Report — {{Title}}

## Symptom
[What the user / observer sees. The visible failure.]

## Reproduction
1. [step 1]
2. [step 2]
3. [step 3]

**Frequency:** consistent | intermittent | one-time
**Environment:** [OS, version, config]

## Root Cause
[The actual underlying issue, not the symptom. Cite file:line.]

- **Where it manifests:** `path/to/file.ext:42`
- **Where the root cause originates:** `path/to/other.ext:108`

## Hypothesis Tested
[How the root cause was confirmed — what was the disproving experiment?]

## Fix
[Minimal code change needed]

```diff
- old line
+ new line
```

**Lines changed:** {{N}}
**Files affected:** {{M}}

## Verification
- [ ] [how to prove the fix works — test command, manual check]
- [ ] [regression check — what else could be affected]

## Similar Patterns Checked
- `path/to/similar1.ext` — [status: clean / also affected]
- `path/to/similar2.ext` — [status: clean / also affected]

## Failed Hypotheses (3-failure circuit breaker tracking)
1. [hypothesis 1] — disproved by [evidence]
2. [hypothesis 2] — disproved by [evidence]
3. [hypothesis 3] — disproved by [evidence]

[If 3 failed → escalate to @apex-architect]

## References
- Stack trace: [file]
- Git blame: `commit-sha` introduced this at `file:line`
- Related issue: #XXX
