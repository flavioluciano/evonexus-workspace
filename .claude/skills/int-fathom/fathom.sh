#!/usr/bin/env bash
set -euo pipefail

# Fathom API CLI
# Usage: fathom.sh <command> [options]

BASE_URL="https://api.fathom.ai/external/v1"

# Load .env from .claude/ directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$(cd "$SCRIPT_DIR/../.." && pwd)/.env"
if [[ -f "$ENV_FILE" ]]; then
  while IFS='=' read -r key value; do
    key=$(echo "$key" | xargs)
    [[ -z "$key" || "$key" == \#* ]] && continue
    if [[ -z "${!key:-}" ]]; then
      export "$key=$value"
    fi
  done < "$ENV_FILE"
fi

API_KEY="${FATHOM_API_KEY:-}"

# Fallback: try reading from openclaw.json if env var not set
if [[ -z "$API_KEY" ]]; then
  CONFIG_FILE="${HOME}/.openclaw/openclaw.json"
  if [[ -f "$CONFIG_FILE" ]] && command -v jq &>/dev/null; then
    API_KEY=$(jq -r '.skills.entries.fathom.apiKey // .skills.entries.fathom.env.FATHOM_API_KEY // empty' "$CONFIG_FILE" 2>/dev/null || true)
  fi
fi

if [[ -z "$API_KEY" ]]; then
  echo "Error: FATHOM_API_KEY not set." >&2
  echo "Configure it in openclaw.json under skills.entries.fathom.apiKey" >&2
  exit 1
fi

# --- helpers ---

api_get() {
  local path="$1"
  shift
  local url="${BASE_URL}${path}"
  local attempt=0
  local max_retries=3

  while (( attempt < max_retries )); do
    local http_code
    local response
    response=$(curl -s -w "\n%{http_code}" --request GET \
      --url "$url" \
      --header "X-Api-Key: ${API_KEY}" \
      "$@" 2>/dev/null) || true

    http_code=$(echo "$response" | tail -1)
    local body
    body=$(echo "$response" | sed '$d')

    case "$http_code" in
      200) echo "$body"; return 0 ;;
      429)
        attempt=$((attempt + 1))
        local wait=$((attempt * 2))
        echo "Rate limited, retrying in ${wait}s..." >&2
        sleep "$wait"
        ;;
      401)
        echo "Error: Invalid API key (401 Unauthorized)" >&2
        exit 1
        ;;
      *)
        echo "Error: HTTP ${http_code}" >&2
        echo "$body" >&2
        exit 1
        ;;
    esac
  done
  echo "Error: Max retries exceeded (rate limited)" >&2
  exit 1
}

format_date() {
  local d="$1"
  # If it's just a date (no T), append T00:00:00Z
  if [[ "$d" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "${d}T00:00:00Z"
  else
    echo "$d"
  fi
}

# --- commands ---

cmd_meetings() {
  local params=()
  local fetch_all=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --include-summary)    params+=("include_summary=true"); shift ;;
      --include-transcript) params+=("include_transcript=true"); shift ;;
      --include-actions)    params+=("include_action_items=true"); shift ;;
      --include-crm)        params+=("include_crm_matches=true"); shift ;;
      --after)              params+=("created_after=$(format_date "$2")"); shift 2 ;;
      --before)             params+=("created_before=$(format_date "$2")"); shift 2 ;;
      --domains-type)       params+=("calendar_invitees_domains_type=$2"); shift 2 ;;
      --domains)            params+=("calendar_invitees_domains[]=$2"); shift 2 ;;
      --recorded-by)        params+=("recorded_by[]=$2"); shift 2 ;;
      --team)               params+=("teams[]=$2"); shift 2 ;;
      --cursor)             params+=("cursor=$2"); shift 2 ;;
      --all)                fetch_all=true; shift ;;
      *)                    echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  # Default: include domains type all
  local has_domains_type=false
  for p in "${params[@]+"${params[@]}"}"; do
    [[ "$p" == calendar_invitees_domains_type=* ]] && has_domains_type=true
  done
  if ! $has_domains_type; then
    params+=("calendar_invitees_domains_type=all")
  fi

  local query=""
  for p in "${params[@]+"${params[@]}"}"; do
    if [[ -z "$query" ]]; then
      query="?${p}"
    else
      query="${query}&${p}"
    fi
  done

  if $fetch_all; then
    local all_items="[]"
    local cursor=""
    local page=1

    while true; do
      local page_query="$query"
      if [[ -n "$cursor" ]]; then
        page_query="${page_query}&cursor=${cursor}"
      fi

      local result
      result=$(api_get "/meetings${page_query}")
      local items
      items=$(echo "$result" | jq -c '.items // []')
      all_items=$(echo "$all_items" "$items" | jq -s '.[0] + .[1]')

      cursor=$(echo "$result" | jq -r '.next_cursor // empty')
      if [[ -z "$cursor" ]]; then
        break
      fi
      page=$((page + 1))
      echo "Fetching page ${page}..." >&2
    done

    echo "$all_items" | jq '.'
  else
    api_get "/meetings${query}" | jq '.'
  fi
}

