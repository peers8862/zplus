# Administration Profile — Phase A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a bundled `administration` profile so `zplus new x --profile administration` scaffolds a serveable "company OS" skeleton, using only the engine that already ships (SP1+SP2).

**Architecture:** Pure data authoring under `src/zplus/data/` — new type fragments (`types/<name>/type.toml` [+ `template.md`]) and a profile (`profiles/administration.toml`), exactly like the existing `projecthub` profile. No engine/Python changes. Reuses library types `meeting`, `idea`, `reference`, `automation`; adds admin-specific types.

**Tech Stack:** Python ≥3.11, stdlib `tomllib`, `unittest`. Data is TOML + Markdown consumed by the shipped `manifest`/`apply`/`nav` engine.

## Global Constraints

- **No engine code changes.** Phase A touches only `src/zplus/data/**` and `tests/**`. Anything needing a new `DocType`/`Section` capability (typed fields, refs, status, non-`prose|list|task` shapes, per-type ordering, nested nav, multi-page section seeding) is **out of scope — deferred to Phase B**.
- **Shapes are limited to `prose | list | task`** (the shipped `VALID_SHAPES`). No other shape may appear in any `[[type.section]]`.
- **Every type carries a one-line `landing`** so a fresh site shows the whole nav skeleton immediately (materialized to `docs/<folder>/index.md` by `apply`).
- **Templated types require a `template = "<file>.md"`** key AND a matching `template.md` in the type dir (manifest validation rejects a templated type without a template).
- **Follow the shipped `projecthub` shape exactly:** a profile is `label` + `description` + an ordered `types = [...]` list of type names that all exist in the library.
- Test framework: `unittest`, run with `python -m unittest`.

### Design note — mapping the design's §9 nav onto the flat engine

The engine models a **flat list of top-level types** (each type = one nav section = one `docs/` folder). It does **not** nest sections, seed multiple curated pages per section, order registries alphabetically-when-templated, or carry typed fields. So Phase A **flattens** the design's grouped nav (§9) into ~22 top-level types, ordered group-adjacent. This produces a functional-but-flat nav that deliberately exposes the engine's thinness (no grouping, no fields) — which is the empirical justification for Phase B. This flattening is the one significant assumption in this plan.

## File Structure

Create under `src/zplus/data/`:

**5 new templated types** (`type.toml` + `template.md` each):
`types/decision/`, `types/review/`, `types/procedure/`, `types/agent/`, `types/incident/`

**13 new section types** (`type.toml` only):
`types/mission-control/`, `types/company/`, `types/how-we-run/`, `types/operating-rhythm/`, `types/automation-program/`, `types/knowledge-base/`, `types/site-docs/`, `types/role/`, `types/system/`, `types/policy/`, `types/vendor/`, `types/constellation/`, `types/objective/`

**1 profile:** `profiles/administration.toml`

**Reused (do not author):** `meeting`, `idea`, `reference`, `automation`.

**Tests:** `tests/test_administration_profile.py`

---

### Task 1: New templated types (decision, review, procedure, agent, incident)

**Files:**
- Create: `src/zplus/data/types/decision/type.toml`, `.../decision/template.md`
- Create: `src/zplus/data/types/review/type.toml`, `.../review/template.md`
- Create: `src/zplus/data/types/procedure/type.toml`, `.../procedure/template.md`
- Create: `src/zplus/data/types/agent/type.toml`, `.../agent/template.md`
- Create: `src/zplus/data/types/incident/type.toml`, `.../incident/template.md`
- Test: `tests/test_administration_profile.py`

**Interfaces:**
- Consumes: `zplus.manifest.loads(text) -> Manifest`; `zplus.paths.read_type_fragment(name) -> str`; `zplus.paths.read_type_template(name) -> bytes`.
- Produces: five library types named `decision`, `review`, `procedure`, `agent`, `incident`, each `templated=true` with a `template` and `prose|list|task` sections. Later tasks (profile) reference these names.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_administration_profile.py
import unittest
from zplus import manifest, paths

