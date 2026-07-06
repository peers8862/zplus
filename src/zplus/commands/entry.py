"""new-entry: scaffold a template-filled entry, manifest-driven.

Scaffold mode (default) writes the stamped template and opens $EDITOR. Fill mode
(--fill) walks each section at the terminal first, using the manifest's declared
shape (falling back to detecting it from the template body).
"""
import csv
import os
import re
import subprocess
import sys
from datetime import date

from .. import core, manifest as manifest_mod, corpus as corpus_mod

_HINT = {"task": "one per line", "list": "one bullet per line",
         "prose": "type freely", "diagram": "mermaid syntax, one line per row"}


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


def _choose(values, required):
    """Numbered menu; return the chosen value or '' to skip (if not required)."""
    for i, v in enumerate(values, 1):
        print(f"  [{i}] {v}")
    while True:
        raw = input("  > ").strip()
        if not raw:
            if required:
                print("  (required)")
                continue
            return ""
        if raw.isdigit() and 1 <= int(raw) <= len(values):
            return values[int(raw) - 1]
        if raw in values:
            return raw
        print(f"  pick 1–{len(values)} or a listed value")


def _pick_ref(candidates):
    """One ref pick: return a slug, or None on blank. Accepts a number or a slug."""
    raw = input("  > ").strip()
    if not raw:
        return None
    if raw.isdigit() and 1 <= int(raw) <= len(candidates):
        return candidates[int(raw) - 1][0]
    return raw


def _choose_refs(candidates, many, required):
    for i, (slug, title) in enumerate(candidates, 1):
        print(f"  [{i}] {title} ({slug})")
    if not many:
        while True:
            v = _pick_ref(candidates)
            if v is None:
                if required:
                    print("  (required)")
                    continue
                return ""
            return v
    print("  (one per line — blank line when done)")
    chosen = []
    while True:
        v = _pick_ref(candidates)
        if v is None:
            break
        chosen.append(v)
    return chosen


def fill_fields(text, doc_type, project_dir):
    """Prompt each declared field and inject answers into the front matter."""
    if not doc_type.fields:
        return text
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    corpus = corpus_mod.resolve(corpus_mod.read_corpus(project_dir, m), m)
    print("Fields:")
    for f in doc_type.fields:
        req = " (required)" if f.required else ""
        print(f"{f.name}{req}  [{f.type}]")
        if f.type in ("enum", "status"):
            value = _choose(f.values, f.required)
        elif f.type == "ref":
            cands = [(e.slug, e.title) for e in corpus.entries if e.type_name == f.ref]
            value = _choose_refs(cands, f.many, f.required)
        elif f.required:
            value = ask("  > ")
        else:
            value = ask("  > ", default="")
        if value not in (None, "", []):
            text = core.set_front_matter_value(text, f.name, value)
    return text


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
        text = fill_fields(text, doc_type, project_dir)
        text = run_fill(text, doc_type)
    os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    print(f"✔ wrote {os.path.relpath(path, project_dir)}")
    open_editor(path)
    return path


def _load_rows(path):
    if path.endswith((".yaml", ".yml")):
        import yaml
        with open(path, encoding="utf-8") as f:
            return list(yaml.safe_load(f) or [])
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _coerce(field, raw):
    """Shape a raw cell for a field: split on '|'; wrap lone value in a list for many."""
    if raw is None:
        return None
    if isinstance(raw, list):
        return raw
    parts = [p.strip() for p in str(raw).split("|") if p.strip()]
    many = field is not None and (getattr(field, "many", False)
                                  or field.type == "multi-enum")
    if many:
        return parts
    return parts[0] if len(parts) == 1 else parts


def create_from_file(project_dir, type_name, path):
    """Batch-create one entry per row of a CSV/YAML file. Returns created paths."""
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    dt = m.type_by_name(type_name)
    if dt is None:
        raise SystemExit(f"error: no type named '{type_name}'")
    field_by_name = {f.name: f for f in dt.fields}
    folder = os.path.join(project_dir, "docs", dt.folder)
    os.makedirs(folder, exist_ok=True)
    created = []
    for row in _load_rows(path):
        title = (row.get("title") or "").strip()
        if not title:
            continue
        slug = core.slugify(title)
        cols = {k: v for k, v in row.items() if k not in ("title", "date")}
        if dt.templated:
            entry_date = (row.get("date") or date.today().isoformat()).strip()
            fpath, suffix = core.resolve_collision(folder, entry_date, slug)
            with open(os.path.join(project_dir, "templates", dt.template),
                      encoding="utf-8") as f:
                text = core.stamp(f.read(), title, entry_date, suffix)
            for k, v in cols.items():
                val = _coerce(field_by_name.get(k), v)
                if val not in (None, "", []):
                    text = core.set_front_matter_value(text, k, val)
        else:
            fpath = core.resolve_plain(folder, slug)
            fm = [f"title: {title}"]
            for k, v in cols.items():
                val = _coerce(field_by_name.get(k), v)
                if val not in (None, "", []):
                    fm.append(f"{k}: {core.render_fm_value(val)}")
            text = "---\n" + "\n".join(fm) + f"\n---\n# {title}\n"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(text if text.endswith("\n") else text + "\n")
        created.append(os.path.relpath(fpath, project_dir))
    return created


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    create(os.getcwd(), fill=("--fill" in argv))
    return 0
