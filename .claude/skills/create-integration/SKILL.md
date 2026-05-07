---
name: create-integration
description: "Create a new custom integration (API/service wrapper) for the workspace. Guides the user through defining the integration's slug, display name, description, category, and required env keys. Writes .claude/skills/custom-int-{slug}/SKILL.md via POST /api/integrations/custom. Use when the user says 'create an integration', 'add a new integration', 'new custom integration', 'I want to connect X to the workspace', or wants to wire up a new external API/service."
---

# Create Custom Integration

Guide the user through creating a new custom integration — a wrapper around an external API or service that the workspace's agents can use.

## What You're Building

A custom integration is a skill with the `custom-int-` prefix:
- Lives in `.claude/skills/custom-int-{slug}/SKILL.md`
- Gitignored (personal to the workspace, not shipped)
- Appears in the dashboard `/integrations` page under the "Custom Integrations" section
- Documents the env keys, auth method, and example calls so agents know how to use it

## When to use

Use when the user wants to connect a new external API/service that isn't already in the core integration list (Stripe, Omie, Discord, Telegram, etc.). If the integration already exists as core (`int-*`), don't duplicate — extend or use the existing one.

## Step 1: Understand the Integration

Ask the user (short, direct):

1. **Display name** — e.g., "Airtable", "Notion Databases", "Custom CRM". Human-readable.
2. **Slug** — kebab-case ID (e.g., `airtable`). Auto-suggest from display name, let them override. Must be `[a-z0-9-]+` and not already taken.
3. **Category** — one of:
   - `messaging` (WhatsApp, Telegram, Discord, email)
   - `payments` (Stripe, Asaas, Pix, crypto)
   - `crm` (HubSpot, Salesforce, Pipedrive)
   - `social` (Instagram, LinkedIn, YouTube, TikTok)
   - `productivity` (Notion, Airtable, ClickUp, Linear)
   - `other`
4. **Description** — 1-2 sentences. What does this integration do? What would agents use it for?
5. **Env keys** — what environment variables are needed? Ex: `AIRTABLE_API_KEY`, `AIRTABLE_BASE_ID`. List names only (no values — the user adds those to `.env` later).
6. **Auth method** (optional, guides the SKILL.md template body) — bearer token, API key in header, OAuth, basic auth, none.
7. **Base URL** (optional) — the API's root URL. Helps generate example calls.

## Step 2: Verify slug uniqueness

Check the existing integrations (core + custom) to make sure the slug isn't taken:

```python
from dashboard.backend.sdk_client import evo
existing = evo.get("/api/integrations")
taken = [i["slug"] for i in existing]
if slug in taken or f"int-{slug}" in taken or f"custom-int-{slug}" in taken:
    # ask user for a different slug
```

Also grep the filesystem as a safety check:

```bash
ls .claude/skills/int-{slug} .claude/skills/custom-int-{slug} 2>/dev/null
```

## Step 3: Call the API

Use `from dashboard.backend.sdk_client import evo` — auto-handles URL + auth.

```python
import json
from dashboard.backend.sdk_client import evo
integration = evo.post("/api/integrations/custom", {
    "slug": "airtable",
    "displayName": "Airtable",
    "description": "Query and update Airtable bases. Use when agents need to read/write records in Airtable tables.",
    "category": "productivity",
    "envKeys": ["AIRTABLE_API_KEY", "AIRTABLE_BASE_ID"],
})
print(json.dumps(integration))
```

The backend creates `.claude/skills/custom-int-{slug}/SKILL.md` with a template that documents setup, env keys, and usage. Response shape matches the standard integration entry (with `kind: "custom"`).

## Step 4: Add env keys to .env

Remind the user to add the env keys to `.env` (locally) and, if deploying, to the production `.env` too:

```
AIRTABLE_API_KEY=<value>
AIRTABLE_BASE_ID=<value>
```

The dashboard shows the integration as "Not configured" until the env keys are set.

## Step 5: Fill in the SKILL.md body

The backend creates a minimal template. The user (or an agent they delegate to) should flesh out the SKILL.md with:
- Auth details (how the API expects credentials)
- Base URL and common endpoints
- Example calls with `from dashboard.backend.sdk_client import evo` OR direct HTTP using `requests` / `httpx`
- Rate limits, quirks, response shapes

Offer to open the file for editing or to delegate to a specialist agent (e.g., `@apex-architect` for architecture review, `@quill-writer` for docs polish).

## Step 6: Show what happens next

Explain to the user:

1. The integration now appears in `/integrations` → "Custom Integrations" section with a `[Custom]` badge
2. Agents can discover it via skill search (it's indexed as a skill)
3. Edit description/env keys anytime via the pencil icon on the card
4. Delete via the trash icon (removes the SKILL.md folder entirely)
5. The SKILL.md is gitignored — doesn't leak into the upstream repo

## Notes

- If the user just wants to describe a local script (no external API), suggest `create-routine` or `create-command` instead.
- If the integration needs complex state (OAuth tokens, pagination cursors), recommend the user ask `@apex-architect` to design the adapter before filling in SKILL.md.
- Custom integrations share the same discoverability as core ones — mentioning them in an agent chat (`@agent please call my airtable integration`) works once the env is set.

Related: `.claude/rules/integrations.md`, `.claude/rules/skills.md`, `create-agent`, `create-command`.
