"""new-entry: scaffold a template-filled entry, manifest-driven.

Scaffold mode (default) writes the stamped template and opens $EDITOR. Fill mode
(--fill) walks each section at the terminal first, using the manifest's declared
shape (falling back to detecting it from the template body).
"""
import os
import re
import subprocess
import sys
from datetime import date

from .. import core, manifest as manifest_mod

_HINT = {"task": "one per line", "list": "one bullet per line", "prose": "type freely"}


def ask(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        if default is not None:
            return default
        print("  (required)")


def collect_lines(header):
    """One entry per line; a blank line finishes. Returns list[str]."""
    print(header)
    lines = []
    while True:
        val = input("  > ").rstrip("\n")
        if val == "":
            return lines
        lines.append(val)


def open_editor(path):
    for cmd in (["subl", path], [os.environ.get("EDITOR", ""), path], ["nano", path]):
        if not cmd[0]:
            continue
        try:
            subprocess.call(cmd)
            return True
        except FileNotFoundError:
            continue
    print(f"(no editor found — file written to {path})")
    return False


def _shape_and_prompt(doc_type, heading, body):
    for s in doc_type.sections:
        if s.heading == heading:
            return s.shape, s.prompt
    return core.section_shape(body), ""


def run_fill(text, doc_type):
    """Prompt the user through front-matter lists and each section, in place."""
    if re.search(r"(?m)^attendees:", text):
        names = collect_lines("Attendees (one name per line — empty line when done)")
        if names:
            text = re.sub(r"(?m)^attendees:.*$", core.render_attendees(names), text, count=1)
    if re.search(r"(?m)^tags:", text):
        tags = collect_lines("Tags (one per line — empty line when done)")
        if tags:
            text = re.sub(r"(?m)^tags:\n(?:\s*-.*\n?)*", core.render_tags(tags) + "\n", text, count=1)

    parts = re.split(r"(?m)^(## .+)$", text)
    if len(parts) == 1:  # no ## sections (e.g. timeline): one body prompt under the H1
        lines = collect_lines("Body (type freely — empty line when done)")
        if lines:
            body = "\n".join(lines)
            text = re.sub(r"(?m)^(# .+)$",
                          lambda m: m.group(1) + "\n\n" + body, text, count=1)
        return text

    rebuilt = parts[0]
    for i in range(1, len(parts), 2):
        heading_line = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else "\n"
        heading = heading_line[3:].strip()
        shape, prompt = _shape_and_prompt(doc_type, heading, body.strip("\n"))
        header = f"{heading_line}  ({_HINT[shape]} — empty line when done)"
        if prompt:
            header += f"\n  {prompt}"
        lines = collect_lines(header)
        if lines:
            rebuilt += heading_line + "\n\n" + core.render_body(lines, shape) + "\n\n"
        else:
            rebuilt += heading_line + body
    return rebuilt


def _pick_type(types):
    print("Section?")
    for i, t in enumerate(types, 1):
        print(f"  [{i}] {t.label} ({t.name})")
    choice = ask("  > ")
    try:
        return types[int(choice) - 1]
    except (ValueError, IndexError):
        pass
    for t in types:
        if t.name == choice.lower():
            return t
    raise SystemExit(f"error: pick 1–{len(types)} or a type name")


def create(project_dir, fill=False):
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    types = [t for t in m.types if t.templated]
    if not types:
        raise SystemExit("error: no templated doc types in zplus.toml "
                         "(section types use `zplus add-page`)")
    doc_type = _pick_type(types)
    title = ask("Title  > ")
    today = date.today().isoformat()
    entry_date = ask(f"Date [{today}]  > ", default=today)

    tpl_path = os.path.join(project_dir, "templates", doc_type.template)
    with open(tpl_path, encoding="utf-8") as f:
        text = f.read()
    folder = os.path.join(project_dir, "docs", doc_type.folder)
    path, suffix = core.resolve_collision(folder, entry_date, core.slugify(title))
    text = core.stamp(text, title, entry_date, suffix)
    if fill:
        text = run_fill(text, doc_type)
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    print(f"✔ wrote {os.path.relpath(path, project_dir)}")
    open_editor(path)
    return path


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    create(os.getcwd(), fill=("--fill" in argv))
    return 0
