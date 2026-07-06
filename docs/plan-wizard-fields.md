# Wizard Fills Fields — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (or subagent-driven-development) to implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** `zplus new-entry --fill` prompts each of a type's declared fields — enums/status as pick-lists, `ref`s as pick-from-existing-entries — and writes the answers into the new entry's front matter, so the typed graph gets populated without hand-editing YAML.

**Architecture:** A pure `core.set_front_matter_value` injects a value into a front-matter key. `entry.fill_fields` reads the manifest + corpus (for ref candidates), prompts each declared field by type, and injects answers into the stamped template's front matter — run just before the existing section prompts in `create()`.

**Tech Stack:** Python ≥3.11, `unittest` (with `unittest.mock.patch` for input).

## Global Constraints

- **Only prompts fields the type declares** (`doc_type.fields`). Types with no fields behave exactly as today.
- **Front-matter keys already exist** in templates (B2 added them, e.g. `owner:`, `status:`, `runs: []`). `set_front_matter_value` *replaces* a key's value; if the key is absent it is a no-op (never invents front matter).
- **Refs are picked from existing entries** of the target type (read from the corpus); typing a raw slug is also allowed. `many=true` collects several; blank finishes.
- **Required fields re-prompt** until answered; optional fields accept blank (skip → key left as the template default).
- Field prompting runs **before** the section prompts, after title/date.
- Test framework: `unittest`; run `TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest discover -s tests`.

## File Structure

- Modify: `src/zplus/core.py` (`render_fm_value`, `set_front_matter_value`)
- Modify: `src/zplus/commands/entry.py` (`fill_fields`, `_choose`, `_choose_refs`; call from `create`)
- Create: `tests/test_wizard_fields.py`

---

### Task 1: `core.set_front_matter_value`

**Files:**
- Modify: `src/zplus/core.py`
- Test: `tests/test_wizard_fields.py`

**Interfaces:**
- Produces: `core.render_fm_value(value) -> str` (lists → `[a, b]`, scalars → `str`); `core.set_front_matter_value(text, key, value) -> str` (replaces the first `key:` line; no-op if absent).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_wizard_fields.py
import os
import tempfile
import unittest
from unittest import mock

from zplus import core


class SetFrontMatter(unittest.TestCase):
    def test_replaces_scalar_and_list(self):
        text = ("---\ndate: YYYY-MM-DD\ntitle: Bot\nowner:\nruns: []\n---\n# Bot\n")
        text = core.set_front_matter_value(text, "owner", "steve")
        text = core.set_front_matter_value(text, "runs", ["a", "b"])
        self.assertIn("owner: steve", text)
        self.assertIn("runs: [a, b]", text)

    def test_absent_key_is_noop(self):
        text = "---\ntitle: X\n---\n# X\n"
        self.assertEqual(core.set_front_matter_value(text, "owner", "steve"), text)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest tests.test_wizard_fields -v`
Expected: FAIL — `AttributeError: module 'zplus.core' has no attribute 'set_front_matter_value'`.

- [ ] **Step 3: Implement (append to `src/zplus/core.py`)**

```python
def render_fm_value(value):
    """Render a front-matter value: lists as [a, b], scalars as str."""
    if isinstance(value, list):
        return "[" + ", ".join(str(v) for v in value) + "]"
    return str(value)


def set_front_matter_value(text, key, value):
    """Replace `key:`'s value in the leading front matter. No-op if key absent."""
    pat = re.compile(rf"(?m)^{re.escape(key)}:.*$")
    if not pat.search(text):
        return text
    return pat.sub(f"{key}: {render_fm_value(value)}", text, count=1)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest tests.test_wizard_fields.SetFrontMatter -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/core.py tests/test_wizard_fields.py
