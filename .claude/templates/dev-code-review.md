---
author: claude
agent: lens-reviewer
type: code-review
date: {{YYYY-MM-DD}}
target: {{pr-number-or-files}}
verdict: APPROVE | REQUEST_CHANGES | COMMENT
---

# Code Review — {{Target}}

## Summary
**Files reviewed:** {{N}}
**Total issues:** {{Y}}

### By Severity
- **CRITICAL:** {{X}} (must fix)
- **HIGH:** {{Y}} (should fix)
- **MEDIUM:** {{Z}} (consider fixing)
- **LOW:** {{W}} (optional)

## Stage 1 — Spec Compliance

| Requirement | Status | Notes |
|---|---|---|
| [requirement 1] | ✅ MET / ⚠️ PARTIAL / ❌ MISSING | [evidence] |
| [requirement 2] | ✅ / ⚠️ / ❌ | [evidence] |

## Stage 2 — Code Quality

### Issues Found

#### [CRITICAL] {{title}}
- **File:** `path/to/file.ext:42`
- **Issue:** [what's wrong]
- **Why it matters:** [impact]
- **Fix:** [concrete suggestion]

#### [HIGH] {{title}}
- **File:** `path/to/file.ext:108`
- **Issue:** [what's wrong]
- **Why it matters:** [impact]
- **Fix:** [concrete suggestion]

[... continue per severity tier]

## Security Checklist
- [ ] No hardcoded secrets
- [ ] Inputs sanitized
- [ ] Injection prevented
- [ ] XSS prevented
- [ ] Auth enforced

## Code Quality Checklist
- [ ] Functions < 50 lines
- [ ] Cyclomatic complexity < 10
- [ ] No deeply nested code (> 4 levels)
- [ ] No duplicate logic
- [ ] Clear, descriptive naming

## Positive Observations
- [thing done well 1]
- [thing done well 2]

## Recommendation
**{{APPROVE | REQUEST_CHANGES | COMMENT}}**

[1-sentence justification]

## Follow-ups
- [ ] [action item if REQUEST_CHANGES]
