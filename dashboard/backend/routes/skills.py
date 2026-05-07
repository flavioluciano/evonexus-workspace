"""Skills endpoint — list and view skill definitions."""

from flask import Blueprint, jsonify, abort, Response
from routes._helpers import WORKSPACE, safe_read, parse_frontmatter

bp = Blueprint("skills", __name__)

SKILLS_DIR = WORKSPACE / ".claude" / "skills"


@bp.route("/api/skills")
def list_skills():
    if not SKILLS_DIR.is_dir():
        return jsonify([])

    skills = []
    for d in sorted(SKILLS_DIR.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.is_file():
            # Try lowercase
            skill_md = d / "skill.md"
        fm = {}
        if skill_md.is_file():
            content = safe_read(skill_md) or ""
            fm = parse_frontmatter(content)

        name = d.name
        prefix = name.split("-")[0] if "-" in name else name
        has_scripts = any(
            f.suffix in (".py", ".sh", ".js", ".ts")
            for f in d.iterdir() if f.is_file()
        )

        skills.append({
            "name": name,
            "description": fm.get("description", ""),
            "prefix": prefix,
            "has_scripts": has_scripts,
        })

    # Group by prefix
    groups: dict[str, list] = {}
    for s in skills:
        groups.setdefault(s["prefix"], []).append(s)

    return jsonify({"skills": skills, "groups": groups})


@bp.route("/api/skills/<name>")
def get_skill(name):
    skill_dir = SKILLS_DIR / name
    if not skill_dir.is_dir():
        abort(404, description="Skill not found")
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        skill_md = skill_dir / "skill.md"
    if not skill_md.is_file():
        abort(404, description="SKILL.md not found")
    return Response(safe_read(skill_md) or "", mimetype="text/markdown")
