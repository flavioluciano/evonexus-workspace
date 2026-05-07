---
name: create-command
description: "Create a new slash command for Claude Code. Guides the user through defining the command name, what it does, and generates the markdown file in .claude/commands/. Use when the user says 'create a command', 'new command', 'add a slash command', 'I want a shortcut for', or wants to create a reusable slash command."
---

# Create Slash Command

Guide the user through creating a new slash command for Claude Code.

## What You're Building

A slash command is a `.md` file in `.claude/commands/` that acts as a shortcut. When the user types `/command-name` in Claude Code, the file contents are injected as the prompt.

Commands are simpler than skills — they're one-liners or short instructions, not multi-step workflows.

## Step 1: Understand the Command

Ask the user:
1. **What should this command do?** (e.g., "check deploy status", "run linting", "summarize this file")
2. **What name?** Short, memorable. The file will be `{name}.md` and invoked as `/{name}`
3. **Does it take arguments?** If yes, use `$ARGUMENTS` placeholder
4. **Should it invoke an agent?** If it's domain-specific, point to the right agent

## Step 2: Generate the Command File

Create `.claude/commands/{name}.md`:

### Simple command (no agent)

```markdown
{Instruction for what Claude should do}: $ARGUMENTS

If no arguments were provided, {fallback behavior}.
```

### Agent command

```markdown
Use the @{agent-name} agent to help the user with the following: $ARGUMENTS

If no arguments were provided, ask the user how you can help ({list of things this command handles}).
```

### Command with specific steps

```markdown
---
description: "{short description}"
---

Run these steps:

1. {step 1}
2. {step 2}
3. {step 3}

Context: $ARGUMENTS
```

## Step 3: Verify

```bash
ls -la .claude/commands/{name}.md
```

Tell the user:
- Command created: `/{name}`
- Invoke in Claude Code: `/{name}` or `/{name} some arguments`
- To edit: `.claude/commands/{name}.md`
- To delete: remove the file

## Examples

### Quick status check
`.claude/commands/deploy.md`:
```markdown
Check the deployment status of the current branch. Run `gh run list --limit 5` and summarize: which workflows passed, which failed, and if there are any in progress.
```

### Agent shortcut
`.claude/commands/tickets.md`:
```markdown
Use the @atlas-project agent to review open tickets: $ARGUMENTS

If no arguments were provided, show a summary of open issues by priority.
```

### Multi-step workflow
`.claude/commands/pr-check.md`:
```markdown
---
description: "Pre-PR checklist"
---

Run these steps before opening a PR:

1. Run `git diff --stat main` to see what changed
2. Check for any TODO or FIXME comments in changed files
3. Run the test suite
4. Summarize: files changed, tests passing, any concerns
```

### Custom prefix (gitignored)

For personal commands that shouldn't be committed:
`.claude/commands/custom-{name}.md`

Commands with `custom-` prefix are gitignored — personal to your workspace.

## Naming Convention

| Pattern | Example | Use case |
|---------|---------|----------|
| `{verb}` | `/deploy`, `/lint` | Action commands |
| `{noun}` | `/tickets`, `/costs` | View/query commands |
| `{agent}` | `/clawdia`, `/flux` | Agent shortcuts |
| `custom-{name}` | `/custom-mycheck` | Personal, gitignored |

Rules:
- Lowercase, hyphen-separated
- Keep names short (1-2 words)
- Avoid names that conflict with existing commands
- Use `custom-` prefix for personal commands (gitignored)

## Existing Commands

| Command | What it does |
|---------|-------------|
| `/clawdia` | Ops agent |
| `/flux` | Finance agent |
| `/atlas` | Projects agent |
| `/pulse` | Community agent |
| `/pixel` | Social media agent |
| `/sage` | Strategy agent |
| `/nex` | Sales agent |
| `/mentor` | Courses agent |
| `/kai` | Personal agent |
| `/status` | Workspace status check |
| `/review` | Review recent changes |

## Command vs Skill

| | Command | Skill |
|---|---|---|
| **Complexity** | Simple (1-10 lines) | Complex (multi-step workflows) |
| **Location** | `.claude/commands/` | `.claude/skills/` |
| **Trigger** | Only via `/name` | Auto-triggered by description match |
| **Arguments** | `$ARGUMENTS` placeholder | N/A (triggered by context) |
| **Use case** | Shortcuts, quick actions | Domain workflows, reports, integrations |

If what the user wants is a multi-step workflow with detailed instructions, suggest creating a skill instead (use the `create-routine` or just create a skill manually in `.claude/skills/`).