NEW_TEMPLATED = ["decision", "review", "procedure", "agent", "incident"]

class TemplatedTypes(unittest.TestCase):
    def test_each_parses_as_templated_with_template_and_valid_shapes(self):
        for name in NEW_TEMPLATED:
            frag = paths.read_type_fragment(name)          # raises if dir absent
            m = manifest.loads(frag, source=name)          # raises on invalid shape
            self.assertEqual(len(m.types), 1)
            t = m.types[0]
            self.assertEqual(t.name, name)
            self.assertTrue(t.templated)
            self.assertTrue(t.template, f"{name} needs a template")
            self.assertTrue(t.landing, f"{name} needs a landing")
            self.assertTrue(t.sections, f"{name} needs sections")

    def test_each_template_file_present_with_headings(self):
        for name in NEW_TEMPLATED:
            body = paths.read_type_template(name).decode("utf-8")
            self.assertIn("date: YYYY-MM-DD", body)
            self.assertIn("## ", body)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile -v`
Expected: FAIL — `FileNotFoundError`/error from `read_type_fragment("decision")` (type dir absent).

- [ ] **Step 3: Author the five `type.toml` fragments**

`src/zplus/data/types/decision/type.toml`:
```toml
[[type]]
name = "decision"
label = "Decisions"
folder = "decisions"
template = "decision.md"
landing = "Decisions — context, options, and the call. Newest first."
  [[type.section]]
  heading = "Context"
  shape = "prose"
  prompt = "What decision is needed, and why now."
  [[type.section]]
  heading = "Options"
  shape = "list"
  prompt = "The choices considered."
  [[type.section]]
  heading = "Decision"
  shape = "prose"
  prompt = "The call made, and by whom."
  [[type.section]]
  heading = "Rationale"
  shape = "prose"
  prompt = "Why this option; trade-offs accepted."
  [[type.section]]
  heading = "Consequences"
  shape = "list"
  prompt = "What follows — actions and things to watch."
```

`src/zplus/data/types/review/type.toml`:
```toml
[[type]]
name = "review"
label = "Reviews"
folder = "reviews"
template = "review.md"
landing = "Business reviews — the operating heartbeat. Newest first."
  [[type.section]]
  heading = "Period"
  shape = "prose"
  prompt = "Which cadence and dates this review covers."
  [[type.section]]
  heading = "Scorecard"
  shape = "list"
  prompt = "The numbers that matter this period."
  [[type.section]]
  heading = "What happened"
  shape = "prose"
  prompt = "Highlights, lowlights, notable events."
  [[type.section]]
  heading = "Issues"
  shape = "list"
  prompt = "Problems to resolve."
  [[type.section]]
  heading = "Next"
  shape = "task"
  prompt = "Actions into the next period."
```

`src/zplus/data/types/procedure/type.toml`:
```toml
[[type]]
name = "procedure"
label = "Procedures"
folder = "procedures"
template = "procedure.md"
landing = "Standard operating procedures — how we do things."
  [[type.section]]
  heading = "Purpose"
  shape = "prose"
  prompt = "What this procedure achieves and when to use it."
  [[type.section]]
  heading = "Owner"
  shape = "prose"
  prompt = "The role responsible for this procedure."
  [[type.section]]
  heading = "Steps"
  shape = "task"
  prompt = "The procedure, step by step."
  [[type.section]]
  heading = "Notes"
  shape = "prose"
  prompt = "Edge cases, gotchas, links."
