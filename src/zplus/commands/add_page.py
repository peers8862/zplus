"""add-page: rapidly add a plain subpage to a non-templated section.

For fast human/AI build-out: pick a section, give a name, optionally paste the
first block(s) of text (edited later). Writes docs/<folder>/<slug>.md and updates
the nav.
"""
import os

from .. import core, manifest as manifest_mod
from . import nav


def _ask(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        if default is not None:
            return default
        print("  (required)")


def _pick_section(sections):
    print("Section?")
    for i, t in enumerate(sections, 1):
        print(f"  [{i}] {t.label} ({t.name})")
    choice = _ask("  > ")
    try:
        return sections[int(choice) - 1]
    except (ValueError, IndexError):
        pass
    for t in sections:
        if t.name == choice.lower():
            return t
    raise SystemExit(f"error: pick 1–{len(sections)} or a section name")


def _collect_body():
    print("First text (optional) — end with a line containing only '.', or '.' to skip:")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip("\n")


def create(project_dir):
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    sections = [t for t in m.types if not t.templated]
    if not sections:
        raise SystemExit("error: no non-templated section types in this project "
                         "(templated types use `zplus new-entry`)")
    section = _pick_section(sections)
    name = _ask("Page name  > ")
    body = _collect_body()

    folder = os.path.join(project_dir, "docs", section.folder)
    os.makedirs(folder, exist_ok=True)
    path = core.resolve_plain(folder, core.slugify(name))
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {name}\n" + (f"\n{body}\n" if body else ""))
    print(f"✔ wrote {os.path.relpath(path, project_dir)}")
    nav.regenerate(project_dir)
    return path


def main(argv=None):
    create(os.getcwd())
    return 0
