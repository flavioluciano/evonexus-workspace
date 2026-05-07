# Automated Routines

Managed by the scheduler (`make scheduler`) — see `ROUTINES.md` for full details.

## Daily

| Time | Routine | Make | Agent |
|---------|--------|------|--------|
| 06:50 | Review Todoist | `make review` | @clawdia |
| 07:00 | Good Morning (briefing) | `make morning` | @clawdia |
| 07:15 | Email Triage | `make triage` | @clawdia |
| every 30min | Sync Meetings (Fathom) | `make sync` | @clawdia |
| 18:00 | Social Analytics | `make social` | @pixel |
| 18:30 | Licensing Daily | `make licensing` | @atlas |
| 19:00 | Financial Pulse | `make fin-pulse` | @flux |
| 20:00 | Community Pulse (Discord) | `make community` | @pulse |
| 20:15 | FAQ Sync | `make faq` | @pulse |
| 21:00 | End of Day | `make eod` | @clawdia |
| 21:15 | Memory Sync | `make memory` | @clawdia |
| 21:30 | Consolidated Dashboard | `make dashboard` | @clawdia |

## Weekly

| Day | Routine | Make | Agent |
|-----|--------|------|--------|
| Friday 07:30 | Financial Weekly | `make fin-weekly` | @flux |
| Friday 07:45 | Licensing Weekly | `make licensing-weekly` | @atlas |
| Friday 08:00 | Weekly Review | `make weekly` | @clawdia |
| Friday 08:15 | Social Analytics Weekly | `make social` | @pixel |
| Friday 08:30 | Trends | `make trends` | @clawdia |
| Friday 09:00 | Strategy Digest | `make strategy` | @sage |
| Mon/Wed/Fri 09:00 | Linear Review | `make linear` | @atlas |
| Mon/Wed/Fri 09:15 | GitHub Review | `make github` | @atlas |
| Monday 09:30 | Community Weekly | `make community-week` | @pulse |
| Sunday 09:00 | Memory Lint | `make memory-lint` | @clawdia |
| Sunday 09:45 | Learning Review Weekly | `make learn-weekly` | learn-* skills |
| Sunday 10:00 | Health Check-in | `make health` | @kai |

## Monthly (Day 1)

| Routine | Make | Agent |
|--------|------|--------|
| Monthly Close Kickoff | `make fin-close` | @flux |
| Community Monthly | `make community-month` | @pulse |
| Licensing Monthly | `make licensing-month` | @atlas |
| Social Analytics Monthly | `make social` | @pixel |