```

`src/zplus/data/types/agent/type.toml`:
```toml
[[type]]
name = "agent"
label = "Agents"
folder = "agents"
template = "agent.md"
landing = "AI agents in play — the software workforce. Newest first."
  [[type.section]]
  heading = "Brief"
  shape = "prose"
  prompt = "What this agent does, in a line or two."
  [[type.section]]
  heading = "Scope and tools"
  shape = "list"
  prompt = "What it can touch; systems and permissions."
  [[type.section]]
  heading = "Guardrails"
  shape = "list"
  prompt = "Limits, approvals required, oversight."
  [[type.section]]
  heading = "Owner and status"
  shape = "prose"
  prompt = "Who owns it; maturity (manual, assisted, supervised, autonomous)."
  [[type.section]]
  heading = "Notes"
  shape = "prose"
  prompt = "Automations it runs, incidents, governing policies."
```

`src/zplus/data/types/incident/type.toml`:
```toml
[[type]]
name = "incident"
label = "Incidents"
folder = "incidents"
template = "incident.md"
landing = "Incidents and postmortems — what broke and what we learned. Newest first."
  [[type.section]]
  heading = "What happened"
  shape = "prose"
  prompt = "The incident, plainly."
  [[type.section]]
  heading = "Impact"
  shape = "prose"
  prompt = "Who and what was affected, and how badly."
  [[type.section]]
  heading = "Resolution"
  shape = "list"
  prompt = "Steps taken to mitigate and resolve."
  [[type.section]]
  heading = "Prevention"
  shape = "task"
  prompt = "Changes to stop a recurrence."
```

- [ ] **Step 4: Author the five `template.md` files**

Each mirrors the shipped template format (`prose` → prompt text; `list` → `-`; `task` → `- [ ]`).

`src/zplus/data/types/decision/template.md`:
```markdown
---
date: YYYY-MM-DD
title: Decision title
---
# Decision title — YYYY-MM-DD

## Context
What decision is needed, and why now.

## Options
-

## Decision
The call made, and by whom.

## Rationale
Why this option; trade-offs accepted.

## Consequences
-
```

`src/zplus/data/types/review/template.md`:
```markdown
---
date: YYYY-MM-DD
title: Review title
---
# Review title — YYYY-MM-DD

## Period
Which cadence and dates this review covers.

## Scorecard
-

## What happened
Highlights, lowlights, notable events.

## Issues
-

## Next
- [ ]
```

`src/zplus/data/types/procedure/template.md`:
```markdown
---
date: YYYY-MM-DD
title: Procedure title
---
# Procedure title — YYYY-MM-DD

## Purpose
What this procedure achieves and when to use it.

## Owner
The role responsible for this procedure.

## Steps
- [ ]

## Notes
Edge cases, gotchas, links.
```

`src/zplus/data/types/agent/template.md`:
```markdown
---
date: YYYY-MM-DD
title: Agent title
---
# Agent title — YYYY-MM-DD

## Brief
What this agent does, in a line or two.

## Scope and tools
-

## Guardrails
-

## Owner and status
Who owns it; maturity (manual, assisted, supervised, autonomous).

## Notes
Automations it runs, incidents, governing policies.
```

`src/zplus/data/types/incident/template.md`:
```markdown
---
date: YYYY-MM-DD
title: Incident title
---
# Incident title — YYYY-MM-DD

## What happened
The incident, plainly.

## Impact
Who and what was affected, and how badly.

## Resolution
-

## Prevention
- [ ]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile -v`
Expected: PASS (both tests).

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/data/types/decision src/zplus/data/types/review \
        src/zplus/data/types/procedure src/zplus/data/types/agent \
        src/zplus/data/types/incident tests/test_administration_profile.py
git commit -m "feat(admin): add decision/review/procedure/agent/incident templated types"
```

---

### Task 2: Section types (group landings + registries)

**Files:**
- Create (each is a single `type.toml`): `src/zplus/data/types/{mission-control,company,how-we-run,operating-rhythm,automation-program,knowledge-base,site-docs,role,system,policy,vendor,constellation,objective}/type.toml`
- Test: `tests/test_administration_profile.py` (add a class)

