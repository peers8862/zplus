# Phase B2 — Typed Fields, the `ref` Graph & `zplus check` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give doc types **typed front-matter fields** (including `ref`), read every entry into an in-memory **corpus graph** with computed backlinks, and ship **`zplus check`** to lint it — the foundation B3 renders from.

**Architecture:** Extend the manifest model with a `Field` type parsed from `[[type.field]]` blocks. Add a pure front-matter splitter (PyYAML) in `core.py`, a new `corpus.py` that walks `docs/` and resolves refs into backlinks, and a `check` command. Re-author the graph-bearing admin templated types to declare fields. No rendering yet (that is B3).

**Tech Stack:** Python ≥3.11, **PyYAML ≥6** (new dependency — approved 2026-07-06), stdlib `tomllib`, `unittest`.

## Global Constraints

- **B2 is model + read + lint only. No rendering.** Dashboards, backlink blocks in pages, the Attention Feed, `corpus.json`, boards/faceting are **B3/B4** — do not build them here.
- **Status is a field with `values` only.** Its workflow/transitions and kanban board are **B4**; `check` validates membership in `values`, nothing about transitions.
- **Ref-target existence is a `check`-time concern, not a parse-time one.** `manifest.loads` of a single type fragment must still succeed (fragments are partial); only `zplus check` (which sees the whole corpus) validates that a ref points at a real entry of the right type.
- **PyYAML is now a declared dependency** (`pyproject.toml`). Front-matter parsing uses `yaml.safe_load`.
- **Registries stay plain pages.** Roles/Systems/Policies/Vendors remain section-type pages (created by `add-page`); they are valid `ref` *targets* by slug without carrying fields themselves. Scaffolding fields into section pages is out of scope (later).
- Test framework: `unittest`, run `./.venv/bin/python -m unittest discover -s tests`.

## File Structure

- Modify: `pyproject.toml` (add PyYAML dep)
- Modify: `src/zplus/core.py` (add `split_front_matter`; extend `render_body`/hint for `diagram`)
- Modify: `src/zplus/manifest.py` (add `Field`, `VALID_FIELD_TYPES`, `diagram` shape; parse `[[type.field]]`; `fields` on `DocType`)
- Create: `src/zplus/corpus.py` (Entry/Corpus, `read_corpus`, `resolve`)
- Create: `src/zplus/commands/check.py` (`zplus check`)
- Modify: `src/zplus/cli.py` (wire `check`)
- Modify: `src/zplus/commands/entry.py` (`diagram` hint)
- Modify: admin type fragments + templates: `agent`, `automation`, `decision`, `incident`, `procedure` (add `[[type.field]]` + front-matter keys)
- Create: `tests/test_fields_and_corpus.py`

---

### Task 1: PyYAML dependency + front-matter splitter

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/zplus/core.py`
- Test: `tests/test_fields_and_corpus.py`

**Interfaces:**
- Produces: `core.split_front_matter(text: str) -> tuple[dict, str]` — returns `(front_matter_dict, body)`; `({}, text)` when there is no front matter.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_fields_and_corpus.py
import os
import tempfile
import unittest

from zplus import core


class FrontMatter(unittest.TestCase):
    def test_parses_scalars_and_lists(self):
        text = ("---\n"
                "date: 2026-07-06\n"
                "title: Invoice Bot\n"
                "owner: steve\n"
                "runs: [invoice-import, late-nudge]\n"
                "---\n"
                "# Invoice Bot\n\nbody here\n")
        fm, body = core.split_front_matter(text)
        self.assertEqual(fm["owner"], "steve")
        self.assertEqual(fm["runs"], ["invoice-import", "late-nudge"])
        self.assertIn("body here", body)

    def test_no_front_matter(self):
        fm, body = core.split_front_matter("# Just a heading\n")
        self.assertEqual(fm, {})
        self.assertIn("Just a heading", body)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus -v`
