# Commands guide

A task-oriented walkthrough: from an empty machine to a live site, then every command
explained in the order you'd reach for it. For a terse lookup table, see the
[CLI reference](cli-reference.md).

---

## Prerequisites

zplus orchestrates other tools, so you need on your system:

- **Python 3.11+**
- **`zensical`** — the static-site builder zplus drives (installed below)
- **`node` / `npx`** — only for encrypted builds (`build` / `deploy`) via staticrypt
- **`git`** — only for `deploy`

The one rule that trips people up: **`zplus` and `zensical` must be on the same `PATH`**,
because `zplus new` shells out to `zensical`. The simplest way to guarantee that is to
install both into one virtual environment and activate it.

---

## Install (one-time)

```bash
python3 -m venv ~/.venvs/zplus
source ~/.venvs/zplus/bin/activate         # activate → both tools are on PATH
pip install zensical
pip install git+https://github.com/peers8862/zplus.git
```

Open a new shell later? Re-activate with `source ~/.venvs/zplus/bin/activate`. (If you
prefer `pipx`, run `pipx install zensical` **and** `pipx install …zplus…` so both bins are
exposed.)

To upgrade later:

```bash
pip install -U git+https://github.com/peers8862/zplus.git
zplus apply        # re-patch config + pull any new defaults; your content is preserved
```

---

## The journey (start to published)

```bash
# 1. create a new site in a new folder, from a profile
cd ~/projects
zplus new my-company --profile administration
cd my-company

# 2. preview it right now (no password needed — unencrypted local preview)
zplus serve                                 # http://localhost:8000 ; Ctrl-C to stop

# 3. add content
zplus new-entry --fill                      # guided wizard
zplus jot "automate the monthly close"      # quick draft

# 4. validate + preview again
zplus check
zplus serve

# 5. publish
#    - put a real SITE_PASSWORD in .env
#    - set [project].deploy_remote in zplus.toml
zplus build                                 # encrypt into ./site
zplus deploy                                # push encrypted site to gh-pages
```

Everything below elaborates each step and the commands you didn't see here.

---

## Creating & updating a project

### `zplus new <name> [--profile P]`
Creates a new folder `<name>` (via `zensical new`) and applies a profile to it. `--profile`
defaults to `projecthub`; use `administration` for the company-OS profile. Afterwards the
project is **self-contained** — its `zplus.toml` holds full type definitions, so your edits
and future `pip install -U` never fight.

```bash
zplus new my-company --profile administration
```

What you get: `zplus.toml`, editable `templates/`, a landing `index.md` for every section,
a wired nav region in `zensical.toml`, a `.env` (placeholder password), a unique
`.staticrypt.json` salt, and a managed `.gitignore` block.

### `zplus apply [--profile P]`
The idempotent overlay/update step — safe to run any time, and especially after upgrading
the package. It materializes missing `templates/` / `zplus.toml` / `.env`, ensures the
managed nav region and `.gitignore` block, generates the salt if absent, and removes the
plaintext `.github/workflows/docs.yml` auto-deploy. It never overwrites your content.
`zplus new` runs it for you; call it directly on an existing project after `pip install -U`.

### `zplus profiles`
Lists the available profiles (bundled ∪ your user library).

```bash
zplus profiles      # administration, projecthub, …
```

---

## Adding content

The workhorse is `zplus new-entry`, which has several input modes. There's also `jot` for
quick capture and `add-page` for section pages.

### `zplus new-entry` — scaffold + edit
With no flags: pick a templated type, give a title/date, and it stamps the template and
opens your `$EDITOR`. Best for prose-heavy entries.

### `zplus new-entry --fill` — guided wizard
Prompts **every declared field** (enums/status as numbered pick-lists, `ref`s as
pick-from-existing-entries), then each section. The friendliest way to keep the graph
connected, because refs are chosen from real entries.

### `zplus new-entry --type T --title "…" --set k=v` — one-shot
Fully non-interactive; no editor. Repeat `--set` per field; a value with `|` becomes a
list. This is the mode scripts and **AI agents** use.

```bash
zplus new-entry --type agent --title "Invoice Bot" \
  --set owner=steve --set status=supervised \
  --set runs=invoice-import --set governed_by=financial-controls
```

Add `--date YYYY-MM-DD` to override the entry date.

### `zplus new-entry --type T --title "…" --like SLUG` — clone
Seeds the new entry's field values from an existing entry, then applies any `--set`
overrides. Good for near-duplicates.

### `zplus new-entry --type T --from FILE` — batch
Creates one entry per row of a CSV (or YAML list). Header = column names; `title` required,
`date` optional; other columns become front-matter values (`|` splits lists).

```bash
# systems.csv:  title
#               Billing
#               Payroll
zplus new-entry --type system --from systems.csv     # stands up a registry in one call
```