**Interfaces:**
- Consumes: `zplus.manifest.loads`, `zplus.paths.read_type_fragment`.
- Produces: 13 library types, each `templated=false` with a `landing` and no template. Names the profile (Task 3) references.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_administration_profile.py
NEW_SECTIONS = ["mission-control", "company", "how-we-run", "operating-rhythm",
                "automation-program", "knowledge-base", "site-docs", "role",
                "system", "policy", "vendor", "constellation", "objective"]

class SectionTypes(unittest.TestCase):
    def test_each_parses_as_section_with_landing(self):
        for name in NEW_SECTIONS:
            frag = paths.read_type_fragment(name)
            m = manifest.loads(frag, source=name)
            self.assertEqual(len(m.types), 1)
            t = m.types[0]
            self.assertEqual(t.name, name)
            self.assertFalse(t.templated, f"{name} must be a section (templated=false)")
            self.assertFalse(t.template, f"{name} must not declare a template")
            self.assertTrue(t.landing, f"{name} needs a landing")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile.SectionTypes -v`
Expected: FAIL — error reading `read_type_fragment("mission-control")`.

- [ ] **Step 3: Author the 13 section `type.toml` files**

```toml
# src/zplus/data/types/mission-control/type.toml
[[type]]
name = "mission-control"
label = "Mission Control"
folder = "mission-control"
templated = false
landing = "Start here: what this site is, how to use it, and where everything lives."
```
```toml
# src/zplus/data/types/company/type.toml
[[type]]
name = "company"
label = "Company"
folder = "company"
templated = false
landing = "Who we are: overview, mission, values, and the company record."
```
```toml
# src/zplus/data/types/how-we-run/type.toml
[[type]]
name = "how-we-run"
label = "How We Run"
folder = "how-we-run"
templated = false
landing = "The functional handbook — finance, people, legal, operations, IT."
```
```toml
# src/zplus/data/types/operating-rhythm/type.toml
[[type]]
name = "operating-rhythm"
label = "Operating Rhythm"
folder = "operating-rhythm"
templated = false
landing = "The cadence that runs the company: decision rights, routines, scorecard."
```
```toml
# src/zplus/data/types/automation-program/type.toml
[[type]]
name = "automation-program"
label = "Automation & AI"
folder = "automation-program"
templated = false
landing = "The path to an Automated Enterprise: maturity ladder, division of duties, guardrails."
```
```toml
# src/zplus/data/types/knowledge-base/type.toml
[[type]]
name = "knowledge-base"
label = "Knowledge Base"
folder = "knowledge-base"
templated = false
landing = "How-tos and cross-cutting reference."
```
```toml
# src/zplus/data/types/site-docs/type.toml
[[type]]
name = "site-docs"
label = "Site Docs"
folder = "site-docs"
templated = false
landing = "About this site: how to add entries and how the tooling works."
```
```toml
# src/zplus/data/types/role/type.toml
[[type]]
name = "role"
label = "Roles"
folder = "roles"
templated = false
landing = "Who does what: one page per role."
```
```toml
# src/zplus/data/types/system/type.toml
[[type]]
name = "system"
label = "Systems"
folder = "systems"
templated = false
landing = "The tools and services we run on: one page per system."
```
```toml
# src/zplus/data/types/policy/type.toml
[[type]]
name = "policy"
label = "Policies"
folder = "policies"
templated = false
landing = "The rules we operate by: one page per policy."
```
```toml
# src/zplus/data/types/vendor/type.toml
[[type]]
name = "vendor"
label = "Vendors"
folder = "vendors"
templated = false
landing = "Who we buy from: one page per vendor."
```
```toml
# src/zplus/data/types/constellation/type.toml
[[type]]
name = "constellation"
label = "Constellation"
folder = "constellation"
templated = false
landing = "The company's other sites, and when to use each."
```
```toml
# src/zplus/data/types/objective/type.toml
[[type]]
name = "objective"
label = "Objectives"
folder = "objectives"
templated = false
landing = "Strategy and OKRs: one page per objective period."
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile.SectionTypes -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/data/types/mission-control src/zplus/data/types/company \
        src/zplus/data/types/how-we-run src/zplus/data/types/operating-rhythm \
        src/zplus/data/types/automation-program src/zplus/data/types/knowledge-base \
        src/zplus/data/types/site-docs src/zplus/data/types/role \
        src/zplus/data/types/system src/zplus/data/types/policy \
        src/zplus/data/types/vendor src/zplus/data/types/constellation \
        src/zplus/data/types/objective tests/test_administration_profile.py
