"""Read all entries' front matter into an in-memory typed graph.

read_corpus() walks docs/<folder>/*.md and keeps each entry's declared field
values. resolve() turns `ref` fields into backlinks on their targets. No I/O
beyond reading; nothing is written (rendering is B3).
"""
import glob
import os
from dataclasses import dataclass, field as dfield

from . import core


@dataclass
class Entry:
    type_name: str
    slug: str
    title: str
    path: str
    fields: dict
    front_matter: dict
    backlinks: dict = dfield(default_factory=dict)


@dataclass
class Corpus:
    entries: list
    by_slug: dict

    def get(self, slug):
        return self.by_slug.get(slug)


def read_corpus(project_dir, m):
    entries = []
    for t in m.types:
        folder = os.path.join(project_dir, "docs", t.folder)
        for path in sorted(glob.glob(os.path.join(folder, "*.md"))):
            if os.path.basename(path) == "index.md":
                continue
            with open(path, encoding="utf-8") as f:
                fm, _ = core.split_front_matter(f.read())
            slug = os.path.splitext(os.path.basename(path))[0]
            declared = {fl.name: fm.get(fl.name)
                        for fl in t.fields if fl.name in fm}
            entries.append(Entry(type_name=t.name, slug=slug,
                                 title=fm.get("title", slug), path=path,
                                 fields=declared, front_matter=fm))
    return Corpus(entries=entries, by_slug={e.slug: e for e in entries})


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def resolve(corpus, m):
    """Populate backlinks from ref fields; returns the same corpus."""
    type_by_name = {t.name: t for t in m.types}
    for e in corpus.entries:
        t = type_by_name.get(e.type_name)
        if not t:
            continue
        for fl in t.fields:
            if fl.type != "ref":
                continue
            for target_slug in _as_list(e.fields.get(fl.name)):
                target = corpus.by_slug.get(target_slug)
                if target is not None:
                    target.backlinks.setdefault((e.type_name, fl.name), []).append(e.slug)
    return corpus