### `zplus jot "text" [--type NAME]`
Friction-free quick-capture: creates a draft entry titled from the first words of the text,
with the text as the body. Defaults to the `idea` type. Triage/flesh it out later.

### `zplus add-page`
Adds a **plain page** to a non-templated *section* type (e.g. Roles, Systems, How We Run).
Interactive: pick the section, give a name, optionally paste an opening block. (Templated
types use `new-entry`; section types use `add-page`.)

---

## Defining types & profiles

These extend your **user library** at `$ZPLUS_HOME` (default `~/.config/zplus/`); the
installed package is never edited in place, and user entries win on a name clash.

### `zplus add-type`
Interactively define a new doc type — its label, folder, whether it's templated, its
sections, and its fields. Writes the type to your user library and a starter template.

### `zplus add-profile`
Interactively compose a new profile from library type names. Writes a
`profiles/<name>.toml` to your user library; it's then usable via `zplus new --profile`.

---

## Regenerating & checking

### `zplus gen-nav`
Regenerates the managed nav region in `zensical.toml` from the manifest — newest-first for
templated types, A→Z by title for section types (or a type's explicit `order`). Runs
automatically inside `serve`/`build`; call it after hand-editing `zplus.toml`.

### `zplus gen-derived`
Regenerates all derived content from the corpus: dashboards (into landings), boards, facet
groupings, the Action Center (`mission-control/action-center.md`), the graph page
(`mission-control/graph.md`), and `corpus.json` + `llms.txt` at the project root. Only ever
writes tool-owned files. Runs automatically inside `serve`/`build`.

### `zplus check`
Lints the whole corpus and exits non-zero on any problem — dangling/mis-typed refs, empty
required fields, values outside a field's `values`. Run it before committing or in CI.

```bash
zplus check
# ✔ corpus OK: 42 entries
```

---

## Running & publishing

### `zplus serve`
Runs `gen-derived` + `gen-nav`, then serves an **unencrypted** local preview at
`http://localhost:8000`. Replaces the shell process — press `Ctrl-C` to stop. No password
required.

### `zplus build`
Runs `gen-derived` + `gen-nav` + `zensical build`, then **AES-encrypts** every page with
staticrypt into `./site`. Refuses to run unless `SITE_PASSWORD` is set in `.env` (fail
closed). Needs `node`/`npx`. `corpus.json` and `llms.txt` live at the project root and are
*not* included in `./site`.

### `zplus deploy`
Runs `build`, then force-pushes the encrypted `site/` to your deploy branch. Requires
`[project].deploy_remote` in `zplus.toml`; branch defaults to `gh-pages`. Uses
`GIT_NAME`/`GIT_EMAIL` from `.env` for the commit identity.

---

## Configuration

### `.env` (gitignored)
```
SITE_PASSWORD=your-password      # required for build/deploy
GIT_NAME=Your Name               # optional; used by deploy's commit
GIT_EMAIL=you@example.com        # optional
```

### `zplus.toml` `[project]`
```toml
[project]
profile = "administration"       # recorded at scaffold time
managed_nav = "ZPLUS_TYPES"      # name of the managed nav region in zensical.toml
deploy_branch = "gh-pages"       # deploy target branch
deploy_remote = "https://github.com/you/my-company.git"   # set before `zplus deploy`
```

### `$ZPLUS_HOME`
Where `add-type` / `add-profile` write (default `~/.config/zplus/`). Overlays the bundled
library.

---

## Recipes

**Stand up a site and preview**
```bash
zplus new my-company --profile administration && cd my-company && zplus serve
```

**Bulk-seed a registry**
```bash
# prepare a CSV with a `title` column (+ any field columns), then:
zplus new-entry --type system --from systems.csv
zplus check && zplus serve
```

**Daily authoring loop**
```bash
zplus new-entry --fill        # or --set / jot
zplus check
zplus serve
```

**Publish**
```bash
# edit .env (SITE_PASSWORD) and zplus.toml ([project].deploy_remote) once
zplus build      # verify ./site locally
zplus deploy
```

**Upgrade the toolkit**
```bash
pip install -U git+https://github.com/peers8862/zplus.git
zplus apply
```

---

## Troubleshooting

- **`FileNotFoundError: 'zensical'` from `zplus new`** — `zensical` isn't on `PATH`.
  Activate the venv that has both tools (`source ~/.venvs/zplus/bin/activate`).
- **`error: SITE_PASSWORD not set`** — put it in `.env` before `build`/`deploy`. `serve`
  doesn't need it.
- **`error: set [project].deploy_remote …`** — add your repo URL to `zplus.toml` before
  `deploy`.
- **New entries don't show in the nav** — they appear after `gen-nav`, which runs inside
  `serve`/`build`; run `zplus gen-nav` if you built by another path.
- **First `deploy`** — the encrypt + push path is a faithful port but least-exercised; watch
  your first real deploy.