git commit -m "feat(admin): add curated section + registry types with landings"
```

---

### Task 3: The `administration` profile

**Files:**
- Create: `src/zplus/data/profiles/administration.toml`
- Test: `tests/test_administration_profile.py` (add a class)

**Interfaces:**
- Consumes: `zplus.manifest.resolve_profile(name) -> Manifest` (validates every referenced type exists; raises `ValueError` on a missing name); `zplus.manifest.available_profiles() -> list[str]`.
- Produces: a bundled profile `administration` resolving to 22 types in a fixed group-adjacent order.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_administration_profile.py
EXPECTED_ORDER = [
    "mission-control", "constellation",
    "company", "role", "objective",
    "how-we-run", "procedure", "policy", "system", "vendor",
    "operating-rhythm", "review", "meeting", "decision",
    "automation-program", "agent", "automation", "incident", "idea",
    "knowledge-base", "reference",
    "site-docs",
]

class AdministrationProfile(unittest.TestCase):
    def test_profile_is_available(self):
        self.assertIn("administration", manifest.available_profiles())

    def test_resolves_to_expected_types_in_order(self):
        m = manifest.resolve_profile("administration")
        self.assertEqual([t.name for t in m.types], EXPECTED_ORDER)
        self.assertEqual(m.project.profile, "administration")

    def test_every_type_has_a_landing(self):
        m = manifest.resolve_profile("administration")
        for t in m.types:
            self.assertTrue(t.landing, f"{t.name} missing landing")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile.AdministrationProfile -v`
Expected: FAIL — `read_profile("administration")` errors (profile file absent).

- [ ] **Step 3: Author the profile**

`src/zplus/data/profiles/administration.toml`:
```toml
label = "Administration"
description = "Broad company operating system — mission control for running the whole enterprise and steering it toward an Automated Enterprise: mission control, company & strategy, the functional handbook (how we run), operating rhythm (reviews/meetings/decisions), the automation & AI program (agents/automations/incidents/ideas), a knowledge base, and registries (roles, systems, policies, vendors, objectives, sites)."
types = [
  "mission-control", "constellation",
  "company", "role", "objective",
  "how-we-run", "procedure", "policy", "system", "vendor",
  "operating-rhythm", "review", "meeting", "decision",
  "automation-program", "agent", "automation", "incident", "idea",
  "knowledge-base", "reference",
  "site-docs",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile.AdministrationProfile -v`
Expected: PASS (all three).

