"""Memory endpoint — global and per-agent memory files."""

from flask import Blueprint, jsonify, abort, Response
from routes._helpers import WORKSPACE, safe_read, file_info

bp = Blueprint("memory", __name__)

GLOBAL_MEMORY_DIR = WORKSPACE / "memory"
AGENT_MEMORY_DIR = WORKSPACE / ".claude" / "agent-memory"


@bp.route("/api/memory")
def memory_index():
    # Global memory files
    global_files = []
    if GLOBAL_MEMORY_DIR.is_dir():
        for f in sorted(GLOBAL_MEMORY_DIR.rglob("*")):
            if f.is_file():
                global_files.append(file_info(f, WORKSPACE))

    # Agent memory counts
    agent_counts = {}
    if AGENT_MEMORY_DIR.is_dir():
        for d in sorted(AGENT_MEMORY_DIR.iterdir()):
            if d.is_dir():
                count = sum(1 for f in d.iterdir() if f.is_file())
                agent_counts[d.name] = count

    return jsonify({
        "global_files": global_files,
        "agent_memory_counts": agent_counts,
    })


@bp.route("/api/memory/<path:filepath>")
def get_memory_file(filepath):
    # Try global memory first, then agent-memory
    for base in [GLOBAL_MEMORY_DIR, AGENT_MEMORY_DIR]:
        full = base / filepath
        if full.is_file():
            try:
                full.resolve().relative_to(base.resolve())
            except ValueError:
                abort(403, description="Access denied")
            content = safe_read(full)
            if content is None:
                abort(500, description="Could not read file")
            mime = "text/markdown" if full.suffix.lower() == ".md" else "text/plain"
            return Response(content, mimetype=mime)

    # Also try relative to workspace
    full = WORKSPACE / filepath
    if full.is_file():
        try:
            full.resolve().relative_to(WORKSPACE.resolve())
        except ValueError:
            abort(403)
        content = safe_read(full)
        if content is None:
            abort(500)
        mime = "text/markdown" if full.suffix.lower() == ".md" else "text/plain"
        return Response(content, mimetype=mime)

    abort(404, description="Memory file not found")


@bp.route("/api/memory/agents/<name>")
def list_agent_memories(name):
    mem_dir = AGENT_MEMORY_DIR / name
    if not mem_dir.is_dir():
        return jsonify([])
    files = []
    for f in sorted(mem_dir.iterdir()):
        if f.is_file():
            files.append(file_info(f, mem_dir))
    return jsonify(files)
