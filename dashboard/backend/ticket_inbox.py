"""Ticket inbox helpers for heartbeat integration (Feature 1.3 — F1.1 stub).

This module provides the query functions that heartbeat_runner.py should import
after Feature 1.1 (Heartbeats) is merged with Feature 1.3 (Tickets).

Integration note (requires F1.1 merged):
    In heartbeat_runner.py, Step 3 (query inbox), replace the stub with:

        from ticket_inbox import pick_top_ticket_for_agent, get_inbox_for_agent
        inbox = get_inbox_for_agent(agent_slug)
        top = inbox[0] if inbox else None

    Step 5 (checkout): call POST /api/tickets/{id}/checkout
    Step 9 (release): call POST /api/tickets/{id}/release
    (or use checkout_ticket / release_ticket functions directly)
"""

from __future__ import annotations

from typing import Optional


def get_inbox_for_agent(agent_slug: str, limit: int = 10) -> list[dict]:
    """Return tickets in agent's inbox, ordered by priority then age.

    Requires app context (Flask SQLAlchemy).
    Returns empty list if no tickets found.
    """
    try:
        from models import db
        result = db.session.execute(
            db.text("""
                SELECT id, title, description, priority, priority_rank, status,
                       created_at, goal_id, project_id, locked_at, locked_by
                FROM tickets
                WHERE assignee_agent = :agent
                  AND status IN ('open', 'in_progress')
                  AND locked_at IS NULL
                ORDER BY priority_rank DESC, created_at ASC
                LIMIT :limit
            """),
            {"agent": agent_slug, "limit": limit},
        )
        return [dict(row._mapping) for row in result]
    except Exception as exc:
        print(f"[ticket_inbox] WARNING: get_inbox_for_agent failed: {exc}", flush=True)
        return []


def pick_top_ticket_for_agent(agent_slug: str) -> Optional[dict]:
    """Get highest-priority unlocked ticket for agent. Returns None if inbox is empty."""
    inbox = get_inbox_for_agent(agent_slug, limit=1)
    return inbox[0] if inbox else None


def checkout_ticket(ticket_id: str, agent_slug: str, lock_timeout_seconds: int = 1800) -> bool:
    """Atomically checkout a ticket for an agent.

    Returns True if checkout succeeded, False if ticket was already locked.
    Raises on unexpected errors.
    """
    try:
        from models import db, TicketActivity
        import uuid
        import json
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        result = db.session.execute(
            db.text(
                "UPDATE tickets SET locked_at = :now, locked_by = :agent, "
                "lock_timeout_seconds = :timeout, updated_at = :now "
                "WHERE id = :id AND locked_at IS NULL"
            ),
            {"id": ticket_id, "agent": agent_slug, "timeout": lock_timeout_seconds, "now": now},
        )
        if result.rowcount == 0:
            db.session.rollback()
            return False

        activity = TicketActivity(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            actor=agent_slug,
            action="checkout",
            payload=json.dumps({"lock_timeout_seconds": lock_timeout_seconds}),
            created_at=now,
        )
        db.session.add(activity)
        db.session.commit()
        return True
    except Exception as exc:
        db.session.rollback()
        print(f"[ticket_inbox] WARNING: checkout_ticket failed: {exc}", flush=True)
        raise


def release_ticket(ticket_id: str, agent_slug: str, keep_if_in_progress: bool = False) -> bool:
    """Release a ticket lock.

    If keep_if_in_progress=True and ticket.status == 'in_progress', lock is kept
    (agent signals it will continue on the next heartbeat run).

    Returns True if lock was released, False if lock was kept.
    """
    try:
        from models import db, Ticket, TicketActivity
        import uuid
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return False

        if keep_if_in_progress and ticket.status == "in_progress":
            return False  # keep lock

        if ticket.locked_by != agent_slug:
            print(f"[ticket_inbox] WARNING: release_ticket: ticket {ticket_id} locked by {ticket.locked_by}, not {agent_slug}", flush=True)
            return False

        ticket.locked_at = None
        ticket.locked_by = None
        ticket.updated_at = now

        activity = TicketActivity(
            id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            actor=agent_slug,
            action="release",
            payload="{}",
            created_at=now,
        )
        db.session.add(activity)
        db.session.commit()
        return True
    except Exception as exc:
        db.session.rollback()
        print(f"[ticket_inbox] WARNING: release_ticket failed: {exc}", flush=True)
        raise
