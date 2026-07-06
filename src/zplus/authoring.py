"""Serialize + write types and profiles into the user library (SP2 authoring)."""
import os

from . import paths
from .manifest import Section


def _tstr(s):
    """A TOML basic string with the two escapes that matter here."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _mlstr(s):
    """A TOML string for landing text (single line basic; multi-line literal)."""
    body = s.rstrip("\n")
    if "\n" not in body:
        return _tstr(body)
    if "'''" not in body:
        return "'''\n" + body + "\n'''"
    return '"""\n' + body.replace("\\", "\\\\").replace('"""', '\\"""') + '\n"""'


def type_fragment(name, label, folder, template, sections, templated=True, landing=""):
    """A concatenatable `[[type]]` TOML fragment (same shape the library stores)."""
    lines = ["[[type]]",
             f"name = {_tstr(name)}",
             f"label = {_tstr(label)}",
             f"folder = {_tstr(folder)}"]
    if templated:
        lines.append(f"template = {_tstr(template)}")
    else:
        lines.append("templated = false")
    if landing:
        lines.append("landing = " + _mlstr(landing))
    for s in sections:
        lines.append("  [[type.section]]")
        lines.append(f"  heading = {_tstr(s.heading)}")
        lines.append(f"  shape = {_tstr(s.shape)}")
        if s.prompt:
            lines.append(f"  prompt = {_tstr(s.prompt)}")
    return "\n".join(lines) + "\n"


def type_template(name, sections):
    """Generate a template.md from a type's sections."""
    word = name[:1].upper() + name[1:]
    out = ["---", "date: YYYY-MM-DD", f"title: {word} title", "---",
           f"# {word} title — YYYY-MM-DD", ""]
    if not sections:
        out += ["What happened, and why it matters.", ""]
    for s in sections:
        out.append(f"## {s.heading}")
        out.append("- [ ]" if s.shape == "task"
                   else "-" if s.shape == "list"
                   else (s.prompt or "…"))
        out.append("")
    return "\n".join(out).rstrip("\n") + "\n"


def profile_text(label, types):
    items = ", ".join(_tstr(t) for t in types)
    return f"label = {_tstr(label)}\ntypes = [{items}]\n"


def write_type(name, label, folder, sections, template=None, templated=True, landing=""):
    """Write a type into the user library. Section types (templated=False) get no
    template.md. Returns the type's dir."""
    template = template or (f"{name}.md" if templated else "")
    d = paths.user_type_dir(name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "type.toml"), "w", encoding="utf-8") as f:
        f.write(type_fragment(name, label, folder, template, sections, templated, landing))
    if templated:
        with open(os.path.join(d, "template.md"), "w", encoding="utf-8") as f:
            f.write(type_template(name, sections))
    return d


def write_profile(name, label, types):
    """Write a profile (ordered type list) into the user library. Returns its path."""
    path = paths.user_profile_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(profile_text(label, types))
    return path


def section(heading, shape="prose", prompt=""):
    return Section(heading=heading, shape=shape, prompt=prompt)
