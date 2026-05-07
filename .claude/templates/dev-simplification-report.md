---
author: claude
agent: zen-simplifier
type: simplification-report
date: {{YYYY-MM-DD}}
scope: {{module-or-file}}
---

# Simplification Report — {{Scope}}

## Files Simplified
- `path/to/file.ts:42-60` — [what was simplified]
- `path/to/other.ts:108-150` — [what was simplified]

## Changes Applied
- **Naming:** [what was renamed and why]
- **Structure:** [nesting reduction, early returns, etc.]
- **Consistency:** [pattern alignment]
- **DRY:** [redundancy eliminated]

## Skipped
- `path/to/other.ts` — [reason: no meaningful improvement]

## Detected Style
- Naming: {camelCase | snake_case | PascalCase}
- Imports: {alphabetized | grouped}
- Error handling: {throw | Result type | callbacks}

## Verification
- ✅ Type check: 0 errors
- ✅ Build: exit 0
- ✅ Tests: all passed (no behavior change confirmed)

## Commits Created
1. `{hash}` — {message} — N files
2. `{hash}` — {message} — M files