- [ ] **Step 5: Run the whole suite (no regressions)**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest -v`
Expected: PASS — the new file plus all existing `tests/*` green (confirms the added types didn't break `projecthub` or manifest tests).

- [ ] **Step 6: Commit**

```bash
cd /home/morgen/making/zplus
git add src/zplus/data/profiles/administration.toml tests/test_administration_profile.py
git commit -m "feat(admin): add the administration profile (22 types, grouped order)"
```

---

### Task 4: End-to-end smoke — scaffold, apply, serve

Automated tests cover resolution; this task verifies the profile actually scaffolds a serveable site through the real CLI. It is a **documented manual verification** (needs `zensical` in the repo `.venv`), plus one automated landing-materialization check that needs no external tools.

**Files:**
- Test: `tests/test_administration_profile.py` (add a class)

**Interfaces:**
- Consumes: `zplus.manifest.resolve_profile_text(name) -> str` (composes a self-contained project `zplus.toml`); `zplus.commands.apply._materialize_landings(project_dir) -> list[str]` (writes `docs/<folder>/index.md` per type with a landing).

- [ ] **Step 1: Write the failing test (automated landing check)**

```python
# append to tests/test_administration_profile.py
import os, tempfile
from zplus.commands import apply as apply_cmd

class LandingMaterialization(unittest.TestCase):
    def test_apply_writes_a_landing_index_per_type(self):
        m = manifest.resolve_profile("administration")
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            # write the resolved project manifest so apply reads the same types
            with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
                f.write(manifest.resolve_profile_text("administration"))
            written = apply_cmd._materialize_landings(d)
            self.assertEqual(len(written), len(m.types))
            for t in m.types:
                idx = os.path.join(d, "docs", t.folder, "index.md")
                self.assertTrue(os.path.exists(idx), f"missing landing for {t.name}")
                self.assertIn(t.label, open(idx, encoding="utf-8").read())
```

> Note for the implementer: `_materialize_landings` loads the project's `zplus.toml` internally. If its signature differs from `(project_dir) -> list`, adapt this test to the actual function (see `src/zplus/commands/apply.py:67`) — the assertion (one `index.md` per type, containing its label) is what matters. If it cannot be called in isolation, drop this automated test and rely on the manual smoke below; do not add engine code to make it testable (that is Phase B).

- [ ] **Step 2: Run test to verify it fails, then passes**

Run: `cd /home/morgen/making/zplus && ./.venv/bin/python -m unittest tests.test_administration_profile.LandingMaterialization -v`
Expected: FAIL first only if a prior task is incomplete; with Tasks 1–3 done it should PASS (all types + profile exist). If it errors on the `_materialize_landings` signature, follow the note above.

- [ ] **Step 3: Manual smoke test (documented; requires `zensical`)**

Run:
```bash
cd /tmp && rm -rf admin-smoke
zplus new admin-smoke --profile administration
cd admin-smoke
zplus serve      # regenerates nav, serves at http://localhost:8000
```
Expected:
- `zplus new` completes; `docs/` contains an `index.md` landing for every type folder (`mission-control/`, `company/`, `agents/`, `decisions/`, …).
- `zplus.toml` `[project].profile = "administration"` and the managed nav region lists all 22 labels (Mission Control, Constellation, Company, … Site Docs).
- The served site shows the full flat admin nav skeleton, each section opening on its landing page.

Record the result (and any rough edges — the flat 22-item nav, absence of fields — these are the Phase-B inputs) as a short note appended to `QUESTIONS.md` under the design-stage section.

- [ ] **Step 4: Commit**

```bash
cd /home/morgen/making/zplus
git add tests/test_administration_profile.py
git commit -m "test(admin): landing materialization + manual scaffold smoke for administration"
```

---

## Self-Review

- **Spec coverage (design §9 / §10 Phase A):** the 22-type roster covers every group and collection in §9.1 (Mission Control, Company, How We Run, Operating Rhythm, Automation & AI, Knowledge Base, Site Docs) and the registries (Roles, Systems, Policies, Vendors, Constellation/Sites, Objectives); the templated streams (Decisions, Reviews, Meetings, Procedures, Automations, Agents, Incidents, Ideas, References) are present via new + reused types. Phase-B-only items (typed fields, refs, status, dashboards, Attention Feed, nesting) are explicitly out of scope per Global Constraints.
- **Deferred-with-reason (documented, not gaps):** per-section multi-page seeding (engine seeds only the landing), registry alphabetical ordering (templated types are newest-first), and nav grouping — all Phase B; called out in the Design note and Global Constraints.
- **Placeholder scan:** none — every type's full TOML and every template's full Markdown is inline.
- **Type/name consistency:** the 22 names in `EXPECTED_ORDER` (Task 3), the profile `types` list (Task 3), and the authored dirs (Tasks 1–2) + reused library names (`meeting`, `idea`, `reference`, `automation`) match exactly.
