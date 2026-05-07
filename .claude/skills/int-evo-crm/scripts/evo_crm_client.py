#!/usr/bin/env python3
"""
Evo AI CRM client - calls the CRM REST API directly.
No third-party SDK dependency. Uses only Python stdlib.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path


def _load_dotenv():
    """Load .env from workspace root."""
    env_path = Path(__file__).resolve().parents[4] / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()


def get_config():
    url = os.environ.get("EVO_CRM_URL")
    token = os.environ.get("EVO_CRM_TOKEN")
    errors = []
    if not url:
        errors.append("EVO_CRM_URL")
    if not token:
        errors.append("EVO_CRM_TOKEN")
    if errors:
        print(json.dumps({
            "success": False,
            "error": f"Missing env var(s): {', '.join(errors)}. Set them before running this script."
        }))
        sys.exit(1)
    return url.rstrip("/"), token


def api_request(method, path, params=None, body=None):
    """Make an HTTP request to the CRM API and return parsed JSON."""
    base_url, token = get_config()
    url = f"{base_url}/api/v1/{path}"

    if params:
        # Filter out None values
        clean = {k: v for k, v in params.items() if v is not None}
        if clean:
            url += "?" + urllib.parse.urlencode(clean)

    data = json.dumps(body).encode("utf-8") if body is not None else None

    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "api_access_token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return {"success": True}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read())
        except Exception:
            error_body = {"message": e.reason}
        print(json.dumps({
            "success": False,
            "error": f"CRM API error {e.code}",
            "details": error_body,
        }))
        sys.exit(1)


def output(data, meta=None):
    """Print JSON result to stdout."""
    result = {"success": True, "data": data}
    if meta:
        result["meta"] = meta
    print(json.dumps(result, indent=2, default=str))


# ---------------------------------------------------------------------------
# CONTACTS
# ---------------------------------------------------------------------------

def cmd_contacts(args):
    params = {"page": args.page}
    if args.sort:
        params["sort"] = args.sort
    resp = api_request("GET", "contacts", params=params)
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_contact(args):
    resp = api_request("GET", f"contacts/{args.id}")
    output(resp)


def cmd_search_contacts(args):
    resp = api_request("GET", "contacts/search", params={"q": args.q, "page": args.page})
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_filter_contacts(args):
    body = json.loads(args.payload)
    params = {"page": args.page}
    resp = api_request("POST", "contacts/filter", params=params, body=body)
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_create_contact(args):
    body = {"name": args.name}
    if args.email:
        body["email"] = args.email
    if args.phone:
        body["phone_number"] = args.phone
    resp = api_request("POST", "contacts", body=body)
    output(resp)


def cmd_update_contact(args):
    body = {}
    if args.name:
        body["name"] = args.name
    if args.email:
        body["email"] = args.email
    if args.phone:
        body["phone_number"] = args.phone
    if not body:
        print(json.dumps({"success": False, "error": "No fields to update"}))
        sys.exit(1)
    resp = api_request("PUT", f"contacts/{args.id}", body=body)
    output(resp)


def cmd_delete_contact(args):
    api_request("DELETE", f"contacts/{args.id}")
    print(json.dumps({"success": True, "message": f"Contact {args.id} deleted"}))


def cmd_contact_conversations(args):
    resp = api_request("GET", f"contacts/{args.id}/conversations")
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_contact_notes(args):
    resp = api_request("GET", f"contacts/{args.id}/notes")
    output(resp.get("data", resp))


def cmd_create_contact_note(args):
    body = {"content": args.content}
    resp = api_request("POST", f"contacts/{args.id}/notes", body=body)
    output(resp)


def cmd_contact_pipelines(args):
    resp = api_request("GET", f"contacts/{args.id}/pipelines")
    output(resp.get("data", resp))


# ---------------------------------------------------------------------------
# CONVERSATIONS
# ---------------------------------------------------------------------------

def cmd_conversations(args):
    params = {
        "status": args.status,
        "assignee_type": args.assignee_type,
        "inbox_id": args.inbox_id,
        "page": args.page,
    }
    resp = api_request("GET", "conversations", params=params)
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_conversation(args):
    resp = api_request("GET", f"conversations/{args.id}")
    output(resp)


def cmd_search_conversations(args):
    resp = api_request("GET", "conversations/search", params={"q": args.q, "page": args.page})
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_filter_conversations(args):
    body = json.loads(args.payload)
    params = {"page": args.page}
    resp = api_request("POST", "conversations/filter", params=params, body=body)
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_conversation_meta(args):
    params = {
        "status": args.status,
        "assignee_type": args.assignee_type,
    }
    resp = api_request("GET", "conversations/meta", params=params)
    output(resp)


def cmd_create_conversation(args):
    body = {
        "contact_id": args.contact_id,
        "inbox_id": args.inbox_id,
    }
    resp = api_request("POST", "conversations", body=body)
    output(resp)


def cmd_assign_conversation(args):
    body = {"assignee_id": args.assignee_id}
    resp = api_request("POST", f"conversations/{args.id}/assignments", body=body)
    output(resp)


def cmd_toggle_status(args):
    body = {"status": args.status}
    resp = api_request("POST", f"conversations/{args.id}/toggle_status", body=body)
    output(resp)


def cmd_toggle_priority(args):
    body = {"priority": args.priority}
    resp = api_request("POST", f"conversations/{args.id}/toggle_priority", body=body)
    output(resp)


def cmd_mute_conversation(args):
    resp = api_request("POST", f"conversations/{args.id}/mute")
    output(resp)


def cmd_unmute_conversation(args):
    resp = api_request("POST", f"conversations/{args.id}/unmute")
    output(resp)


def cmd_mark_unread(args):
    resp = api_request("POST", f"conversations/{args.id}/unread")
    output(resp)


def cmd_send_transcript(args):
    body = {"email": args.email}
    resp = api_request("POST", f"conversations/{args.id}/transcript", body=body)
    output(resp)


# ---------------------------------------------------------------------------
# MESSAGES
# ---------------------------------------------------------------------------

def cmd_messages(args):
    resp = api_request("GET", f"conversations/{args.conversation_id}/messages")
    payload = resp.get("data", {}).get("payload", resp.get("data", resp))
    meta = resp.get("data", {}).get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_create_message(args):
    body = {"content": args.content, "message_type": "outgoing"}
    if args.private:
        body["private"] = True
        body["message_type"] = "outgoing"
    resp = api_request("POST", f"conversations/{args.conversation_id}/messages", body=body)
    output(resp)


def cmd_update_message(args):
    body = {"content": args.content}
    resp = api_request("PATCH", f"conversations/{args.conversation_id}/messages/{args.message_id}", body=body)
    output(resp)


def cmd_delete_message(args):
    api_request("DELETE", f"conversations/{args.conversation_id}/messages/{args.message_id}")
    print(json.dumps({"success": True, "message": f"Message {args.message_id} deleted"}))


def cmd_retry_message(args):
    resp = api_request("POST", f"conversations/{args.conversation_id}/messages/{args.message_id}/retry")
    output(resp)


# ---------------------------------------------------------------------------
# INBOXES
# ---------------------------------------------------------------------------

def cmd_inboxes(args):
    resp = api_request("GET", "inboxes")
    output(resp.get("payload", resp.get("data", resp)))


def cmd_inbox(args):
    resp = api_request("GET", f"inboxes/{args.id}")
    output(resp)


def cmd_inbox_agents(args):
    resp = api_request("GET", f"inbox_members/{args.inbox_id}")
    output(resp.get("payload", resp.get("data", resp)))


def cmd_assignable_agents(args):
    resp = api_request("GET", f"inboxes/{args.inbox_id}/assignable_agents")
    output(resp.get("payload", resp.get("data", resp)))


def cmd_inbox_templates(args):
    resp = api_request("GET", f"inboxes/{args.inbox_id}/message_templates")
    output(resp.get("payload", resp.get("data", resp)))


# ---------------------------------------------------------------------------
# PIPELINES
# ---------------------------------------------------------------------------

def cmd_pipelines(args):
    resp = api_request("GET", "pipelines")
    output(resp.get("data", resp))


def cmd_pipeline(args):
    resp = api_request("GET", f"pipelines/{args.id}")
    output(resp)


def cmd_pipeline_stats(args):
    resp = api_request("GET", "pipelines/stats")
    output(resp.get("data", resp))


def cmd_pipeline_stat(args):
    resp = api_request("GET", f"pipelines/{args.id}/stats")
    output(resp)


def cmd_pipeline_stages(args):
    resp = api_request("GET", f"pipelines/{args.pipeline_id}/pipeline_stages")
    output(resp.get("data", resp))


def cmd_pipeline_items(args):
    params = {"page": args.page}
    if args.stage_id:
        params["stage_id"] = args.stage_id
    resp = api_request("GET", f"pipelines/{args.pipeline_id}/pipeline_items", params=params)
    data = resp.get("data", resp)
    if isinstance(data, list):
        payload = data
        meta = resp.get("meta")
    else:
        payload = data.get("payload", data)
        meta = data.get("meta", resp.get("meta"))
    output(payload, meta)


def cmd_create_pipeline_item(args):
    body = {
        "contact_id": args.contact_id,
        "stage_id": args.stage_id,
    }
    resp = api_request("POST", f"pipelines/{args.pipeline_id}/pipeline_items", body=body)
    output(resp)


def cmd_move_item(args):
    body = {"stage_id": args.stage_id}
    resp = api_request("POST", f"pipelines/{args.pipeline_id}/pipeline_items/{args.item_id}/move_to_stage", body=body)
    output(resp)


def cmd_bulk_move_items(args):
    item_ids = [x.strip() for x in args.item_ids.split(",")]
    body = {"item_ids": item_ids, "stage_id": args.stage_id}
    resp = api_request("POST", f"pipelines/{args.pipeline_id}/pipeline_items/bulk_move", body=body)
    output(resp)


def cmd_remove_pipeline_item(args):
    api_request("DELETE", f"pipelines/{args.pipeline_id}/pipeline_items/{args.item_id}")
    print(json.dumps({"success": True, "message": f"Pipeline item {args.item_id} removed"}))


def cmd_pipeline_items_stats(args):
    resp = api_request("GET", f"pipelines/{args.pipeline_id}/pipeline_items/stats")
    output(resp)


# ---------------------------------------------------------------------------
# LABELS
# ---------------------------------------------------------------------------

def cmd_contact_labels(args):
    resp = api_request("GET", f"contacts/{args.contact_id}/labels")
    output(resp.get("payload", resp.get("data", resp)))


def cmd_add_contact_labels(args):
    labels = [x.strip() for x in args.labels.split(",")]
    body = {"labels": labels}
    resp = api_request("POST", f"contacts/{args.contact_id}/labels", body=body)
    output(resp)


def cmd_conversation_labels(args):
    resp = api_request("GET", f"conversations/{args.conversation_id}/labels")
    output(resp.get("payload", resp.get("data", resp)))


def cmd_add_conversation_labels(args):
    labels = [x.strip() for x in args.labels.split(",")]
    body = {"labels": labels}
    resp = api_request("POST", f"conversations/{args.conversation_id}/labels", body=body)
    output(resp)


# ---------------------------------------------------------------------------
# CLI PARSER
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evo AI CRM REST API client")
    sub = parser.add_subparsers(dest="command")

    # --- Contacts ---
    p = sub.add_parser("contacts", help="List contacts")
    p.add_argument("--sort", help="Sort field (e.g. name)")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("contact", help="Get contact details")
    p.add_argument("id")

    p = sub.add_parser("search_contacts", help="Search contacts")
    p.add_argument("--q", required=True, help="Search term")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("filter_contacts", help="Advanced filter contacts")
    p.add_argument("--payload", required=True, help="JSON filter payload")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("create_contact", help="Create a contact")
    p.add_argument("--name", required=True)
    p.add_argument("--email")
    p.add_argument("--phone")

    p = sub.add_parser("update_contact", help="Update a contact")
    p.add_argument("id")
    p.add_argument("--name")
    p.add_argument("--email")
    p.add_argument("--phone")

    p = sub.add_parser("delete_contact", help="Delete a contact")
    p.add_argument("id")

    p = sub.add_parser("contact_conversations", help="List contact conversations")
    p.add_argument("id")

    p = sub.add_parser("contact_notes", help="List contact notes")
    p.add_argument("id")

    p = sub.add_parser("create_contact_note", help="Add a note to a contact")
    p.add_argument("id")
    p.add_argument("--content", required=True)

    p = sub.add_parser("contact_pipelines", help="Get contact pipelines")
    p.add_argument("id")

    # --- Conversations ---
    p = sub.add_parser("conversations", help="List conversations")
    p.add_argument("--status", default="open")
    p.add_argument("--assignee_type", default="all")
    p.add_argument("--inbox_id")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("conversation", help="Get conversation details")
    p.add_argument("id")

    p = sub.add_parser("search_conversations", help="Search conversations")
    p.add_argument("--q", required=True)
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("filter_conversations", help="Advanced filter conversations")
    p.add_argument("--payload", required=True, help="JSON filter payload")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("conversation_meta", help="Conversation counts by status")
    p.add_argument("--status", default="open")
    p.add_argument("--assignee_type", default="all")

    p = sub.add_parser("create_conversation", help="Create a conversation")
    p.add_argument("--contact_id", required=True)
    p.add_argument("--inbox_id", required=True)

    p = sub.add_parser("assign_conversation", help="Assign conversation to agent")
    p.add_argument("id")
    p.add_argument("--assignee_id", required=True)

    p = sub.add_parser("toggle_status", help="Toggle conversation status")
    p.add_argument("id")
    p.add_argument("--status", required=True, choices=["open", "resolved", "pending", "snoozed"])

    p = sub.add_parser("toggle_priority", help="Set conversation priority")
    p.add_argument("id")
    p.add_argument("--priority", required=True, choices=["none", "low", "medium", "high", "urgent"])

    p = sub.add_parser("mute_conversation", help="Mute conversation")
    p.add_argument("id")

    p = sub.add_parser("unmute_conversation", help="Unmute conversation")
    p.add_argument("id")

    p = sub.add_parser("mark_unread", help="Mark conversation as unread")
    p.add_argument("id")

    p = sub.add_parser("send_transcript", help="Email conversation transcript")
    p.add_argument("id")
    p.add_argument("--email", required=True)

    # --- Messages ---
    p = sub.add_parser("messages", help="List messages in conversation")
    p.add_argument("conversation_id")

    p = sub.add_parser("create_message", help="Send message or private note")
    p.add_argument("conversation_id")
    p.add_argument("--content", required=True)
    p.add_argument("--private", action="store_true", help="Create as private note")

    p = sub.add_parser("update_message", help="Update a message")
    p.add_argument("conversation_id")
    p.add_argument("message_id")
    p.add_argument("--content", required=True)

    p = sub.add_parser("delete_message", help="Delete a message")
    p.add_argument("conversation_id")
    p.add_argument("message_id")

    p = sub.add_parser("retry_message", help="Retry a failed message")
    p.add_argument("conversation_id")
    p.add_argument("message_id")

    # --- Inboxes ---
    sub.add_parser("inboxes", help="List all inboxes")

    p = sub.add_parser("inbox", help="Get inbox details")
    p.add_argument("id")

    p = sub.add_parser("inbox_agents", help="List agents in inbox")
    p.add_argument("inbox_id")

    p = sub.add_parser("assignable_agents", help="Get assignable agents for inbox")
    p.add_argument("inbox_id")

    p = sub.add_parser("inbox_templates", help="List message templates for inbox")
    p.add_argument("inbox_id")

    # --- Pipelines ---
    sub.add_parser("pipelines", help="List all pipelines")

    p = sub.add_parser("pipeline", help="Get pipeline details")
    p.add_argument("id")

    sub.add_parser("pipeline_stats", help="Get stats for all pipelines")

    p = sub.add_parser("pipeline_stat", help="Get stats for a pipeline")
    p.add_argument("id")

    p = sub.add_parser("pipeline_stages", help="List stages in a pipeline")
    p.add_argument("pipeline_id")

    p = sub.add_parser("pipeline_items", help="List items in a pipeline")
    p.add_argument("pipeline_id")
    p.add_argument("--stage_id")
    p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("create_pipeline_item", help="Add item to pipeline")
    p.add_argument("pipeline_id")
    p.add_argument("--contact_id", required=True)
    p.add_argument("--stage_id", required=True)

    p = sub.add_parser("move_item", help="Move item to different stage")
    p.add_argument("pipeline_id")
    p.add_argument("item_id")
    p.add_argument("--stage_id", required=True)

    p = sub.add_parser("bulk_move_items", help="Bulk move items to stage")
    p.add_argument("pipeline_id")
    p.add_argument("--item_ids", required=True, help="Comma-separated item IDs")
    p.add_argument("--stage_id", required=True)

    p = sub.add_parser("remove_pipeline_item", help="Remove item from pipeline")
    p.add_argument("pipeline_id")
    p.add_argument("item_id")

    p = sub.add_parser("pipeline_items_stats", help="Get pipeline items statistics")
    p.add_argument("pipeline_id")

    # --- Labels ---
    p = sub.add_parser("contact_labels", help="List labels on a contact")
    p.add_argument("contact_id")

    p = sub.add_parser("add_contact_labels", help="Add labels to a contact")
    p.add_argument("contact_id")
    p.add_argument("--labels", required=True, help="Comma-separated label names")

    p = sub.add_parser("conversation_labels", help="List labels on a conversation")
    p.add_argument("conversation_id")

    p = sub.add_parser("add_conversation_labels", help="Add labels to a conversation")
    p.add_argument("conversation_id")
    p.add_argument("--labels", required=True, help="Comma-separated label names")

    # --- Parse and dispatch ---
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        # Contacts
        "contacts": cmd_contacts,
        "contact": cmd_contact,
        "search_contacts": cmd_search_contacts,
        "filter_contacts": cmd_filter_contacts,
        "create_contact": cmd_create_contact,
        "update_contact": cmd_update_contact,
        "delete_contact": cmd_delete_contact,
        "contact_conversations": cmd_contact_conversations,
        "contact_notes": cmd_contact_notes,
        "create_contact_note": cmd_create_contact_note,
        "contact_pipelines": cmd_contact_pipelines,
        # Conversations
        "conversations": cmd_conversations,
        "conversation": cmd_conversation,
        "search_conversations": cmd_search_conversations,
        "filter_conversations": cmd_filter_conversations,
        "conversation_meta": cmd_conversation_meta,
        "create_conversation": cmd_create_conversation,
        "assign_conversation": cmd_assign_conversation,
        "toggle_status": cmd_toggle_status,
        "toggle_priority": cmd_toggle_priority,
        "mute_conversation": cmd_mute_conversation,
        "unmute_conversation": cmd_unmute_conversation,
        "mark_unread": cmd_mark_unread,
        "send_transcript": cmd_send_transcript,
        # Messages
        "messages": cmd_messages,
        "create_message": cmd_create_message,
        "update_message": cmd_update_message,
        "delete_message": cmd_delete_message,
        "retry_message": cmd_retry_message,
        # Inboxes
        "inboxes": cmd_inboxes,
        "inbox": cmd_inbox,
        "inbox_agents": cmd_inbox_agents,
        "assignable_agents": cmd_assignable_agents,
        "inbox_templates": cmd_inbox_templates,
        # Pipelines
        "pipelines": cmd_pipelines,
        "pipeline": cmd_pipeline,
        "pipeline_stats": cmd_pipeline_stats,
        "pipeline_stat": cmd_pipeline_stat,
        "pipeline_stages": cmd_pipeline_stages,
        "pipeline_items": cmd_pipeline_items,
        "create_pipeline_item": cmd_create_pipeline_item,
        "move_item": cmd_move_item,
        "bulk_move_items": cmd_bulk_move_items,
        "remove_pipeline_item": cmd_remove_pipeline_item,
        "pipeline_items_stats": cmd_pipeline_items_stats,
        # Labels
        "contact_labels": cmd_contact_labels,
        "add_contact_labels": cmd_add_contact_labels,
        "conversation_labels": cmd_conversation_labels,
        "add_conversation_labels": cmd_add_conversation_labels,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
