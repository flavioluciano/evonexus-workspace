Quick workspace status check. Run these steps:

1. Run `git status` to show working tree state
2. Run `git log --oneline -5` to show recent commits
3. Check for recent ADW logs: `ls -lt ADWs/logs/ 2>/dev/null | head -10`
4. Check today's daily log if it exists: `ls "workspace/daily-logs/" 2>/dev/null | grep "$(date +%Y-%m-%d)" | head -5`

Present a concise summary with:
- Git state (branch, pending changes)
- Latest commits
- Latest routines executed
- Today's log (if it exists)
