---
date: 2026-07-05
title: zplus — profiles, typed-graph corpus & authoring CLI (design)
status: draft-for-review (reconciled with shipped SP1/SP2 on 2026-07-06 — see §2a)
extends: plan.md   # SP1 foundation plan (this repo)
---

# zplus — profiles, typed-graph corpus & authoring CLI

## 1. Purpose & context

SP1 turned doc types into **data** (a per-project manifest) on top of a pip-installable
engine. This spec builds the platform on that foundation. It covers three linked
advances:

1. **Profiles** — named, complete starter bundles (`administration`, `sales`, …) that
   `zplus new` scaffolds, so a whole purpose-built site comes up in one command.
2. **A typed-graph corpus** — entries carry typed fields; a `ref` field is an edge, so
   the corpus becomes a graph the build can traverse to derive dashboards, backlinks,
   an action feed, and a machine-readable export.
3. **An authoring CLI with a simple→complex→AI onboarding ramp** — every way of
   populating a site (six modes) sits behind one clean verb set and one sequential
   prompt flow, so a beginner is running in one command and a power user (or an AI) can
   go arbitrarily deep from the *same* prompts.

The strategic frame: zplus grows a **constellation of company sites** that let humans
manage a business *and* let it evolve into an **Automated Enterprise** whose changing
workings stay continuously documented — and therefore comprehensible to its human
owners. **`administration`** is the first profile that exercises the entire architecture
(§9), so building it is the forcing function that proves the platform.

## 2. Design goals & non-negotiables

- **Dual mandate.** The site is a *knowledge center* (reference) **and** an *action
  center* (what needs doing/deciding) — the action half is *derived*, not curated.
- **Comprehensibility as automation grows.** Any automation/agent must be traceable to
  what it runs, touches, and is governed by, without hand-maintained links.
- **Zero-friction express path (non-negotiable).** `zplus new <site> --profile P` →
  a complete, seeded, serveable site with **no further questions**. Every advanced
  capability below is *opt-in* and must never tax the beginner.
- **Progressive disclosure.** Simple → complex → AI-oriented options all live inside
  **one** sequential prompt flow; each prompt has a fast default (Enter to accept) and a
  branch to "customize" or "let AI suggest."
- **One interface for humans and agents.** The CLI is the write-API; `corpus.json` is
  the read-API; humans and agents use both identically.
- **Static-first.** All derivation happens at build time from front-matter; no runtime
  server. `corpus.json` enables optional client-side interactivity later.

## 2a. Reconciliation with shipped SP1/SP2 (2026-07-06)

This design targets the zplus repo **as built** — SP1 + SP2 are already committed, so much
of the "structure" layer exists. Mapping the design's vocabulary onto what ships:

| This design | Shipped today | Status |
|---|---|---|
| Collection (stream) | a **templated** type (`templated=true`) — dated entries via `new-entry`, newest-first | exists |
| Collection (curated) | a **section** type (`templated=false`) — A→Z folder, plain pages via `add-page` | exists |
| Page / landing | a type's `landing` → its `index.md`; individual `add-page` subpages | exists |
| Layout | a type's inline `sections` list (`[[type.section]]`) | exists (not a reusable named object yet) |
| Type in a nav slot | a `[[type]]` + `gen-nav` managed region (`ZPLUS_TYPES`) | exists |
| Profile | `data/profiles/<name>.toml`: `label` + `description` + ordered `types=[…]` | exists |
| Shared type library | `data/types/<name>/` (bundled) ∪ `$ZPLUS_HOME` (user) | exists |
| **Order strategy** (date-desc/alpha/manual/status) | the `templated` bool (true≈date-desc, false≈alpha) | **generalizes the bool — NEW** |
| **Typed fields · `ref` graph · status workflow · views** | — | **NEW** |
| **Shapes** table/fields/diagram/callout/links | `VALID_SHAPES = prose\|list\|task` | **extend the set — NEW** |

