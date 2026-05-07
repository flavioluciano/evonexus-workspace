#!/usr/bin/env python3
"""
Evolution API client - calls Evolution API REST endpoints directly.
No third-party SDK dependency. Uses only stdlib.

Manages WhatsApp instances, sends messages, queries chats/contacts,
manages groups, and configures webhooks.
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
    """Return (base_url, api_key) or exit with clear error."""
    url = os.environ.get("EVOLUTION_API_URL")
    key = os.environ.get("EVOLUTION_API_KEY")
    errors = []
    if not url:
        errors.append("EVOLUTION_API_URL is not set")
    if not key:
        errors.append("EVOLUTION_API_KEY is not set")
    if errors:
        print(json.dumps({"error": "Missing environment variables", "details": errors}))
        sys.exit(1)
    return url.rstrip("/"), key


def api_request(method, path, body=None, params=None):
    """Make an HTTP request to the Evolution API. Returns parsed JSON."""
    base_url, api_key = get_config()
    url = f"{base_url}/{path.lstrip('/')}"

    if params:
        url += "?" + urllib.parse.urlencode(params)

    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "apikey": api_key,
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            if not raw:
                return {"status": "ok"}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        try:
            error_body = json.loads(e.read())
        except Exception:
            error_body = {"message": str(e)}
        print(json.dumps({"error": f"HTTP {e.code}", "details": error_body}, indent=2))
        sys.exit(1)
    except urllib.error.URLError as e:
        print(json.dumps({"error": "Connection failed", "details": str(e.reason)}))
        sys.exit(1)


def output(data):
    """Print JSON to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Instance Management
# ---------------------------------------------------------------------------

def cmd_instances(args):
    result = api_request("GET", "/instance/fetchInstances")
    output(result)


def cmd_create_instance(args):
    body = {"instanceName": args.name}
    if args.qrcode:
        body["qrcode"] = True
    result = api_request("POST", "/instance/create", body=body)
    output(result)


def cmd_connect(args):
    result = api_request("GET", f"/instance/connect/{args.name}")
    output(result)


def cmd_connection_state(args):
    result = api_request("GET", f"/instance/connectionState/{args.name}")
    output(result)


def cmd_restart(args):
    result = api_request("POST", f"/instance/restart/{args.name}")
    output(result)


def cmd_logout(args):
    result = api_request("DELETE", f"/instance/logout/{args.name}")
    output(result)


def cmd_delete_instance(args):
    result = api_request("DELETE", f"/instance/delete/{args.name}")
    output(result)


def cmd_set_presence(args):
    body = {"presence": args.presence}
    result = api_request("POST", f"/instance/setPresence/{args.name}", body=body)
    output(result)


def cmd_summary(args):
    instances = api_request("GET", "/instance/fetchInstances")
    if not isinstance(instances, list):
        instances = instances.get("data", instances.get("instances", [instances]))

    summary = []
    for inst in instances:
        name = inst.get("instanceName") or inst.get("instance", {}).get("instanceName", "unknown")
        try:
            state = api_request("GET", f"/instance/connectionState/{name}")
        except SystemExit:
            state = {"state": "error"}
        summary.append({
            "instance": name,
            "connectionState": state.get("instance", {}).get("state", state.get("state", "unknown")),
        })
    output(summary)


# ---------------------------------------------------------------------------
# Send Messages
# ---------------------------------------------------------------------------

def _format_number(number):
    """Ensure number has @s.whatsapp.net suffix."""
    if "@" in number:
        return number
    return f"{number}@s.whatsapp.net"


def cmd_send_text(args):
    body = {
        "number": _format_number(args.number),
        "text": args.text,
    }
    result = api_request("POST", f"/message/sendText/{args.instance}", body=body)
    output(result)


def cmd_send_media(args):
    body = {
        "number": _format_number(args.number),
        "mediatype": args.type,
        "media": args.url,
    }
    if args.caption:
        body["caption"] = args.caption
    result = api_request("POST", f"/message/sendMedia/{args.instance}", body=body)
    output(result)


def cmd_send_location(args):
    body = {
        "number": _format_number(args.number),
        "latitude": args.lat,
        "longitude": args.lng,
    }
    if args.name:
        body["name"] = args.name
    result = api_request("POST", f"/message/sendLocation/{args.instance}", body=body)
    output(result)