Expected: FAIL — `AttributeError: module 'zplus.core' has no attribute 'split_front_matter'`.

- [ ] **Step 3: Declare the dependency**

In `pyproject.toml`, change:
```toml
dependencies = []
```
to:
```toml
dependencies = ["pyyaml>=6"]
```
Then reinstall so the metadata updates: `cd /home/morgen/making/zplus && ./.venv/bin/pip install -q -e .`

- [ ] **Step 4: Implement `split_front_matter`**

At the top of `src/zplus/core.py`, add `import yaml` beside `import os`/`import re`. Then add:

```python
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
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.FrontMatter -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add pyproject.toml src/zplus/core.py tests/test_fields_and_corpus.py
git commit -m "feat: add PyYAML dep + core.split_front_matter"
```

---

### Task 2: Field model in the manifest (+ `diagram` shape)

**Files:**
- Modify: `src/zplus/manifest.py`
- Test: `tests/test_fields_and_corpus.py`

**Interfaces:**
- Produces: `manifest.Field(name, type="text", required=False, values=[], ref="", many=False)`; `DocType.fields: list[Field]`; `manifest.VALID_FIELD_TYPES`; `"diagram"` added to `VALID_SHAPES`. Parsing of `[[type.field]]` blocks in `from_dict`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_fields_and_corpus.py
from zplus import manifest

FIELD_FRAG = '''
[[type]]
name = "agent"
label = "Agents"
folder = "agents"
template = "agent.md"
landing = "Agents."
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["manual", "assisted", "supervised", "autonomous"]
  [[type.field]]
  name = "runs"
  type = "ref"
  ref = "automation"
  many = true
'''


class FieldModel(unittest.TestCase):
    def test_parses_fields(self):
        m = manifest.loads(FIELD_FRAG, source="agent")
        t = m.types[0]
        self.assertEqual([f.name for f in t.fields], ["owner", "status", "runs"])
        owner, status, runs = t.fields
        self.assertTrue(owner.required)
        self.assertEqual(status.values, ["manual", "assisted", "supervised", "autonomous"])
        self.assertEqual(runs.type, "ref")
        self.assertEqual(runs.ref, "automation")
        self.assertTrue(runs.many)

    def test_rejects_unknown_field_type(self):
        bad = FIELD_FRAG.replace('type = "owner"', 'type = "wizard"')
        with self.assertRaises(ValueError):
            manifest.loads(bad, source="bad")

    def test_ref_requires_target(self):
        bad = ('[[type]]\nname="x"\nlabel="X"\nfolder="x"\ntemplated=false\n'
               'landing="x"\n  [[type.field]]\n  name="r"\n  type="ref"\n')
        with self.assertRaises(ValueError):
            manifest.loads(bad, source="bad")

    def test_diagram_is_a_valid_shape(self):
        self.assertIn("diagram", manifest.VALID_SHAPES)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.FieldModel -v`
Expected: FAIL — `AttributeError: module 'zplus.manifest' has no attribute 'Field'`.

- [ ] **Step 3: Implement the field model**

In `src/zplus/manifest.py`:

Change the shapes constant:
```python
VALID_SHAPES = {"prose", "list", "task", "diagram"}
VALID_FIELD_TYPES = {"text", "enum", "multi-enum", "date", "number",
                     "bool", "owner", "status", "ref"}
```

Add the dataclass (below `Section`):
```python
@dataclass
class Field:
    name: str
    type: str = "text"
    required: bool = False
    values: list = field(default_factory=list)
    ref: str = ""
    many: bool = False
```

Add `fields` to `DocType`:
```python
@dataclass
class DocType:
    name: str
    label: str
    folder: str
    template: str = ""
    templated: bool = True
    landing: str = ""
    sections: list = field(default_factory=list)
    fields: list = field(default_factory=list)
