---
author: claude
agent: grid-tester
type: test-strategy
date: {{YYYY-MM-DD}}
component: {{component}}
---

# Test Strategy — {{Component}}

## Summary
- **Coverage:** X% → Y%
- **Test health:** 🟢 green / 🟡 yellow / 🔴 red
- **Pyramid balance:** unit X% / integration Y% / e2e Z%

## Tests Written
- `path/to/file.test.ts` — N tests covering [behavior]

## Coverage Gaps
| File | Lines | Logic | Risk |
|---|---|---|---|
| `file.ts` | 42-60 | [untested logic] | high/med/low |

## Flaky Tests Fixed
- `file.test.ts:42` — **Cause:** [root cause] — **Fix:** [what changed]

## TDD Cycles (if applicable)
1. RED: [test name] → ❌ failed as expected
2. GREEN: [code change] → ✅ passes
3. REFACTOR: [improvement] → ✅ still passes

## Verification
- `npm test` → ✅ N passed, 0 failed
- Multiple runs (5x): all green (flake check)
- Coverage: `coverage report` shows X% → Y%

## Recommendations
[next testing priorities]
