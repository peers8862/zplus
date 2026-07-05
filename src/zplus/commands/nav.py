"""gen-nav: regenerate the managed nav region in zensical.toml from the manifest.

Blog-style ordering: any index.md first, then entries newest-first by a
YYYY-MM-DD filename prefix (else a `date:` front-matter field, else filename).
Files starting with "_" are ignored. Types with no files are skipped entirely.
"""
import glob
import os
import re

from .. import manifest as manifest_mod
from ..patch import toml_nav


def date_key(path):
    name = os.path.basename(path)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", name)
    if m:
        return m.group(1)
    with open(path, encoding="utf-8") as f:
        head = f.read(500)
    fm = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", head, re.M)
    return fm.group(1) if fm else name


def ordered_paths(docs_dir, folder):
    files = [p for p in glob.glob(os.path.join(docs_dir, folder, "*.md"))
             if not os.path.basename(p).startswith("_")]
    index = [p for p in files if os.path.basename(p) == "index.md"]
    entries = sorted((p for p in files if os.path.basename(p) != "index.md"),
                     key=date_key, reverse=True)
    return [os.path.relpath(p, docs_dir).replace(os.sep, "/")
            for p in index + entries]


def build_region_body(m, docs_dir):
    """Return the nav lines (one per non-empty type) for the managed region."""
    lines = []
    for t in m.types:
        paths = ordered_paths(docs_dir, t.folder)
        if not paths:
            continue
        items = ", ".join(f'"{p}"' for p in paths)
        lines.append(f'  {{ "{t.label}" = [{items}] }},')
    return "\n".join(lines)


def regenerate(project_dir):
    """Ensure the region exists, then fill it from the manifest. Returns counts."""
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    toml_path = os.path.join(project_dir, "zensical.toml")
    docs_dir = os.path.join(project_dir, "docs")
    with open(toml_path, encoding="utf-8") as f:
        text = f.read()
    text = toml_nav.ensure_nav_region(text, m.project.managed_nav)
    body = build_region_body(m, docs_dir)
    text = toml_nav.splice_region(text, m.project.managed_nav, body)
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(text)
    return sum(1 for t in m.types if ordered_paths(docs_dir, t.folder))


def main(argv=None):
    n = regenerate(os.getcwd())
    print(f"zplus gen-nav: {n} section(s) written to the managed region")
    return 0
