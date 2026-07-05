"""apply: idempotent overlay + update. Safe to re-run after `pip install -U`.

Materializes editable files only if absent (never clobbers content), generates a
unique salt, patches zensical.toml's nav region + .gitignore, and removes the
plaintext Actions auto-deploy.
"""
import json
import os
import secrets

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


def _materialize_templates(project_dir):
    dest = os.path.join(project_dir, "templates")
    os.makedirs(dest, exist_ok=True)
    written = []
    for entry in (paths.data_root() / "templates").iterdir():
        if _write_if_absent(os.path.join(dest, entry.name), entry.read_bytes()):
            written.append(entry.name)
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


def apply(project_dir):
    actions = []

    if _write_if_absent(os.path.join(project_dir, "zplus.toml"),
                        paths.read_data("zplus.default.toml")):
        actions.append("created zplus.toml (default manifest)")

    tw = _materialize_templates(project_dir)
    if tw:
        actions.append(f"materialized {len(tw)} template(s)")

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


def main(argv=None):
    for a in apply(os.getcwd()):
        print(f"  • {a}")
    print("✔ zplus apply complete")
    return 0