**Already-shipped verbs:** `new · apply · profiles · add-type · add-profile ·
new-entry (--fill) · add-page · gen-nav · serve · build · deploy`. `add-type`/`add-profile`
are interactive and write to the **user** library (`$ZPLUS_HOME`); the pip package is never
edited in place (QUESTIONS #14).

**Where `administration` lives:** it is a **maintainer-shipped bundled profile** — authored
into the package `src/zplus/data/` (new `types/<…>/` fragments + `profiles/administration.toml`),
exactly as `projecthub` was. Since `add-type`/`add-profile` build *user* profiles, the
"dogfood a live site then snapshot it into the package" path (§6) needs a future
`--to-package` flag (QUESTIONS #14); until then admin is hand-authored into `data/`.

## 3. The core model (the grammar)

Six nested primitives; each has a fast CLI verb (§7).

```
PROFILE          a curated arrangement, shipped in the package
  └ NAV          a tree of Pages + Collections (hand regions + tool-managed regions)
      ├ PAGE       singleton, hand-written  (landings, vision, orientation)
      └ COLLECTION a Type bound to a nav node; grows via add-entry
            └ TYPE     layout + fields + order-strategy + status-workflow + views
            │          (from a SHARED library ∪ profile-specific types)
            │   ├ LAYOUT   an ordered set of SECTION blocks (composed via add-section)
            │   │   └ SECTION heading + shape + prompt
            │   └ FIELDS  typed front-matter (see §4)
```

- **Section block** — the atom: `{ heading, shape, prompt, default? }`.
  Shapes: `prose · list · task · table · fields · diagram · callout · links`.
- **Layout** — an ordered list of section blocks; what `add-section` edits.
- **Type** — a Layout + folder + field schema + **order strategy**
  (`date-desc · alpha · manual · status`) + optional **status workflow** + **views**;
  `single` or `collection` cardinality.
- **Collection** — a Type placed at a nav node; grown with `add-entry`. May be **flat**
  or **faceted** (grouped by one field, e.g. Procedures by function).
- **Page** — a singleton, hand-authored.
- **Profile** — the nav arrangement + type set + seed content.

**Manifest.** All of this extends the shipped `zplus.toml`: today `[[type]]` already
carries `name/label/folder/template/templated/landing` + inline `[[type.section]]`
(`heading/shape/prompt`), and `[project]` already carries `profile/managed_nav/
deploy_*`. This design **adds** to `[[type]]`: `fields`, `order`, `status`, `views` (and
`templated` becomes shorthand for `order = date-desc|alpha`). The `add-*` verbs write it,
the engine reads it. See §2a for how "Collection"/"Page" map to the shipped `templated`
bool — they are *roles a type plays*, not new objects.

## 4. Typed fields & the corpus graph

**Field types:** `text · enum · multi-enum · date · number · bool · owner · status · ref`.

**`ref` is the keystone.** A `ref` field's value *is another entry*, so fields become
**edges** and the corpus becomes a typed **graph**:

- `Automation.runs_on → Agent`, `.touches → System[]`, `.governed_by → Policy`
- `Procedure.owned_by → Role`, `.uses → System[]`
- `Incident.involved → Agent|System[]`, `.violated → Policy`
- `Decision.supersedes → Decision`, `.affects → Function`

`add-entry` prompts refs as **pick-from-existing** (not free text), so the graph stays
connected by construction; `zplus check` (§5) fails on dangling refs.

**Backlinks & rollups (derived).** Every entry gets reverse edges for free; the build
renders them: a **Role** page auto-lists "Procedures owned by this role"; an **Agent**
page lists "Automations I run · Incidents I was in · Policies that govern me." This is
the comprehensibility engine — traceability with zero hand-maintenance.

**Status as a lifecycle.** `status` is an enum plus an optional state machine:

| Type | Workflow |
|---|---|
| Idea | proposed → accepted → building → live → retired |
| Automation / Agent | **manual → assisted → supervised → autonomous** (the maturity ladder) |
| Incident | open → mitigated → resolved → postmortem |
| Decision | proposed → decided → superseded |
| Procedure | draft → active → deprecated |

`status` + `last_reviewed` + `review_cadence` yields **staleness**, which feeds §5.

## 5. The derived surface (build-time)

From fields + graph, the build generates:

- **Collection dashboards & views** — a landing renders as a `table`, `board`
  (grouped by status — the maturity ladder as a kanban), `timeline`, or `graph`.
- **The Attention Feed** — one derived page aggregating status + staleness + missing
  fields across *all* collections: overdue reviews · open incidents · automations
  awaiting approval · ideas needing a decision · entries with no owner. It is the
  action center; nobody curates it, so it can't go stale.
- **The agent contract** — `corpus.json` (every entry + fields + resolved refs +
  computed backlinks) plus an `llms.txt`-style index, emitted beside the HTML. This is
  the site's read-API. (Staticrypt seam: it sits in the same unencrypted bucket as
  today's `search.json` — a deliberate trade to record per site.)
- **`zplus check`** — lints broken refs, missing required fields, illegal status
  transitions, and unowned entries. Runs in build and CI; it is what lets humans and
  agents trust the Attention Feed.

## 6. Profiles & the shared Type library

- A **Profile** is `data/profiles/<name>.toml` — `label` + `description` + an ordered
  `types = […]` list — which `zplus new --profile <name>` resolves into a self-contained
  project `zplus.toml` (full defs, editable). Its types + templates live in
  `data/types/<name>/`. (Matches the shipped `projecthub` profile exactly.)
- **Shared Type library.** Types like `meeting · decision · procedure · incident` are
  not admin-specific; they live in the shared library (`data/types/`, bundled ∪ user)
  that profiles compose from, plus profile-specific types (admin adds `agent ·
  automation · role · policy · system`). Authoring a Type once and reusing it across the
  constellation is what keeps new sites cheap.
- **`save-profile` (dogfooding).** The aim: build a site *with the authoring verbs*, then
  `zplus save-profile <name>` freezes that arrangement into a reusable profile — "populate
  the site" and "author the profile" become one activity. **Caveat (reconciliation):**
  `add-type`/`add-profile` write the *user* library today, so shipping a profile *into the
  package* needs the future `--to-package` flag (QUESTIONS #14). Until then `administration`
  is hand-authored into `src/zplus/data/` like `projecthub`.

## 7. The authoring CLI

| Verb | Does | Status |
|---|---|---|
| `zplus new <site> [--profile P]` | scaffold a site from a profile (`--profile` default `projecthub`) | shipped |
| `zplus profiles` | list available profiles | shipped |
| `zplus new-entry [--fill]` | scaffold a dated entry of a templated type (the daily driver); `--fill` prompts each section | shipped |
| `zplus add-page` | add a plain subpage to a section (non-templated) type | shipped |
| `zplus add-type` | interactively define a new type → user library | shipped |
| `zplus add-profile` | interactively compose a profile from library types → user library | shipped |
| `zplus apply / gen-nav / serve / build / deploy` | overlay/update · wire nav · operate | shipped |
| `zplus check` | lint the corpus (dangling refs · required fields · status · unowned) | **NEW** |
| `zplus jot "…"` | quick-capture → draft entry to triage | **NEW** |
| `zplus add-section [--type T]` | edit an existing type's layout outside `add-type` | **NEW** (sections are composed *inside* `add-type` today) |
| `zplus save-profile <name> [--to-package]` | snapshot the live site into a reusable profile | **NEW** (cf. `add-profile`; QUESTIONS #14) |

There is deliberately **no `add-collection`** — a "collection" is just a *templated* type;
you create it with `add-type` and it appears in the nav via `gen-nav`.

### 7.1 The six population modes (all planned)

Every content/structure verb accepts a **mode**, from all-hand to agent-led:

1. **Raw markdown** — write the file directly. The escape hatch; always valid.
2. **Scaffold + edit** *(default)* — verb stamps a correctly-named, layout-filled file
   and opens `$EDITOR`. Best for prose-heavy entries.
3. **Guided wizard** (`--wizard`) — prompts every section *and field*; enums become
   pick-lists, refs become "pick an existing entry," validates on save. Best for a
   non-technical owner; keeps the graph connected.
4. **One-shot flags** (`--set field=value …`) — everything on the command line;
   scriptable, fast for power users.
5. **Batch / declarative** (`--from file.yaml|csv`, `zplus seed seed.yaml`) — the rapid
   lever: stand up a whole registry, or a whole site's pages+collections+entries, in one
   call.
6. **Agent-led** — an agent runs the *same verbs*; the human dictates and confirms.
   No separate "agent mode" — one CLI, both sides use it; `check` guards the door
   regardless of who knocked.

*Shipped baseline:* modes **1** (raw) and **2** (scaffold+edit — `new-entry` default)
work today; mode **3** partially — `--fill` prompts each *section* but not fields (fields
don't exist yet), and grows to prompt fields/refs once §4 lands. Modes **4–6** are new
here; `new-entry`/`add-type`/`add-profile` are interactive-only today (QUESTIONS #16).

### 7.2 Accelerators

`--like <entry>` (clone), `jot` (friction-free capture), `--dry-run` (preview the file +
`zensical.toml` diff before writing). **Deferred to a later phase:** a standalone
`add-section` layout editor and the reusable **section-block library** — today sections
are composed *inside* `add-type`; presets grow once the platform is built.

## 8. Onboarding ramp — `zplus new`, simple → complex → AI

The central UX requirement: **auto site-generation must range from simple to complex to
AI-oriented, with every option baked into one sequential prompt flow that allows manual
human engagement at each step.** Same flow, graduated depth.
*(Status: Level 0 ships today via `zplus new --profile …`; Levels 1–3 are new here.)*

- **Level 0 — Express (non-negotiable, zero friction) — SHIPPED.**
  `zplus new mysite --profile administration` → a complete, seeded, serveable site,
  no questions asked. `zplus serve` and you're live. (Works today for `projecthub`;
  needs the `administration` profile authored — Phase A.)
- **Level 1 — Guided.** `zplus new` (no flags) → a short sequential prompt flow:
  *site name → pick a profile (with descriptions) → light identity (company, owner) →
  which optional collections to include*. Every prompt has a fast default (Enter
  accepts); finishing early at any point yields a valid site.
- **Level 2 — Tailored.** At any prompt, choose **"customize"** to go deeper in place:
  add/remove collections, add a type, tweak a field schema, compose sections (raw
  `add-section`). Power path, never required.
- **Level 3 — AI-oriented.** At any prompt, choose **"let AI suggest"**, or start with
  `zplus new --describe "we're a 12-person accounting firm…"`. The engine proposes a
  profile arrangement (which collections/types/fields fit the described business) and
  can draft seed entries; **the human reviews and approves/edits each proposal through
  the same sequential prompts.** AI proposes; the prompts keep the human in control.

**Principle.** The prompt flow is a difficulty ramp: defaults carry beginners through in
seconds; "customize" and "let AI suggest" branches at each node open the full power and
AI surface without ever forcing them on. One flow, three depths, human always able to
step in.

## 9. The `administration` profile (first concrete instance)

### 9.1 Nav — Pages (singletons) + Collections

```
Mission Control      index · how-this-site-works · for-ai-agents · the-constellation*
                     · automated-enterprise (north star + maturity ladder) · glossary
Company              overview · mission-vision-values · key-facts · Roles* · Objectives(OKR)*
How We Run           index · Procedures* (faceted by function) · Policies* · Systems* · Vendors*
Operating Rhythm     index (cadence) · decision-rights · scorecard · Reviews* · Meetings*
Automation & AI      index (program) · maturity-ladder · division-of-duties
                     · oversight-and-guardrails · Agents* · Automations* · Incidents*
                     · roadmap (= Ideas* board)
Knowledge Base       index · how-to hub · References*
Site Docs            how to add entries · the profile's tooling
```
`*` = a Collection (type-backed, grows via `add-entry`). Everything else is a Page.

### 9.2 Type set (fields · status · key refs · order · default view)

| Type | Key fields | Status workflow | Order / view |
|---|---|---|---|
| Decision | owner, date, affects→Function[], supersedes→Decision? | proposed→decided→superseded | date-desc · timeline |
| Review | period, owner, scorecard, issues→Incident[]? | — | date-desc · table |
| Meeting | date, attendees, decisions→Decision[] | — | date-desc · table |
| Procedure | owner→Role, function(facet), uses→System[], last_reviewed, review_cadence | draft→active→deprecated | faceted/alpha · table |
| Automation | owner, runs_on→Agent?, touches→System[], governed_by→Policy?, trigger | manual→assisted→supervised→autonomous | board · board-by-status |
| Agent | owner, tools→System[], governed_by→Policy[], guardrails | manual→assisted→supervised→autonomous | alpha · board |
| Idea | owner, impact, effort, relates_to→any | proposed→accepted→building→live→retired | board-by-status |
| Incident | date, severity, involved→Agent\|System[], violated→Policy?, owner | open→mitigated→resolved→postmortem | date-desc · table |
| Role | person, reports_to→Role? | — | alpha · table |
| System | owner, vendor→Vendor?, criticality, access | active→deprecated | alpha · table |
| Policy | owner, applies_to | draft→active→deprecated | alpha · table |
| Vendor | owner, spend, contract_renewal(date) | — | alpha · table |
| Site (constellation) | url, purpose, steward | planned→live→retired | manual · table |
| Objective (OKR) | period, owner, key_results | on-track→at-risk→done | manual/period · board |

Shared-library types: `Decision · Review · Meeting · Procedure · Incident · Idea ·
Reference`. Admin-specific: `Automation · Agent · Role · System · Policy · Vendor ·
Site · Objective`.

## 10. Phased delivery

The design is complete above; implementation phases (each its own plan → build cycle).
SP1 + SP2 already ship the profile/type-library/`add-type`/`add-page`/`new-entry` engine,
so phasing re-anchors on *that*:

- **Phase A — Ship the `administration` profile on the existing engine (no new engine
  code).** Author the admin type fragments + `data/profiles/administration.toml` into the
  package (like `projecthub`), each type templated-or-section with a `landing`, so
  `zplus new x --profile administration` yields a serveable skeleton *today*. Mostly
  content authoring; it deliberately stress-tests where the current model is too thin
  (no fields/refs/status) and feeds Phase B.
- **Phase B — Extend the model → the typed graph & action surface.** Add `fields`/
  `order`/`status`/`views` to `DocType` and grow `VALID_SHAPES`; `ref` fields +
  backlinks/rollups; status workflows; `table`/`board`/`timeline` dashboards; the
  **Attention Feed**; faceted collections. Re-author the admin types to use them.
- **Phase C — Contract, batch, guided/AI onboarding.** `corpus.json` + `llms.txt`;
  `zplus check`; population modes 4–6 (one-shot flags, batch `--from`/`seed`, agent-led);
  interactive **Guided/Tailored `zplus new`** + **AI-oriented** (`--describe`, "let AI
  suggest"); `save-profile --to-package`. (`add-type`/`add-profile` already ship.)
- **Phase D — Later.** Standalone `add-section` + section-block **library**;
  cross-site/federated refs; `schema_version` migrations on `pip -U`; `graph` view;
  client-side interactivity.

All six population modes are *designed* here; A–C build them; only the standalone
`add-section`/section-block library and cross-site concerns defer to D.

## 11. Seams to protect now (not built here)

- **Schema versioning.** Each Type carries `schema_version`; `apply` reports drift after
  `pip install -U` rather than clobbering tailored types. (Field now; migrations in D.)
- **Cross-site / federated refs.** Refs are within-site; cross-site links are plain URLs
  for now, with room for a constellation-level index later.

## 12. Testing strategy

- **Unit:** manifest load/validate (incl. fields/refs/status/nav); `gen-nav` from
  manifest; ref resolution + backlink computation; Attention-Feed derivation from a
  fixture corpus; `check` catches dangling refs / missing fields / illegal status;
  slug / collision / section-shape (migrated from `test_new_entry.py`).
- **Integration:** `zplus new --profile administration` yields a tree that `zplus build`
  compiles clean; `add-entry` (each mode) produces a file that appears in the nav and in
  `corpus.json`; `add-collection` patches `zensical.toml` idempotently; `seed seed.yaml`
  stands up multiple collections+entries; `save-profile` round-trips (new → save → new
  from saved → identical).

## 13. Open questions

- Exact `corpus.json` schema (per-type JSONL vs. one document) — settle in Phase C.
- Whether `add-type` and `add-collection` are one verb (define + place) or two — settle
  when Phase C wires `add-type`.
- Which optional collections are on by default in Guided vs. offered — tune during
  Phase A seed authoring.