def cmd_send_contact(args):
    body = {
        "number": _format_number(args.number),
        "contact": [{
            "fullName": args.name,
            "wuid": args.phone,
            "phoneNumber": args.phone,
        }],
    }
    result = api_request("POST", f"/message/sendContact/{args.instance}", body=body)
    output(result)


def cmd_send_buttons(args):
    body = {
        "number": _format_number(args.number),
        "text": args.text,
        "buttons": json.loads(args.buttons),
    }
    result = api_request("POST", f"/message/sendButtons/{args.instance}", body=body)
    output(result)


def cmd_send_list(args):
    body = {
        "number": _format_number(args.number),
        "title": args.title,
        "sections": json.loads(args.sections),
    }
    result = api_request("POST", f"/message/sendList/{args.instance}", body=body)
    output(result)


def cmd_send_poll(args):
    body = {
        "number": _format_number(args.number),
        "name": args.name,
        "values": [v.strip() for v in args.values.split(",")],
    }
    result = api_request("POST", f"/message/sendPoll/{args.instance}", body=body)
    output(result)


def cmd_send_reaction(args):
    body = {
        "key": json.loads(args.key),
        "reaction": args.reaction,
    }
    result = api_request("POST", f"/message/sendReaction/{args.instance}", body=body)
    output(result)


def cmd_send_template(args):
    body = {
        "number": _format_number(args.number),
        "text": args.text,
    }
    result = api_request("POST", f"/message/sendTemplate/{args.instance}", body=body)
    output(result)


# ---------------------------------------------------------------------------
# Chat Operations
# ---------------------------------------------------------------------------

def cmd_find_chats(args):
    body = {}
    if args.where:
        body["where"] = json.loads(args.where)
    if args.take:
        body["take"] = args.take
    result = api_request("POST", f"/chat/findChats/{args.instance}", body=body)
    output(result)


def cmd_find_messages(args):
    body = {}
    if args.where:
        body["where"] = json.loads(args.where)
    if args.take:
        body["take"] = args.take
    result = api_request("POST", f"/chat/findMessages/{args.instance}", body=body)
    output(result)


def cmd_find_contacts(args):
    body = {}
    if args.where:
        body["where"] = json.loads(args.where)
    result = api_request("POST", f"/chat/findContacts/{args.instance}", body=body)
    output(result)


def cmd_mark_read(args):
    body = {"readMessages": json.loads(args.messages)}
    result = api_request("POST", f"/chat/markMessageAsRead/{args.instance}", body=body)
    output(result)


def cmd_archive_chat(args):
    body = {
        "lastMessage": {"key": {"remoteJid": _format_number(args.number)}},
        "archive": args.archive.lower() == "true",
    }
    result = api_request("POST", f"/chat/archiveChat/{args.instance}", body=body)
    output(result)


def cmd_check_numbers(args):
    numbers = [n.strip() for n in args.numbers.split(",")]
    body = {"numbers": numbers}
    result = api_request("POST", f"/chat/whatsappNumbers/{args.instance}", body=body)
    output(result)


def cmd_update_profile_name(args):
    body = {"name": args.name}
    result = api_request("POST", f"/chat/updateProfileName/{args.instance}", body=body)
    output(result)


def cmd_update_profile_status(args):
    body = {"status": args.status}
    result = api_request("POST", f"/chat/updateProfileStatus/{args.instance}", body=body)
    output(result)


# ---------------------------------------------------------------------------
# Group Operations
# ---------------------------------------------------------------------------

def cmd_create_group(args):
    participants = [p.strip() for p in args.participants.split(",")]
    body = {
        "subject": args.subject,
        "participants": participants,
    }
    result = api_request("POST", f"/group/create/{args.instance}", body=body)
    output(result)


def cmd_group_info(args):
    result = api_request("GET", f"/group/findGroupInfos/{args.instance}", params={"groupJid": args.jid})
    output(result)


def cmd_group_participants(args):
    result = api_request("GET", f"/group/participants/{args.instance}", params={"groupJid": args.jid})
    output(result)


