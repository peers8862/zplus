"""apply: idempotent overlay + update, profile-aware.

Materializes editable files only if absent (never clobbers content), generates a
unique salt, patches zensical.toml's nav region + .gitignore, and removes the
plaintext Actions auto-deploy. The project's `zplus.toml` is composed from the
chosen profile's ordered types (self-contained); re-runs reuse the recorded profile.
"""
import json
import os
import secrets
import sys

from .. import manifest as manifest_mod, paths
from ..patch import gitignore, toml_nav
from . import nav


def _write_if_absent(target, data_bytes):
    if os.path.exists(target):
        return False
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    with open(target, "wb") as f:
        f.write(data_bytes)
    return True


def _effective_profile(project_dir, requested):
    """Recorded profile from an existing manifest wins; else requested; else default."""
    zt = os.path.join(project_dir, "zplus.toml")
    if os.path.exists(zt):
        recorded = manifest_mod.load(zt).project.profile
        if recorded:
            return recorded
    return requested or "projecthub"


def _ensure_manifest(project_dir, profile):
    target = os.path.join(project_dir, "zplus.toml")
    if os.path.exists(target):
        return False
    if profile not in manifest_mod.available_profiles():
        raise SystemExit(f"error: unknown profile '{profile}'. "
                         f"Available: {', '.join(manifest_mod.available_profiles())}")
    with open(target, "w", encoding="utf-8") as f:
        f.write(manifest_mod.resolve_profile_text(profile))
    return True


def _materialize_templates(project_dir):
    """Copy each project type's library template into templates/ if absent."""
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    library = set(paths.list_types())
    dest = os.path.join(project_dir, "templates")
    os.makedirs(dest, exist_ok=True)
    written = []
    for t in m.types:
        if not t.templated:
            continue  # section types have no template
        if t.name not in library:
            continue  # a project-only type ships its own template
        if _write_if_absent(os.path.join(dest, t.template),
                            paths.read_type_template(t.name)):
            written.append(t.template)
    return written


def _materialize_landings(project_dir):
    """Write docs/<folder>/index.md from each type's `landing` text, if absent."""
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    written = []
    for t in m.types:
        if not t.landing:
            continue
        folder = os.path.join(project_dir, "docs", t.folder)
        os.makedirs(folder, exist_ok=True)
        idx = os.path.join(folder, "index.md")
        if not os.path.exists(idx):
            with open(idx, "w", encoding="utf-8") as f:
                f.write(f"# {t.label}\n\n{t.landing}\n")
            written.append(t.folder)
    return written


def _ensure_salt(project_dir):
    target = os.path.join(project_dir, ".staticrypt.json")
    if os.path.exists(target):
        return False
    with open(target, "w", encoding="utf-8") as f:
        json.dump({"salt": secrets.token_hex(16)}, f)
    return True


def _patch_file(target, transform):
    text = ""
    if os.path.exists(target):
        with open(target, encoding="utf-8") as f:
            text = f.read()
    new = transform(text)
    if new != text:
        with open(target, "w", encoding="utf-8") as f:
            f.write(new)
        return True
    return False


def apply(project_dir, profile=None):
    actions = []
    profile = _effective_profile(project_dir, profile)

    if _ensure_manifest(project_dir, profile):
        actions.append(f"created zplus.toml from profile '{profile}'")

    tw = _materialize_templates(project_dir)
    if tw:
        actions.append(f"materialized {len(tw)} template(s)")
    lw = _materialize_landings(project_dir)
    if lw:
        actions.append(f"created {len(lw)} section landing page(s)")

    if _write_if_absent(os.path.join(project_dir, ".env.example"),
                        paths.read_data("env.example")):
        actions.append("created .env.example")
    if _write_if_absent(os.path.join(project_dir, ".env"),
                        paths.read_data("env.example")):
        actions.append("created .env — set SITE_PASSWORD before building")

    if _ensure_salt(project_dir):
        actions.append("generated a unique .staticrypt.json salt")

    zt = os.path.join(project_dir, "zensical.toml")
    if os.path.exists(zt):
        m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
        if _patch_file(zt, lambda t: toml_nav.ensure_nav_region(t, m.project.managed_nav)):
            actions.append("added the managed nav region to zensical.toml")
        nav.regenerate(project_dir)
        actions.append("regenerated nav from the manifest")
    else:
        actions.append("WARNING: no zensical.toml — run inside a Zensical project")

    if _patch_file(os.path.join(project_dir, ".gitignore"), gitignore.ensure_block):
        actions.append("updated .gitignore (managed block)")

    docs_yml = os.path.join(project_dir, ".github", "workflows", "docs.yml")
    if os.path.exists(docs_yml):
        os.remove(docs_yml)
        actions.append("removed .github/workflows/docs.yml (plaintext auto-deploy)")

    return actions


def _profile_from_argv(argv):
    if "--profile" in argv:
        i = argv.index("--profile")
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    for a in apply(os.getcwd(), profile=_profile_from_argv(argv)):
        print(f"  • {a}")
    print("✔ zplus apply complete")
    return 0
