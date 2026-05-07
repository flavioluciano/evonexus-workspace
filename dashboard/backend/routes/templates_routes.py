"""Templates endpoint — list and serve HTML/MD templates (core + custom)."""

from flask import Blueprint, jsonify, abort, Response
from routes._helpers import WORKSPACE, safe_read, file_info

bp = Blueprint("templates", __name__)

TEMPLATES_BASE = WORKSPACE / ".claude" / "templates"


@bp.route("/api/templates")
def list_templates():
    templates = []

    # Core HTML templates
    html_dir = TEMPLATES_BASE / "html"
    if html_dir.is_dir():
        for f in sorted(html_dir.iterdir()):
            if f.is_file() and f.suffix.lower() == ".html":
                info = file_info(f, WORKSPACE)
                info["type"] = "html"
                info["custom"] = False
                templates.append(info)

    # Custom HTML templates
    html_custom = TEMPLATES_BASE / "html" / "custom"
    if html_custom.is_dir():
        for f in sorted(html_custom.iterdir()):
            if f.is_file() and f.suffix.lower() == ".html":
                info = file_info(f, WORKSPACE)
                info["type"] = "html"
                info["custom"] = True
                templates.append(info)

    # Core MD templates
    if TEMPLATES_BASE.is_dir():
        for f in sorted(TEMPLATES_BASE.iterdir()):
            if f.is_file() and f.suffix.lower() == ".md":
                info = file_info(f, WORKSPACE)
                info["type"] = "markdown"
                info["custom"] = False
                templates.append(info)

    # Custom MD templates
    md_custom = TEMPLATES_BASE / "custom"
    if md_custom.is_dir():
        for f in sorted(md_custom.iterdir()):
            if f.is_file() and f.suffix.lower() == ".md":
                info = file_info(f, WORKSPACE)
                info["type"] = "markdown"
                info["custom"] = True
                templates.append(info)

    return jsonify(templates)


@bp.route("/api/templates/<path:name>")
def get_template(name):
    # Search in all template directories
    search_dirs = [
        TEMPLATES_BASE / "html",
        TEMPLATES_BASE / "html" / "custom",
        TEMPLATES_BASE,
        TEMPLATES_BASE / "custom",
    ]

    for d in search_dirs:
        path = d / name
        if path.is_file():
            mime = "text/html" if path.suffix.lower() == ".html" else "text/markdown"
            return Response(safe_read(path) or "", mimetype=mime)

    abort(404, description="Template not found")