def cmd_update_participant(args):
    participants = [p.strip() for p in args.participants.split(",")]
    body = {
        "groupJid": args.jid,
        "action": args.action,
        "participants": participants,
    }
    result = api_request("POST", f"/group/updateParticipant/{args.instance}", body=body)
    output(result)


# ---------------------------------------------------------------------------
# Webhook Management
# ---------------------------------------------------------------------------

def cmd_webhooks(args):
    result = api_request("GET", f"/webhook/find/{args.instance}")
    output(result)


def cmd_set_webhook(args):
    events = [e.strip() for e in args.events.split(",")]
    body = {
        "url": args.url,
        "events": events,
        "enabled": True,
    }
    result = api_request("POST", f"/webhook/set/{args.instance}", body=body)
    output(result)


def cmd_delete_webhook(args):
    result = api_request("DELETE", f"/webhook/delete/{args.instance}")
    output(result)


# ---------------------------------------------------------------------------
# CLI Argument Parser
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Evolution API client — manage WhatsApp instances, messages, chats, groups, and webhooks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  Instance:   instances, create_instance, connect, connection_state, restart,
              logout, delete_instance, set_presence, summary
  Messages:   send_text, send_media, send_location, send_contact, send_buttons,
              send_list, send_poll, send_reaction, send_template
  Chats:      find_chats, find_messages, mark_read, archive_chat,
              update_profile_name, update_profile_status
  Contacts:   find_contacts, check_numbers
  Groups:     create_group, group_info, group_participants, update_participant
  Webhooks:   webhooks, set_webhook, delete_webhook

Examples:
  %(prog)s instances
  %(prog)s send_text my-instance 5511999999999 "Hello!"
  %(prog)s summary