```

In `from_dict`, after the `sections` loop and before `types.append(...)`, add field parsing:
```python
        fields = []
        for fdef in t.get("field", []):
            if "name" not in fdef:
                raise ValueError(
                    f"{source}: a field in type '{t['name']}' is missing 'name'")
            ftype = fdef.get("type", "text")
            if ftype not in VALID_FIELD_TYPES:
                raise ValueError(
                    f"{source}: invalid field type '{ftype}' in "
                    f"'{t['name']}/{fdef['name']}'")
            if ftype == "ref" and not fdef.get("ref"):
                raise ValueError(
                    f"{source}: ref field '{t['name']}/{fdef['name']}' "
                    f"needs a 'ref' target type")
            if ftype in ("enum", "multi-enum", "status") and not fdef.get("values"):
                raise ValueError(
                    f"{source}: {ftype} field '{t['name']}/{fdef['name']}' "
                    f"needs 'values'")
            fields.append(Field(name=fdef["name"], type=ftype,
                                required=fdef.get("required", False),
                                values=fdef.get("values", []),
                                ref=fdef.get("ref", ""),
                                many=fdef.get("many", False)))
```

Then include `fields` in the append:
```python
        types.append(DocType(name=t["name"], label=t["label"],
                             folder=t["folder"], template=t.get("template", ""),
                             templated=templated, landing=t.get("landing", ""),
                             sections=sections, fields=fields))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.FieldModel -v`
Expected: PASS. Then run the whole suite to confirm no regressions:
`./.venv/bin/python -m unittest discover -s tests` → all green (adding `diagram` and `fields` is additive).

- [ ] **Step 5: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/manifest.py tests/test_fields_and_corpus.py
git commit -m "feat: typed fields on doc types + diagram shape"
```

---

### Task 3: The corpus reader + ref resolution

**Files:**
- Create: `src/zplus/corpus.py`
- Test: `tests/test_fields_and_corpus.py`

**Interfaces:**
- Produces:
  - `corpus.Entry(type_name, slug, title, path, fields: dict, front_matter: dict, backlinks: dict)`
  - `corpus.Corpus(entries: list, by_slug: dict)` with `.get(slug)`
  - `corpus.read_corpus(project_dir, manifest) -> Corpus` — walks `docs/<folder>/*.md` (skips `index.md`), parses front matter, keeps only declared field keys.
  - `corpus.resolve(corpus, manifest) -> Corpus` — populates `entry.backlinks[(source_type, field_name)] = [source_slug, …]` from `ref` fields.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_fields_and_corpus.py
from zplus import corpus as corpus_mod


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


AGENT_TYPES = manifest.loads(FIELD_FRAG + '''
[[type]]
name = "automation"
label = "Automations"
folder = "automations"
template = "automation.md"
landing = "Automations."
''', source="fixture")


