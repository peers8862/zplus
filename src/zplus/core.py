"""Pure, side-effect-free helpers shared by zplus commands.

Everything here is unit-tested and free of I/O so the logic can be reasoned about
and tested without touching a real project tree.
"""
import os
import re

import yaml

# Word-form suffixes for same-day/same-title filename collisions.
ORDINALS = {2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX",
            7: "SEVEN", 8: "EIGHT", 9: "NINE", 10: "TEN"}


def split_front_matter(text):
    """Split a markdown doc into (front_matter_dict, body).

    Recognizes a leading YAML block fenced by lines of exactly '---'. Returns
    ({}, text) when there is no valid front matter.
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.split("\n")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            data = yaml.safe_load("\n".join(lines[1:i])) or {}
            if not isinstance(data, dict):
                data = {}
            return data, "\n".join(lines[i + 1:])
    return {}, text


def slugify(title):
    """Lowercase, collapse non-alphanumerics to single hyphens, trim ends."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


def resolve_collision(folder, date, slug):
    """Return (path, suffix_word|None) for the first free `<date>-<slug>[-WORD].md`.

    First file is unsuffixed; later same-name files get -TWO, -THREE … -TEN.
    An 11th collision is an error rather than a silent fallback.
    """
    base = f"{date}-{slug}"
    first = os.path.join(folder, base + ".md")
    if not os.path.exists(first):
        return first, None
    for n in range(2, 11):
        word = ORDINALS[n]
        cand = os.path.join(folder, f"{base}-{word}.md")
        if not os.path.exists(cand):
            return cand, word
    raise SystemExit(f"error: more than ten '{base}' entries — check {folder}")


def resolve_plain(folder, slug):
    """First free `<slug>.md`, then `<slug>-2.md`, … (non-dated section pages)."""
    first = os.path.join(folder, slug + ".md")
    if not os.path.exists(first):
        return first
    n = 2
    while os.path.exists(os.path.join(folder, f"{slug}-{n}.md")):
        n += 1
    return os.path.join(folder, f"{slug}-{n}.md")


def stamp(template_text, title, date, suffix_word=None):
    """Substitute date/title into a template's front matter and H1.

    The H1 gets a `(WORD)` suffix on collisions so generated nav labels stay
    distinct; the front-matter `title:` stays the plain title.
    """
    h1 = title if not suffix_word else f"{title} ({suffix_word})"
    text = template_text.replace("YYYY-MM-DD", date)
    text = re.sub(r"(?m)^title:.*$", f"title: {title}", text, count=1)
    text = re.sub(r"(?m)^# .*$", f"# {h1} — {date}", text, count=1)
    return text


def section_shape(placeholder_body):
    """Classify a template section body: 'task' | 'list' | 'prose'.

    Used as the fallback when the manifest doesn't state a section's shape.
    Recognizes a bare `-`, a `- ` bullet, and a `- [ ]` task item.
    """
    first = placeholder_body.strip().split("\n", 1)[0].strip()
    if first == "- [ ]":
        return "task"
    if first == "-" or first.startswith("- "):
        return "list"
    return "prose"


def render_body(lines, shape):
    """Format collected fill-mode lines according to a section shape."""
    if shape == "task":
        return "\n".join(f"- [ ] {l}" for l in lines)
    if shape == "list":
        return "\n".join(f"- {l}" for l in lines)
    if shape == "diagram":
        return "```mermaid\n" + "\n".join(lines) + "\n```"
    return "\n".join(lines)


def render_attendees(names):
    """Meeting front-matter flow list: `attendees: [A, B]`."""
    return "attendees: [" + ", ".join(names) + "]"


def render_tags(tags):
    """Timeline front-matter block list: `tags:` then `  - X` lines."""
    return "tags:\n" + "\n".join(f"  - {t}" for t in tags)
