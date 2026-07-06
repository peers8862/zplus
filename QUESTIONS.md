# zplus — open questions for Morgen

Decisions I made autonomously while building SP1. None block the build; each is a
place we can revisit. Newest at the bottom.

| # | Topic | Decision I made | Why / revisit if… |
|---|---|---|---|
| 1 | **Deploy remote URL** | `build.sh` hardcoded `peers8862/abs-project-hub-zensical`. In the package it can't be hardcoded, so `zplus deploy` reads `[project].deploy_remote` from the project's `zplus.toml`. Each project sets its own. | Revisit if you'd rather auto-detect from a git remote, or keep it in `.env`. |
| 2 | **staticrypt salt** | `zplus apply` generates a **fresh unique** `.staticrypt.json` salt per project if absent, never copies one. | Sharing a salt across sites weakens the gate; this is deliberate. |
| 3 | **Nav consolidation** | The scattered per-type markers become **one managed region** (`# >>> ZPLUS_TYPES >>> … <<<`) regenerated from the manifest. One-time reshuffle of a project's nav order. | You approved this in the spec; revisit if you want per-type placement back. |
| 4 | **Fill-mode section shape** | Taken from the manifest (`shape = prose|list|task`) when the section is defined there; falls back to detecting it from the template body otherwise. | Manifest is authoritative; templates stay the scaffold source. |
| 5 | **Python floor 3.11** | Package requires Python ≥ 3.11 (uses stdlib `tomllib`). New projects' venvs must be 3.11+. | Revisit if you need to support older Python (would add a `tomli` dep). |
| 6 | **Upgrades don't overwrite content** | `zplus apply` materializes `templates/`, `overrides/`, `zplus.toml` **only if absent** — it never clobbers your edits. So a `pip install -U` that ships *new* default templates won't auto-appear in existing projects. | Revisit: we may want `zplus apply --refresh-templates` to pull new defaults on demand. |
| 7 | **Deploy config in manifest** | `[project]` in `zplus.toml` holds `deploy_remote`, `deploy_branch` (default `gh-pages`), and `managed_nav` (region name). | Revisit the split between `zplus.toml` and `.env` for deploy settings. |
| 8 | **Branding-neutral** | zplus is a *general* tool, so it does NOT ship theme overrides, logos, favicons, or announce banners — the hub's `overrides/main.html` ("Welcome to the ABS Project Hub") was dropped. `apply` no longer forces `custom_dir`/`extra_css`; a site sets its own branding. | Revisit if you want zplus to optionally scaffold a neutral `overrides/` starter. |
| 9 | **Empty doc-type folders** | `gen-nav` skips a type whose `docs/<folder>/` has no files (no empty `{ "Label" = [] }` in nav). A fresh project's managed region is empty until you create entries. | Revisit: `apply` could instead scaffold an `index.md` landing per type folder. |
| 10 | **Deploy git identity** | `build.sh` hardcoded your name/email. `zplus deploy` now reads `GIT_NAME`/`GIT_EMAIL` from `.env` (defaults `zplus`/`zplus@localhost`). | Revisit: prefer the machine's global git config, or make it required config. |
| 11 | **Encrypt/deploy not re-exercised** | `zplus build`'s staticrypt step and `zplus deploy`'s git push are faithful ports of your working `build.sh` (incl. the `rm -rf .git` fix), but this session verified only up to `zensical build` (no `npx`/remote here). First real `zplus deploy` should be watched. | — |
| 12 | **`new-entry` also standalone** | Exposed both as `zplus new-entry` and a bare `new-entry` console command (parity with your current wrapper). | Drop the bare command if you prefer only `zplus new-entry`. |
| 13 | **Profiles + type library (self-contained)** | Types are a reusable library (`data/types/<name>/`); profiles (`data/profiles/<name>.toml`) are ordered type-name lists. `zplus new --profile <kind>` resolves a profile into a self-contained project `zplus.toml` (full defs, editable) + templates; the profile is recorded in `[project].profile`. Only `projecthub` exists so far. | Confirmed self-contained. `administration`/`sales` are future drop-in folders — their sections are still to be conceived. |
| 14 | **SP2 authoring → user library** | `add-type`/`add-profile` write to a **user library** at `$ZPLUS_HOME` (default `~/.config/zplus/`), NOT the pip-installed package. The engine reads bundled ∪ user (user wins on name clash). | Package stays read-only; the toolkit maintainer edits the package source separately to change built-ins. Revisit if you want a `--to-package` dev flag. |
| 15 | **Generated template shape** | `add-type` generates `template.md`: front matter (date/title), H1 `"<Name> title — YYYY-MM-DD"` (name capitalized), and each section as `## heading` + a `-`/`- [ ]` placeholder (list/task) or the prompt text (prose). | Revisit the title wording (singularization) and default placeholders. |
| 16 | **add-type/add-profile interactive-only** | Both are interactive prompts (no CLI flags for non-interactive/scripted creation yet). | Revisit if you want `--section`/`--types` flags for scripting or automation. |
| 17 | **Two kinds of type + `add-page`** | Types have a `templated` flag: **templated** (dated entries via `new-entry`) vs **section** (non-templated nav folders whose plain pages come from `zplus add-page` — name + optional text blocks). Any type may carry `landing` text → the folder's `index.md` on apply. `new-entry` lists templated only; `add-page` lists sections only. Templated nav orders newest-first; sections order A→Z. | — |
| 18 | **projecthub mirrors the ABS hub nav** | The `projecthub` profile now reproduces the full ABS-hub top nav: 7 non-templated sections (Project Hub · Spokes · Phases · Work · Docs · AI · $) + the 8 templated logs, in ABS order. All 15 carry a brief one-line `landing` so a fresh site shows the whole nav skeleton immediately. | Landings are generic placeholders — edit per site. Revisit the section→folder mapping (e.g. "Project Hub" → folder `project-hub`). |