cmd_summary() {
  local recording_id="${1:?Usage: fathom.sh summary <recording_id>}"
  api_get "/recordings/${recording_id}/summary" | jq '.'
}

cmd_transcript() {
  local recording_id="${1:?Usage: fathom.sh transcript <recording_id>}"
  api_get "/recordings/${recording_id}/transcript" | jq '.'
}

cmd_teams() {
  local cursor=""
  local all_items="[]"

  while true; do
    local query=""
    [[ -n "$cursor" ]] && query="?cursor=${cursor}"

    local result
    result=$(api_get "/teams${query}")
    local items
    items=$(echo "$result" | jq -c '.items // []')
    all_items=$(echo "$all_items" "$items" | jq -s '.[0] + .[1]')

    cursor=$(echo "$result" | jq -r '.next_cursor // empty')
    [[ -z "$cursor" ]] && break
  done

  echo "$all_items" | jq '.'
}

cmd_members() {
  local team_filter=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --team) team_filter="$2"; shift 2 ;;
      *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
  done

  local cursor=""
  local all_items="[]"

  while true; do
    local query=""
    if [[ -n "$team_filter" ]]; then
      query="?team=${team_filter}"
    fi
    if [[ -n "$cursor" ]]; then
      [[ -n "$query" ]] && query="${query}&cursor=${cursor}" || query="?cursor=${cursor}"
    fi

    local result
    result=$(api_get "/team_members${query}")
    local items
    items=$(echo "$result" | jq -c '.items // []')
    all_items=$(echo "$all_items" "$items" | jq -s '.[0] + .[1]')

    cursor=$(echo "$result" | jq -r '.next_cursor // empty')
    [[ -z "$cursor" ]] && break
  done

  echo "$all_items" | jq '.'
}

cmd_help() {
  cat <<'EOF'
Fathom CLI - Meeting recordings, transcripts & summaries

Usage: fathom.sh <command> [options]

Commands:
  meetings    List meetings (with optional filters)
  summary     Get summary for a recording
  transcript  Get transcript for a recording
  teams       List teams
  members     List team members
  help        Show this help

Meetings options:
  --include-summary       Include AI summary
  --include-transcript    Include full transcript
  --include-actions       Include action items
  --include-crm           Include CRM matches
  --after <date>          Filter: created after (YYYY-MM-DD or ISO 8601)
  --before <date>         Filter: created before
  --domains-type <type>   all | only_internal | one_or_more_external
  --domains <domain>      Filter by invitee domain (e.g. acme.com)
  --recorded-by <email>   Filter by recorder email
  --team <name>           Filter by team name
  --all                   Fetch all pages (default: first page only)

Members options:
  --team <name>           Filter by team name

Examples:
  fathom.sh meetings --after "2026-03-01" --include-summary
  fathom.sh summary 123456789
  fathom.sh transcript 123456789
  fathom.sh meetings --domains "client.com" --include-actions
  fathom.sh teams
  fathom.sh members --team "Engineering"
EOF
}

# --- main ---

command="${1:-help}"
shift || true

case "$command" in
  meetings)    cmd_meetings "$@" ;;
  summary)     cmd_summary "$@" ;;
  transcript)  cmd_transcript "$@" ;;
  teams)       cmd_teams "$@" ;;
  members)     cmd_members "$@" ;;
  help|--help|-h) cmd_help ;;
  *)
    echo "Unknown command: $command" >&2
    echo "Run 'fathom.sh help' for usage." >&2
    exit 1
    ;;
esac
