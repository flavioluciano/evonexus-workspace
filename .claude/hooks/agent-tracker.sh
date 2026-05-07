#!/bin/bash
# Agent Activity Tracker Hook
# Writes active agent state to .claude/agent-status.json
# Used by dashboard to show which agents are running in real-time

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
STATUS_FILE="$PROJECT_DIR/.claude/agent-status.json"
EVENT="$CLAUDE_HOOK_EVENT"

# Initialize file if missing
if [ ! -f "$STATUS_FILE" ]; then
  echo '{"active_agents":[],"last_updated":""}' > "$STATUS_FILE"
fi

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$EVENT" = "PreToolUse" ]; then
  # Read tool input from stdin
  INPUT=$(cat)
  TOOL=$(echo "$INPUT" | grep -o '"tool_name":"[^"]*"' | head -1 | cut -d'"' -f4)

  if [ "$TOOL" = "Agent" ]; then
    # Extract agent type from input
    AGENT_TYPE=$(echo "$INPUT" | grep -o '"subagent_type":"[^"]*"' | head -1 | cut -d'"' -f4)
    DESCRIPTION=$(echo "$INPUT" | grep -o '"description":"[^"]*"' | head -1 | cut -d'"' -f4)

    if [ -z "$AGENT_TYPE" ]; then
      AGENT_TYPE="general-purpose"
    fi

    # Add to active agents (simple append, dedupe on read)
    python3 -c "
import json, sys
try:
    with open('$STATUS_FILE') as f:
        data = json.load(f)
except:
    data = {'active_agents': [], 'last_updated': ''}

data['active_agents'].append({
    'agent': '$AGENT_TYPE',
    'description': '$DESCRIPTION',
    'started_at': '$NOW'
})
# Keep only last 20 entries
data['active_agents'] = data['active_agents'][-20:]
data['last_updated'] = '$NOW'

with open('$STATUS_FILE', 'w') as f:
    json.dump(data, f)
" 2>/dev/null
  fi

elif [ "$EVENT" = "Stop" ]; then
  # Clear active agents on session stop
  echo "{\"active_agents\":[],\"last_updated\":\"$NOW\"}" > "$STATUS_FILE"
fi