git commit -m "feat: core.set_front_matter_value for wizard field injection"
```

---

### Task 2: `entry.fill_fields` — prompt declared fields and inject them

**Files:**
- Modify: `src/zplus/commands/entry.py`
- Test: `tests/test_wizard_fields.py`

**Interfaces:**
- Consumes: `manifest.load`, `corpus.read_corpus`, `corpus.resolve`, `core.set_front_matter_value`.
- Produces: `entry.fill_fields(text, doc_type, project_dir) -> str` — prompts each declared field (via `input()`), injects answers into `text`'s front matter, returns it. Called in `create()` before `run_fill` when `--fill`.

- [ ] **Step 1: Write the failing test** (patches `input` to drive the prompts)

```python
# append to tests/test_wizard_fields.py
from zplus import manifest
from zplus.commands import entry


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class FillFields(unittest.TestCase):
    def _project(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")

    def test_prompts_status_and_ref_and_injects(self):
        m = manifest.resolve_profile("administration")
        agent = next(t for t in m.types if t.name == "agent")
        template = ("---\ndate: YYYY-MM-DD\ntitle: Bot\nowner:\nstatus:\n"
                    "runs: []\ngoverned_by: []\n---\n# Bot\n")
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            # answers, in field order: owner(text), status(enum pick 3),
            # runs(ref: pick 1 then blank to finish), governed_by(ref: blank to finish)
            answers = iter(["steve", "3", "1", "", ""])
            with mock.patch("builtins.input", lambda *_a: next(answers)):
                out = entry.fill_fields(template, agent, d)
        self.assertIn("owner: steve", out)
        self.assertIn("status: supervised", out)       # 3rd maturity value
        self.assertIn("runs: [invoice-import]", out)   # picked existing automation


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest tests.test_wizard_fields.FillFields -v`
Expected: FAIL — `AttributeError: module 'zplus.commands.entry' has no attribute 'fill_fields'`.

- [ ] **Step 3: Implement in `src/zplus/commands/entry.py`**

Add to the imports at the top:
```python
from .. import core, manifest as manifest_mod, corpus as corpus_mod
```
(replace the existing `from .. import core, manifest as manifest_mod` line).

Add these functions (above `create`):
```python
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
```

Then call it in `create`, changing:
```python
    if fill:
        text = run_fill(text, doc_type)
```
to:
```python
    if fill:
        text = fill_fields(text, doc_type, project_dir)
        text = run_fill(text, doc_type)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest tests.test_wizard_fields.FillFields -v`
Expected: PASS.

- [ ] **Step 5: Full suite (no regressions)**

Run: `cd /home/morgen/making/zplus && TMPDIR=/home/morgen/making/.zplus-scratch ./.venv/bin/python -m unittest discover -s tests` → all green.

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/commands/entry.py tests/test_wizard_fields.py
git commit -m "feat: new-entry --fill prompts declared fields (enums, refs) into front matter"
```

---

### Task 3: Manual smoke — a wizard-driven agent entry, then check + gen-derived

**Files:** none (manual verification).

- [ ] **Step 1: Drive the wizard end-to-end (in ~/making)**

```bash
cd /home/morgen/making && rm -rf wiz-smoke
export PATH="/home/morgen/making/zplus/.venv/bin:$PATH"
zplus new wiz-smoke --profile administration >/dev/null && cd wiz-smoke
printf -- '---\ntitle: Billing\n---\n# Billing\n' > docs/systems/billing.md
printf -- '---\ndate: 2026-07-06\ntitle: Invoice Import\nowner: steve\nstatus: supervised\ntouches: [billing]\n---\n# Invoice Import\n' > docs/automations/invoice-import.md
# Now create an agent via the wizard, feeding answers on stdin:
#   type=agent, title, date(enter), owner=steve, status pick, runs pick 1 + blank, governed_by blank
# (EDITOR set to true so it doesn't open an editor)
printf '1\nInvoice Bot\n\nsteve\n3\n1\n\n\n' | EDITOR=true zplus new-entry --fill
echo "=== the created agent's front matter ===" && sed -n '1,10p' docs/agents/*invoice-bot*.md
echo "=== check passes? ===" && zplus check
cd /home/morgen/making && rm -rf wiz-smoke
```

Expected: the created agent file has `owner: steve`, `status: supervised`, `runs: [invoice-import]` in its front matter; `zplus check` reports `✔ corpus OK`. (Note: the `1` first line selects the `agent` type from the menu — confirm it is listed as option 1; if the menu order differs, adjust the leading digit.)

---

## Self-Review

- **Spec coverage:** implements design §7.1 mode 3 ("wizard prompts every field; enums → pick-lists, refs → pick-existing"). Sections prompting is unchanged (already existed).
- **Placeholder scan:** none — all code inline; Task 3 is a manual smoke with exact keystrokes.
- **Type/name consistency:** `set_front_matter_value`/`render_fm_value` (Task 1) are consumed in `fill_fields` (Task 2); `fill_fields(text, doc_type, project_dir)` is called in `create` with the same `project_dir` already in scope.
- **Known limits:** raw-slug entry for refs is accepted without validating it exists (that is `zplus check`'s job, run afterward); `many` refs render as an inline `[a, b]` list; `bool`/`number`/`date` fields use free-text entry (no special widget) — acceptable, refinement later.
