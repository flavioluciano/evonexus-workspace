"""Agents endpoint — list agents, their config and memory."""

from flask import Blueprint, jsonify, abort, Response
from flask_login import login_required, current_user
from routes._helpers import WORKSPACE, safe_read, parse_frontmatter, file_info
from models import has_agent_access

bp = Blueprint("agents", __name__)

AGENTS_DIR = WORKSPACE / ".claude" / "agents"
AGENT_MEMORY_DIR = WORKSPACE / ".claude" / "agent-memory"


def _count_memory(name: str) -> int:
    mem_dir = AGENT_MEMORY_DIR / name
    if not mem_dir.is_dir():
        return 0
    return sum(1 for f in mem_dir.iterdir() if f.is_file())


@bp.route("/api/agents")
@login_required
def list_agents():
    if not AGENTS_DIR.is_dir():
        return jsonify([])
    agents = []
    role = current_user.role if current_user.is_authenticated else "viewer"
    for f in sorted(AGENTS_DIR.iterdir()):
        if f.suffix.lower() == ".md" and f.is_file():
            content = safe_read(f) or ""
            fm = parse_frontmatter(content)
            name = f.stem
            entry = {
                "name": name,
                "description": fm.get("description", ""),
                "memory_count": _count_memory(name),
                "custom": name.startswith("custom-"),
                "locked": not has_agent_access(role, name),
            }
            if fm.get("color"):
                entry["color"] = fm["color"]
            if fm.get("model"):
                entry["model"] = fm["model"]
            agents.append(entry)
    return jsonify(agents)


@bp.route("/api/agents/<name>")
def get_agent(name):
    path = (AGENTS_DIR / f"{name}.md").resolve()
    try:
        path.relative_to(AGENTS_DIR.resolve())
    except ValueError:
        abort(403, description="Access denied")
    if not path.is_file():
        abort(404, description="Agent not found")
    return Response(safe_read(path) or "", mimetype="text/markdown")


@bp.route("/api/agents/<name>/memory")
def list_agent_memory(name):
    mem_dir = (AGENT_MEMORY_DIR / name).resolve()
    try:
        mem_dir.relative_to(AGENT_MEMORY_DIR.resolve())
    except ValueError:
        abort(403, description="Access denied")
    if not mem_dir.is_dir():
        return jsonify([])
    files = []
    for f in sorted(mem_dir.iterdir()):
        if f.is_file():
            files.append(file_info(f, mem_dir))
    return jsonify(files)


@bp.route("/api/agents/<name>/memory/<file>")
def get_agent_memory_file(name, file):
    path = (AGENT_MEMORY_DIR / name / file).resolve()
    try:
        path.relative_to(AGENT_MEMORY_DIR.resolve())
    except ValueError:
        abort(403, description="Access denied")
    if not path.is_file():
        abort(404, description="Memory file not found")
    content = safe_read(path)
    if content is None:
        abort(500, description="Could not read file")
    mime = "text/markdown" if path.suffix.lower() == ".md" else "text/plain"
    return Response(content, mimetype=mime)