class CorpusGraph(unittest.TestCase):
    def _project(self, d):
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")
        _write(os.path.join(d, "docs", "agents", "invoice-bot.md"),
               "---\ntitle: Invoice Bot\nowner: steve\n"
               "status: supervised\nruns: [invoice-import]\n---\n# Invoice Bot\n")

    def test_reads_entries_and_declared_fields(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            c = corpus_mod.read_corpus(d, AGENT_TYPES)
            slugs = sorted(e.slug for e in c.entries)
            self.assertEqual(slugs, ["invoice-bot", "invoice-import"])
            bot = c.get("invoice-bot")
            self.assertEqual(bot.fields["owner"], "steve")
            self.assertEqual(bot.fields["runs"], ["invoice-import"])

    def test_resolve_populates_backlinks_on_target(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            c = corpus_mod.resolve(corpus_mod.read_corpus(d, AGENT_TYPES), AGENT_TYPES)
            target = c.get("invoice-import")
            self.assertEqual(target.backlinks[("agent", "runs")], ["invoice-bot"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.CorpusGraph -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'zplus.corpus'`.

- [ ] **Step 3: Implement `corpus.py`**

Create `src/zplus/corpus.py`:
```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.CorpusGraph -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/corpus.py tests/test_fields_and_corpus.py
git commit -m "feat: corpus reader + ref resolution (backlinks)"
```

---

### Task 4: `zplus check`

**Files:**
- Create: `src/zplus/commands/check.py`
- Modify: `src/zplus/cli.py`
- Test: `tests/test_fields_and_corpus.py`

**Interfaces:**
- Consumes: `manifest.load`, `corpus.read_corpus`, `corpus.resolve`.
- Produces: `check.run(project_dir) -> int` (0 clean, 1 with problems); `check.main(argv=None)`; a `check` subcommand.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_fields_and_corpus.py
from zplus.commands import check as check_cmd


class Check(unittest.TestCase):
    def _project(self, d, runs_slug, owner="steve"):
        _write(os.path.join(d, "zplus.toml"),
               'label="t"\n')  # placeholder, overwritten below
        # write a real project manifest with the two fixture types
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write('[project]\nprofile="fixture"\n' + FIELD_FRAG + '''
[[type]]
name = "automation"
label = "Automations"
folder = "automations"
template = "automation.md"
landing = "Automations."
''')
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")
        _write(os.path.join(d, "docs", "agents", "invoice-bot.md"),
               f"---\ntitle: Invoice Bot\nowner: {owner}\n"
               f"status: supervised\nruns: [{runs_slug}]\n---\n# Invoice Bot\n")

    def test_clean_corpus_returns_zero(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d, runs_slug="invoice-import")
            self.assertEqual(check_cmd.run(d), 0)

    def test_dangling_ref_and_missing_required_return_one(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d, runs_slug="does-not-exist", owner="")
            self.assertEqual(check_cmd.run(d), 1)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.Check -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'zplus.commands.check'`.

- [ ] **Step 3: Implement `check.py`**

Create `src/zplus/commands/check.py`:
```python
"""zplus check — lint the corpus against the manifest's field declarations."""
import os

from .. import manifest as manifest_mod, corpus as corpus_mod


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def run(project_dir):
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    c = corpus_mod.resolve(corpus_mod.read_corpus(project_dir, m), m)
    type_by_name = {t.name: t for t in m.types}
    problems = []
    for e in c.entries:
        t = type_by_name[e.type_name]
        for fl in t.fields:
            val = e.fields.get(fl.name)
            if fl.required and (val is None or val == "" or val == []):
                problems.append(f"{e.path}: missing required field '{fl.name}'")
                continue
            if val is None:
                continue
            if fl.type in ("enum", "status"):
                if val not in fl.values:
                    problems.append(
                        f"{e.path}: field '{fl.name}'='{val}' not in {fl.values}")
            elif fl.type == "multi-enum":
                for v in _as_list(val):
                    if v not in fl.values:
                        problems.append(
                            f"{e.path}: field '{fl.name}' value '{v}' not in {fl.values}")
            elif fl.type == "ref":
                for slug in _as_list(val):
                    target = c.by_slug.get(slug)
                    if target is None:
                        problems.append(
                            f"{e.path}: ref '{fl.name}' → unknown entry '{slug}'")
                    elif fl.ref and target.type_name != fl.ref:
                        problems.append(
                            f"{e.path}: ref '{fl.name}' → '{slug}' is a "
                            f"{target.type_name}, expected {fl.ref}")
    for p in problems:
        print(p)
    if problems:
        print(f"✗ {len(problems)} problem(s) across {len(c.entries)} entries")
        return 1
    print(f"✔ corpus OK: {len(c.entries)} entries")
    return 0


def main(argv=None):
    return run(os.getcwd())
```

- [ ] **Step 4: Wire the CLI**

In `src/zplus/cli.py`, add to the imports line:
```python
from .commands import (add_page as add_page_cmd, add_profile as add_profile_cmd,
                       add_type as add_type_cmd, apply as apply_cmd,
                       check as check_cmd,
                       entry as entry_cmd, nav as nav_cmd, new as new_cmd,
                       site as site_cmd)
```
Add the subparser (next to `gen-nav`):
```python
    sub.add_parser("check", help="lint the corpus (refs, required fields, enums)")
```
Add dispatch (next to the `gen-nav` branch):
```python
    if args.cmd == "check":
        return check_cmd.run(cwd)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.Check -v`
Expected: PASS (both).

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/commands/check.py src/zplus/cli.py tests/test_fields_and_corpus.py
git commit -m "feat: zplus check — lint refs, required fields, enums"
```

---

### Task 5: `diagram` shape scaffolding in new-entry

**Files:**
- Modify: `src/zplus/core.py` (`render_body` handles `diagram`)
- Modify: `src/zplus/commands/entry.py` (`_HINT` gains `diagram`)
- Test: `tests/test_fields_and_corpus.py`

**Interfaces:**
- Consumes: `core.render_body(lines, shape)`.
- Produces: `render_body(lines, "diagram")` wraps the lines in a ` ```mermaid ` fence.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_fields_and_corpus.py
class DiagramShape(unittest.TestCase):
    def test_render_body_wraps_mermaid(self):
        out = core.render_body(["graph TD", "A --> B"], "diagram")
        self.assertTrue(out.startswith("```mermaid\n"))
        self.assertIn("A --> B", out)
        self.assertTrue(out.rstrip().endswith("```"))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.DiagramShape -v`
Expected: FAIL — the current `render_body` returns the lines joined as prose (no fence).

- [ ] **Step 3: Implement**

In `src/zplus/core.py` `render_body`, add a `diagram` branch before the prose fallback:
```python
def render_body(lines, shape):
    """Format collected fill-mode lines according to a section shape."""
    if shape == "task":
        return "\n".join(f"- [ ] {l}" for l in lines)
    if shape == "list":
        return "\n".join(f"- {l}" for l in lines)
    if shape == "diagram":
        return "```mermaid\n" + "\n".join(lines) + "\n```"
    return "\n".join(lines)
```

In `src/zplus/commands/entry.py`, extend `_HINT`:
```python
_HINT = {"task": "one per line", "list": "one bullet per line",
         "prose": "type freely", "diagram": "mermaid syntax, one line per row"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.DiagramShape -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/core.py src/zplus/commands/entry.py tests/test_fields_and_corpus.py
git commit -m "feat: diagram section shape scaffolds a mermaid fence"
```

---

### Task 6: Declare fields on the graph-bearing admin types

Add `[[type.field]]` blocks to the five templated types that carry the graph, and add matching (empty) keys to their `template.md` front matter so `new-entry` produces field-ready entries. Registries (roles/systems/policies/vendors) stay plain — they are ref *targets* by slug.

**Files:**
- Modify: `src/zplus/data/types/agent/type.toml`, `.../agent/template.md`
- Modify: `src/zplus/data/types/automation/type.toml`, `.../automation/template.md`
- Modify: `src/zplus/data/types/decision/type.toml`, `.../decision/template.md`
- Modify: `src/zplus/data/types/incident/type.toml`, `.../incident/template.md`
- Modify: `src/zplus/data/types/procedure/type.toml`, `.../procedure/template.md`
- Test: `tests/test_fields_and_corpus.py`

> Note: `automation` is a **library** type reused by other profiles. Adding admin-oriented fields is acceptable (fields are optional metadata; other profiles' automation entries simply omit them and `check` only enforces `required`). Only `owner`/`status` are marked required, and only on types the admin profile owns.

**Interfaces:**
- Produces: `resolve_profile("administration")` yields these five types each with the fields below; their templates carry matching front-matter keys.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_fields_and_corpus.py
class AdminFields(unittest.TestCase):
    def test_graph_types_declare_expected_ref_fields(self):
        m = manifest.resolve_profile("administration")
        by = {t.name: t for t in m.types}
        agent_refs = {f.name: f.ref for f in by["agent"].fields if f.type == "ref"}
        self.assertEqual(agent_refs.get("runs"), "automation")
        self.assertEqual(agent_refs.get("governed_by"), "policy")
        auto_refs = {f.name: f.ref for f in by["automation"].fields if f.type == "ref"}
        self.assertEqual(auto_refs.get("touches"), "system")
        # every graph type carries a required owner
        for name in ["agent", "automation", "decision", "incident", "procedure"]:
            owners = [f for f in by[name].fields if f.name == "owner"]
            self.assertTrue(owners and owners[0].required, f"{name} needs required owner")

    def test_templates_have_field_keys(self):
        from zplus import paths
        agent_tpl = paths.read_type_template("agent").decode("utf-8")
        for key in ("owner:", "status:", "runs:", "governed_by:"):
            self.assertIn(key, agent_tpl)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.AdminFields -v`
Expected: FAIL — no `runs` ref field yet.

- [ ] **Step 3: Add fields to the five `type.toml` fragments**

Append these blocks to each existing fragment (after its `[[type.section]]` blocks — order among top-level keys/tables doesn't matter to `tomllib`, but append at end for clarity):

`agent/type.toml`:
```toml
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["manual", "assisted", "supervised", "autonomous"]
  [[type.field]]
  name = "runs"
  type = "ref"
  ref = "automation"
  many = true
  [[type.field]]
  name = "governed_by"
  type = "ref"
  ref = "policy"
  many = true
```

`automation/type.toml`:
```toml
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["manual", "assisted", "supervised", "autonomous"]
  [[type.field]]
  name = "touches"
  type = "ref"
  ref = "system"
  many = true
  [[type.field]]
  name = "governed_by"
  type = "ref"
  ref = "policy"
  many = true
```

`decision/type.toml`:
```toml
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["proposed", "decided", "superseded"]
  [[type.field]]
  name = "supersedes"
  type = "ref"
  ref = "decision"
  many = true
```

`incident/type.toml`:
```toml
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "severity"
  type = "enum"
  values = ["low", "medium", "high", "critical"]
  [[type.field]]
  name = "status"
  type = "status"
  values = ["open", "mitigated", "resolved", "postmortem"]
  [[type.field]]
  name = "involved"
  type = "ref"
  ref = "system"
  many = true
```

`procedure/type.toml`:
```toml
  [[type.field]]
  name = "owner"
  type = "ref"
  ref = "role"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["draft", "active", "deprecated"]
  [[type.field]]
  name = "uses"
  type = "ref"
  ref = "system"
  many = true
```

- [ ] **Step 4: Add matching front-matter keys to the five `template.md` files**

Replace each template's front-matter block (the top `---` … `---`) so the declared fields are present as empty keys. Example — `agent/template.md` front matter becomes:
```markdown
---
date: YYYY-MM-DD
title: Agent title
owner:
status:
runs: []
governed_by: []
---
```
Apply the analogous change to the other four (keys = each type's field names; `many=true` refs default to `[]`, scalars to empty):
- `automation/template.md`: `owner:`, `status:`, `touches: []`, `governed_by: []`
- `decision/template.md`: `owner:`, `status:`, `supersedes: []`
- `incident/template.md`: `owner:`, `severity:`, `status:`, `involved: []`
- `procedure/template.md`: `owner:`, `status:`, `uses: []`

Leave the body (H1 + `##` sections) of each template unchanged.

- [ ] **Step 5: Run test + full suite**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.AdminFields -v`
Expected: PASS.
Then: `./.venv/bin/python -m unittest discover -s tests` → all green.

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/data/types/agent src/zplus/data/types/automation \
        src/zplus/data/types/decision src/zplus/data/types/incident \
        src/zplus/data/types/procedure tests/test_fields_and_corpus.py
git commit -m "feat(admin): declare owner/status/ref fields on graph-bearing types"
```

---

### Task 7: End-to-end integration — stand up, seed, check

Verifies the whole chain against a real profile scaffold: fields flow from templates into entries, the corpus resolves refs, backlinks compute, and `check` distinguishes clean from broken.

**Files:**
- Test: `tests/test_fields_and_corpus.py`

- [ ] **Step 1: Write the test**

```python
# append to tests/test_fields_and_corpus.py
class IntegrationAdmin(unittest.TestCase):
    def _scaffold(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        # a system (ref target, plain page) + an automation that touches it
        _write(os.path.join(d, "docs", "systems", "billing.md"),
               "---\ntitle: Billing\n---\n# Billing\n")
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\nowner: steve\n"
               "status: supervised\ntouches: [billing]\ngoverned_by: []\n---\n# Invoice Import\n")

    def test_clean_scaffold_checks_ok_and_backlinks(self):
        with tempfile.TemporaryDirectory() as d:
            self._scaffold(d)
            self.assertEqual(check_cmd.run(d), 0)
            m = manifest.resolve_profile("administration")
            c = corpus_mod.resolve(corpus_mod.read_corpus(d, m), m)
            self.assertEqual(c.get("billing").backlinks[("automation", "touches")],
                             ["invoice-import"])

    def test_broken_ref_fails_check(self):
        with tempfile.TemporaryDirectory() as d:
            self._scaffold(d)
            _write(os.path.join(d, "docs", "automations", "bad.md"),
                   "---\ntitle: Bad\nowner: steve\nstatus: supervised\n"
                   "touches: [ghost-system]\n---\n# Bad\n")
            self.assertEqual(check_cmd.run(d), 1)
```

- [ ] **Step 2: Run it**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_fields_and_corpus.IntegrationAdmin -v`
Expected: PASS (Tasks 1–6 make this green; if it fails, the failure names the broken link in the chain).

- [ ] **Step 3: Manual CLI smoke (optional, needs a scaffold)**

```bash
cd /home/morgen/making && rm -rf b2-smoke
export PATH="/home/morgen/making/zplus/.venv/bin:$PATH"
zplus new b2-smoke --profile administration && cd b2-smoke
# seed one system + one automation referencing it, then:
zplus check     # expect: ✔ corpus OK
```

- [ ] **Step 4: Commit**

```bash
cd /home/morgen/making/zplus
git add tests/test_fields_and_corpus.py
git commit -m "test: end-to-end fields + corpus + check on administration scaffold"
```

---

## Self-Review

- **Spec coverage (design §4 + Phase B2):** typed fields (Task 2), `ref` as edges + backlinks (Task 3), `zplus check` for dangling refs / required / enums (Task 4), the `diagram` shape (Task 5, per mermaid decision), admin types declaring fields (Task 6), end-to-end verification (Task 7). Rendering (dashboards/backlink blocks/Attention Feed/corpus.json), status workflows/boards, and faceting are explicitly **not** here — B3/B4 per Global Constraints.
- **Placeholder scan:** none — every module and every field/template edit is inline.
- **Type/name consistency:** `Field(name, type, required, values, ref, many)` is defined in Task 2 and consumed identically in Tasks 3/4/6; `Entry`/`Corpus`/`read_corpus`/`resolve` signatures in Task 3 match their use in Tasks 4/7; `check.run(project_dir) -> int` in Task 4 matches Tasks 4/7 calls; ref targets in Task 6 (`automation`, `policy`, `system`, `role`, `decision`) are all real type names in the `administration` profile.
- **Dependency note:** PyYAML added in Task 1 and reinstalled (`pip install -e .`) so later tasks import `yaml`.
- **Known deferrals (documented, not gaps):** section-type/registry pages don't scaffold field front matter (they're ref targets only); status is membership-checked but transitions aren't (B4); `owner` as a free string vs. a Roles-registry ref is intentionally mixed (procedure.owner is a `ref`→role; others are `owner` scalars) — unifying is a later call.