---

## Design-stage — profiles & authoring

From the forward architecture spec `docs/design-profiles-and-authoring.md` (2026-07-06),
reconciled with shipped SP1/SP2. These are *not yet built* — they update items above and
add open questions to settle before/within the phase that builds each.

**Prior items the design now addresses:**

- **#13** — `administration` sections are now conceived: design §9 defines the full nav +
  14 types. It ships as a **bundled** profile authored into `data/` like `projecthub`.
- **#14** — the `save-profile` "dogfood a live site → ship it" path *depends on* a
  `--to-package` flag; promoted from "revisit if" to a planned Phase-C item.
- **#16** — non-interactive/scripted authoring (flags) becomes a first-class requirement
  (population modes 4–5); planned Phase C.
- **#9 / #17** — empty-folder handling is considered resolved: every collection carries a
  `landing`, so a fresh site shows the skeleton; the design assumes this.

**New open questions (design-stage):**

| # | Topic | Question / proposed default | Phase |
|---|---|---|---|
| 19 | Field type system | Add `fields` to `[[type]]` (`text/enum/multi-enum/date/number/bool/owner/status/ref`), stored in entry front-matter. OK to grow the `Section`/`DocType` dataclasses + `VALID_SHAPES` (add table/fields/diagram/callout/links)? | B |
| 20 | `ref` = graph edges | Refs point at entries by slug; `zplus check` fails on dangling; backlinks/rollups computed at build. Confirm **within-site only** for now (cross-site = plain URLs). | B |
| 21 | `order` generalizes `templated` | Introduce `order = date-desc\|alpha\|manual\|status`, with `templated` kept as shorthand (true≈date-desc). Acceptable, or keep the bool? | B |
| 22 | Status workflows | Model `status` as a per-type state machine (the maturity ladder etc.). Where does the workflow definition live — in the type fragment `type.toml`? | B |
| 23 | Attention Feed | One generated page from status + staleness + missing-owner across all collections. What are the default "needs attention" rules (e.g. review cadence source)? | B |
| 24 | corpus.json + staticrypt | Emit `corpus.json` / `llms.txt` beside the HTML, **unencrypted** (same bucket as today's `search.json`). Accept the disclosure trade per site? | C |
| 25 | AI onboarding boundary | `zplus new --describe` / "let AI suggest" proposes a profile + seed entries. How much does the CLI call a model vs. stay deterministic with an optional AI step (which model/key)? | C |
| 26 | save-profile → package | Ship a `--to-package` dev flag (write a profile into package source, not the user library), or keep built-in profiles hand-authored? | C |

**Phase A landed (2026-07-06).** The `administration` profile stands up cleanly:
`zplus new x --profile administration` → 22 landings + 9 templates, the managed nav lists
all 22 sections in grouped order, and `zensical build` reports "No issues found." Rough
edges that motivate Phase B, as predicted: the nav is a flat 22-item list (no
grouping/nesting); the reused `meeting` type sits under `work/meetings` (folder mismatch
with the flat admin folders, cf. #18); and there are no typed fields/refs/status yet.