""",
    )
    sub = parser.add_subparsers(dest="command")

    # --- Instance Management ---
    sub.add_parser("instances", help="List all instances")

    p = sub.add_parser("create_instance", help="Create a new instance")
    p.add_argument("name", help="Instance name")
    p.add_argument("--qrcode", action="store_true", help="Return QR code on creation")

    p = sub.add_parser("connect", help="Connect instance (returns QR code)")
    p.add_argument("name", help="Instance name")

    p = sub.add_parser("connection_state", help="Get connection state")
    p.add_argument("name", help="Instance name")

    p = sub.add_parser("restart", help="Restart an instance")
    p.add_argument("name", help="Instance name")

    p = sub.add_parser("logout", help="Logout and disconnect")
    p.add_argument("name", help="Instance name")

    p = sub.add_parser("delete_instance", help="Delete an instance")
    p.add_argument("name", help="Instance name")

    p = sub.add_parser("set_presence", help="Set presence state")
    p.add_argument("name", help="Instance name")
    p.add_argument("--presence", required=True, choices=["available", "unavailable", "composing", "recording"])

    sub.add_parser("summary", help="Overview of all instances with connection states")

    # --- Send Messages ---
    p = sub.add_parser("send_text", help="Send text message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number (e.g. 5511999999999)")
    p.add_argument("text", help="Message text")

    p = sub.add_parser("send_media", help="Send media message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--type", required=True, choices=["image", "video", "audio", "document"], help="Media type")
    p.add_argument("--url", required=True, help="Media URL")
    p.add_argument("--caption", help="Optional caption")

    p = sub.add_parser("send_location", help="Send location")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--lat", required=True, type=float, help="Latitude")
    p.add_argument("--lng", required=True, type=float, help="Longitude")
    p.add_argument("--name", help="Location name")

    p = sub.add_parser("send_contact", help="Send contact card")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--name", required=True, help="Contact name")
    p.add_argument("--phone", required=True, help="Contact phone number")

    p = sub.add_parser("send_buttons", help="Send buttons message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--text", required=True, help="Message text")
    p.add_argument("--buttons", required=True, help="Buttons JSON array")

    p = sub.add_parser("send_list", help="Send list message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--title", required=True, help="List title")
    p.add_argument("--sections", required=True, help="Sections JSON array")

    p = sub.add_parser("send_poll", help="Send poll")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--name", required=True, help="Poll question")
    p.add_argument("--values", required=True, help="Comma-separated poll options")

    p = sub.add_parser("send_reaction", help="React to a message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--key", required=True, help="Message key JSON")
    p.add_argument("--reaction", required=True, help="Emoji reaction")

    p = sub.add_parser("send_template", help="Send template message")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("text", help="Template text")

    # --- Chat Operations ---
    p = sub.add_parser("find_chats", help="Search/filter chats")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--where", help="Filter JSON")
    p.add_argument("--take", type=int, help="Limit results")

    p = sub.add_parser("find_messages", help="Search/filter messages")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--where", help="Filter JSON")
    p.add_argument("--take", type=int, help="Limit results")

    p = sub.add_parser("mark_read", help="Mark messages as read")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--messages", required=True, help="Messages JSON array")

    p = sub.add_parser("archive_chat", help="Archive/unarchive a chat")
    p.add_argument("instance", help="Instance name")
    p.add_argument("number", help="Phone number")
    p.add_argument("--archive", required=True, help="true or false")

    p = sub.add_parser("update_profile_name", help="Update WhatsApp profile name")
    p.add_argument("instance", help="Instance name")
    p.add_argument("name", help="New profile name")

    p = sub.add_parser("update_profile_status", help="Update WhatsApp status text")
    p.add_argument("instance", help="Instance name")
    p.add_argument("status", help="New status text")

    # --- Contacts ---
    p = sub.add_parser("find_contacts", help="Search/filter contacts")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--where", help="Filter JSON")

    p = sub.add_parser("check_numbers", help="Check if numbers are on WhatsApp")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--numbers", required=True, help="Comma-separated phone numbers")

    # --- Group Operations ---
    p = sub.add_parser("create_group", help="Create a group")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--subject", required=True, help="Group name")
    p.add_argument("--participants", required=True, help="Comma-separated phone numbers")

    p = sub.add_parser("group_info", help="Get group info")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--jid", required=True, help="Group JID")

    p = sub.add_parser("group_participants", help="List group participants")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--jid", required=True, help="Group JID")

    p = sub.add_parser("update_participant", help="Add/remove/promote/demote participant")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--jid", required=True, help="Group JID")
    p.add_argument("--action", required=True, choices=["add", "remove", "promote", "demote"])
    p.add_argument("--participants", required=True, help="Comma-separated phone numbers")

    # --- Webhook Management ---
    p = sub.add_parser("webhooks", help="List webhooks for instance")
    p.add_argument("instance", help="Instance name")

    p = sub.add_parser("set_webhook", help="Set webhook")
    p.add_argument("instance", help="Instance name")
    p.add_argument("--url", required=True, help="Webhook URL")
    p.add_argument("--events", required=True, help="Comma-separated event names")

    p = sub.add_parser("delete_webhook", help="Delete webhook")
    p.add_argument("instance", help="Instance name")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        # Instance
        "instances": cmd_instances,
        "create_instance": cmd_create_instance,
        "connect": cmd_connect,
        "connection_state": cmd_connection_state,
        "restart": cmd_restart,
        "logout": cmd_logout,
        "delete_instance": cmd_delete_instance,
        "set_presence": cmd_set_presence,
        "summary": cmd_summary,
        # Messages
        "send_text": cmd_send_text,
        "send_media": cmd_send_media,
        "send_location": cmd_send_location,
        "send_contact": cmd_send_contact,
        "send_buttons": cmd_send_buttons,
        "send_list": cmd_send_list,
        "send_poll": cmd_send_poll,
        "send_reaction": cmd_send_reaction,
        "send_template": cmd_send_template,
        # Chats
        "find_chats": cmd_find_chats,
        "find_messages": cmd_find_messages,
        "mark_read": cmd_mark_read,
        "archive_chat": cmd_archive_chat,
        "update_profile_name": cmd_update_profile_name,
        "update_profile_status": cmd_update_profile_status,
        # Contacts
        "find_contacts": cmd_find_contacts,
        "check_numbers": cmd_check_numbers,
        # Groups
        "create_group": cmd_create_group,
        "group_info": cmd_group_info,
        "group_participants": cmd_group_participants,
        "update_participant": cmd_update_participant,
        # Webhooks
        "webhooks": cmd_webhooks,
        "set_webhook": cmd_set_webhook,
        "delete_webhook": cmd_delete_webhook,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args)
    else:
        print(json.dumps({"error": f"Unknown command: {args.command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
