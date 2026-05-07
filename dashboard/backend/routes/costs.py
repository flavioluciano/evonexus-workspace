"""Costs endpoint — aggregated and daily cost breakdowns."""

import json
from datetime import date, timedelta
from flask import Blueprint, jsonify, request
from routes._helpers import WORKSPACE, safe_read
from models import db, Heartbeat, HeartbeatRun
from sqlalchemy import func

bp = Blueprint("costs", __name__)

METRICS_PATH = WORKSPACE / "ADWs" / "logs" / "metrics.json"
LOGS_DIR = WORKSPACE / "ADWs" / "logs"


@bp.route("/api/costs")
def costs_summary():
    content = safe_read(METRICS_PATH)
    if not content:
        return jsonify({"total_cost": 0, "by_routine": [], "by_agent": [], "today": 0, "week": 0, "month_estimate": 0})

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return jsonify({"total_cost": 0, "by_routine": [], "by_agent": [], "today": 0, "week": 0, "month_estimate": 0})

    total = 0.0
    by_routine = []
    agent_costs = {}

    if isinstance(data, dict):
        for name, val in data.items():
            if isinstance(val, dict):
                cost = float(val.get("total_cost_usd", 0) or 0)
                tokens = int(val.get("total_input_tokens", 0) or 0) + int(val.get("total_output_tokens", 0) or 0)
                runs = int(val.get("runs", 0) or 0)
                avg_cost = float(val.get("avg_cost_usd", 0) or 0)
                agent = val.get("agent", "unknown")

                total += cost
                by_routine.append({
                    "name": name,
                    "cost": round(cost, 5),
                    "total_cost": round(cost, 5),
                    "avg_cost": round(avg_cost, 5),
                    "tokens": tokens,
                    "runs": runs,
                    "agent": agent,
                })
                agent_costs[agent] = agent_costs.get(agent, 0.0) + cost

    by_agent = [{"agent": a, "cost": round(c, 4)} for a, c in sorted(agent_costs.items(), key=lambda x: x[1], reverse=True)]

    # Aggregate heartbeat costs from DB
    hb_rows = (
        db.session.query(
            HeartbeatRun.heartbeat_id,
            func.count(HeartbeatRun.run_id).label("runs"),
            func.sum(func.coalesce(HeartbeatRun.cost_usd, 0)).label("total_cost_usd"),
            func.avg(func.coalesce(HeartbeatRun.cost_usd, 0)).label("avg_cost_usd"),
        )
        .group_by(HeartbeatRun.heartbeat_id)
        .all()
    )

    # Build a lookup for heartbeat agent names
    hb_agents = {h.id: h.agent for h in db.session.query(Heartbeat.id, Heartbeat.agent).all()}

    hb_total = 0.0
    hb_runs_total = 0
    by_heartbeat = []
    for row in hb_rows:
        hb_cost = float(row.total_cost_usd or 0)
        hb_avg = float(row.avg_cost_usd or 0)
        hb_count = int(row.runs or 0)
        hb_total += hb_cost
        hb_runs_total += hb_count
        by_heartbeat.append({
            "name": row.heartbeat_id,
            "agent": hb_agents.get(row.heartbeat_id, "unknown"),
            "runs": hb_count,
            "total_cost": round(hb_cost, 5),
            "avg_cost": round(hb_avg, 5),
        })

    # Calculate today and week from JSONL logs (routines)
    today_cost = 0.0
    week_cost = 0.0
    daily_costs = {}
    today_str = date.today().isoformat()
    week_start = (date.today() - timedelta(days=7)).isoformat()

    if LOGS_DIR.is_dir():
        for f in LOGS_DIR.iterdir():
            if f.suffix != ".jsonl":
                continue
            text = safe_read(f)
            if not text:
                continue
            for line in text.strip().splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("timestamp", "")[:10]
                cost_val = float(entry.get("cost_usd", 0) or 0)
                if ts:
                    daily_costs[ts] = daily_costs.get(ts, 0.0) + cost_val
                if ts == today_str:
                    today_cost += cost_val
                if ts >= week_start:
                    week_cost += cost_val

    # Add heartbeat daily costs from DB
    hb_daily_rows = (
        db.session.query(
            func.substr(HeartbeatRun.started_at, 1, 10).label("day"),
            func.sum(func.coalesce(HeartbeatRun.cost_usd, 0)).label("cost"),
        )
        .group_by("day")
        .all()
    )
    for row in hb_daily_rows:
        day = row.day
        cost_val = float(row.cost or 0)
        if day:
            daily_costs[day] = daily_costs.get(day, 0.0) + cost_val
        if day == today_str:
            today_cost += cost_val
        if day and day >= week_start:
            week_cost += cost_val

    daily = [{"date": k, "cost": round(v, 4)} for k, v in sorted(daily_costs.items())]

    grand_total = total + hb_total
    routine_runs_total = sum(r["runs"] for r in by_routine)

    return jsonify({
        "total_cost": round(grand_total, 4),
        "routines_total_cost": round(total, 4),
        "heartbeats_total_cost": round(hb_total, 4),
        "today": round(today_cost, 4),
        "week": round(week_cost, 4),
        "month_estimate": round(grand_total, 4),
        "total_runs": routine_runs_total + hb_runs_total,
        "daily": daily,
        "by_routine": by_routine,
        "by_heartbeat": by_heartbeat,
        "by_agent": by_agent,
    })


@bp.route("/api/costs/daily")
def costs_daily():
    from_date = request.args.get("from", (date.today() - timedelta(days=7)).isoformat())
    to_date = request.args.get("to", date.today().isoformat())

    routines_daily = {}
    if LOGS_DIR.is_dir():
        for f in sorted(LOGS_DIR.iterdir()):
            if f.suffix != ".jsonl":
                continue
            text = safe_read(f)
            if not text:
                continue
            for line in text.strip().splitlines():
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = entry.get("timestamp", "")
                if not ts:
                    continue
                day = ts[:10]
                if from_date <= day <= to_date:
                    cost = float(entry.get("cost_usd", entry.get("cost", 0)) or 0)
                    routines_daily[day] = routines_daily.get(day, 0.0) + cost

    # Add heartbeat daily costs from DB
    heartbeats_daily = {}
    hb_rows = (
        db.session.query(
            func.substr(HeartbeatRun.started_at, 1, 10).label("day"),
            func.sum(func.coalesce(HeartbeatRun.cost_usd, 0)).label("cost"),
        )
        .filter(
            func.substr(HeartbeatRun.started_at, 1, 10) >= from_date,
            func.substr(HeartbeatRun.started_at, 1, 10) <= to_date,
        )
        .group_by("day")
        .all()
    )
    for row in hb_rows:
        if row.day:
            heartbeats_daily[row.day] = float(row.cost or 0)

    # Merge all days
    all_days = set(routines_daily.keys()) | set(heartbeats_daily.keys())
    combined = []
    for day in sorted(all_days):
        r_cost = routines_daily.get(day, 0.0)
        h_cost = heartbeats_daily.get(day, 0.0)
        combined.append({
            "date": day,
            "cost": round(r_cost + h_cost, 4),
            "routines_cost": round(r_cost, 4),
            "heartbeats_cost": round(h_cost, 4),
        })

    return jsonify(combined)
