# zplus — Guide

zplus is a pip-installable toolkit of [Zensical](https://zensical.org)
customizations. It turns a plain Zensical project into a password-protected site
with a **manifest-driven doc-type system**, and it can bring the same setup to
**new or existing** sites. Because the toolkit is a package, improving it centrally
(`pip install -U`) updates every project.

This guide covers the mental model, install, every command, the manifest format,
day-to-day workflows, publishing, updating, and extending. Sections marked
_(coming in SP2)_ are placeholders for the type/profile generators.

---

## 1. Mental model

Three layers, from most general to most specific:

| Layer | What it is | Where it lives |
|---|---|---|
| **Profile** (site kind) | an ordered list of types that defines a *kind* of site (`projecthub`, later `administration`, `sales`) | package: `data/profiles/<name>.toml` |
| **Type** (doc type) | a reusable section/template (`challenge`, `meeting`, …); can belong to many profiles | package library: `data/types/<name>/` |
| **Manifest** (`zplus.toml`) | a project's **self-contained** resolved copy — the full type defs for *this* site, in order | the project |

Key idea: **types and profiles are authoring-side (in the package); a project is
self-contained.** `zplus new --profile projecthub` *resolves* the profile — copies
the chosen types' full definitions and templates into the project — so your edits
and a `pip install -U` never fight. The engine (entry creator, nav generator,
build/deploy) only ever reads a project's resolved `zplus.toml`.

Split of responsibilities:

- **In the package (updated by pip):** all logic + the type library + profiles.
- **In the project (yours to edit):** `zplus.toml`, `templates/`, your content,
  `.env`, `.staticrypt.json`.

---

## 2. Requirements & install

Runtime tools zplus calls as subprocesses:

- **Python ≥ 3.11** (the venv zplus is installed into)
- **`zensical`** — the site generator
- **`node` / `npx`** — for staticrypt page encryption (build/deploy)
- **`git`** — for deploy

Install into your project's virtual environment:

```bash
pip install git+https://github.com/peers8862/zplus.git    # PyPI later
```

This provides two console commands: **`zplus`** and a bare **`new-entry`** (an
alias for `zplus new-entry`).

---

## 3. Commands

| Command | What it does |
|---|---|
| `zplus profiles` | List available profiles (site kinds). |
| `zplus new <name> [--profile <p>]` | `zensical new <name>`, then apply the profile (default `projecthub`). |
| `zplus apply [--profile <p>]` | Idempotent overlay + **update**. On an existing project it reuses the recorded profile. Safe to re-run after `pip install -U`. |
| `zplus new-entry [--fill]` | Scaffold a dated entry from a type's template. `--fill` prompts each section at the terminal. |
| `zplus gen-nav` | Regenerate the managed nav region in `zensical.toml` from the manifest. (Run automatically by serve/build/deploy.) |
| `zplus serve` | `gen-nav` → `zensical serve` (live preview at http://localhost:8000). |
| `zplus build` | `gen-nav` → `zensical build --clean` → AES-encrypt every page (staticrypt) into `./site`. |
| `zplus deploy` | `build`, then force-push the encrypted `site/` to the deploy branch. |

---

## 4. What `zplus apply` does

Run by `zplus new`, and re-runnable any time (idempotent — it never overwrites
existing content):

1. **`zplus.toml`** — if absent, resolve the profile into a self-contained manifest.
2. **`templates/`** — copy each type's library template in, if absent.
3. **`.env.example` and `.env`** — seed from the package (set `SITE_PASSWORD`!).
4. **`.staticrypt.json`** — generate a **unique** encryption salt if absent (never shared).
5. **`zensical.toml`** — add the managed nav region and fill it from the manifest.
6. **`.gitignore`** — add a managed block (`site/`, `.env`, `.venv/`, salt, …).
7. **`.github/workflows/docs.yml`** — remove it (the plaintext auto-deploy conflicts
   with the encrypted model).

---

## 5. The manifest (`zplus.toml`)

A project's self-contained doc-type definition:

```toml
[project]
profile       = "projecthub"      # which site kind this was resolved from
managed_nav   = "ZPLUS_TYPES"     # name of the managed nav region in zensical.toml
deploy_branch = "gh-pages"
deploy_remote = "https://github.com/you/your-repo.git"   # set before `zplus deploy`

[[type]]
name     = "challenge"            # unique key; also the library folder name
label    = "Challenges"           # nav section title
folder   = "business-challenges"  # under docs/
template = "challenge.md"         # under templates/
  [[type.section]]
  heading = "The issue"
  shape   = "prose"               # prose | list | task
  prompt  = "The focused problem — what's slow, manual, painful, or missing."
  # … one block per section …
```

- **Edit a template's prose** in `templates/<file>`.
- **Change a type's structure** (sections, folder, label, order) here.
- **Reorder types** by reordering the `[[type]]` blocks — that reorders the nav.

### Section shapes

`shape` controls how `--fill` formats your input:

- `prose` — lines kept as-is
- `list` — each line becomes a `- ` bullet
- `task` — each line becomes a `- [ ]` checkbox

---

## 6. Templates

A template is a Markdown scaffold:

```markdown
---
date: YYYY-MM-DD
title: Challenge title
---
# Challenge title — YYYY-MM-DD

## The issue
The focused problem — what's slow, manual, painful, or missing.
```

`new-entry` substitutes the real date and title into the front matter and H1. The
`## ` headings and their hint text are the scaffold you write into. Front-matter
list fields (`attendees:` for meetings, `tags:` for timelines) are prompted in
fill mode automatically.

---

## 7. Everyday workflows

### Create a new site

```bash
zplus new my-site --profile projecthub
cd my-site
# set a password:
sed -i 's/change-me/your-real-password/' .env      # or edit .env
zplus serve                                          # preview at :8000
```

### Author an entry

```bash
zplus new-entry            # pick a type by number, title, date → opens your editor
zplus new-entry --fill     # …and answer each section at the terminal first
```

Fill-mode typing: **Enter** commits a line (next bullet/line); **Enter on an empty
line** finishes the section and moves on. No Ctrl/modifier keys. Same-day,
same-title entries get a `-TWO`, `-THREE`, … suffix on the filename and a `(TWO)`
on the heading so the nav stays distinct.

### Preview

```bash
zplus serve       # regenerates nav first, so new entries appear in the sidebar
```

Always prefer `zplus serve` over a raw `zensical serve` — the raw command skips
nav regeneration, so new entries won't show.

---

## 8. Publishing (encrypted)

The published site is **password-protected**: staticrypt AES-encrypts every page
and injects a password prompt. There is no server — the gate lives in the files.

```bash
# one-time per project:
#   .env            → SITE_PASSWORD=...          (never committed)
#   zplus.toml      → [project].deploy_remote = "https://github.com/you/repo.git"

zplus deploy      # build → encrypt → force-push encrypted site/ to gh-pages
```

Then set the repo's **GitHub Pages source** to **Deploy from a branch → `gh-pages`
→ `/root`**. The password lives only in `.env` and each reader's browser.

**Deploy notes**
- Each deploy uses a fresh throwaway git repo inside `site/` and force-pushes, so
  repeat deploys never collide.
- If a GitHub Pages build wedges ("Deployment failed, try again later"), re-trigger
  it; if it stays stuck, toggle Settings → Pages source off/on.

---

## 9. Updating a project

```bash
pip install -U <zplus>     # or: pip install -U git+https://github.com/peers8862/zplus.git
zplus apply                # re-patch config; reuses the recorded profile
```

**Caveat:** `apply` never overwrites existing content, so if an upgrade ships *new*
default templates, they won't auto-appear in a project that already has a
`templates/` folder. (Tracked — a `--refresh-templates` option is a likely
addition. See `QUESTIONS.md`.)

---

## 10. Extending

### A one-off type for a single site (works today, by hand)

Add a `[[type]]` block to that project's `zplus.toml` and drop a matching template
in `templates/`. The engine reads it immediately; `apply` won't touch your
hand-written template.

### A reusable type or a new profile (in the package)

- **New type:** add `data/types/<name>/type.toml` (a `[[type]]` fragment) +
  `data/types/<name>/template.md`.
- **New profile:** add `data/profiles/<name>.toml` with `label` and an ordered
  `types = [...]` list referencing library types.

No engine changes are needed — adding a site kind is a drop-in folder.

> _(coming in SP2)_ `zplus add-type` and `zplus add-profile` will make the two
> package-authoring actions above interactive — name a type, define its
> sections/prompts; name a profile, pick and order its types — instead of writing
> the files by hand.

---

## 11. Layout reference

**Package (the zplus repo):**

```
src/zplus/
  cli.py                     # subcommand dispatch
  core.py                    # slug / collision / stamping / fill formatting
  manifest.py                # load + validate + profile resolution
  paths.py                   # bundled-data access
  patch/{toml_nav,gitignore} # idempotent config patchers
  commands/{new,apply,entry,nav,site}
  data/
    env.example
    types/<name>/{type.toml, template.md}   # the type library
    profiles/<name>.toml                     # site kinds
```

**A configured project:**

```
zensical.toml     # patched: managed nav region
zplus.toml        # your self-contained manifest
templates/*.md    # editable
.env              # SITE_PASSWORD (gitignored)
.staticrypt.json  # unique salt (gitignored)
docs/             # your content
```

---

## 12. Pointers

- **`QUESTIONS.md`** — decisions made during the build that are open to revisit.
- **Roadmap:** SP2 = `add-type` / `add-profile` generators; SP3 = resource
  generators (e.g. calendar feeds → an auto-built "Cal" page).
