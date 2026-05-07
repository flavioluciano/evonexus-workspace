Review recent changes and suggest next actions. Run these steps:

1. Run `git diff --stat HEAD~5` to see recent file changes
2. Run `git log --oneline -10` to understand recent work
3. Check agent memory for recent activity: `ls -lt .claude/agent-memory/ 2>/dev/null | head -10`
4. Check for any pending items in today's logs

Present:
- What was done recently (based on commits and logs)
- What changed (modified files)
- Concrete suggestion of what to do next (1-3 prioritized items)
- Blockers or items needing attention
