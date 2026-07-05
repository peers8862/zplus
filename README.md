# zplus

A pip-installable toolkit of [Zensical](https://zensical.org) customizations for
new or existing sites. Doc types are data (a per-project `zplus.toml` manifest),
so the engine can be improved centrally (`pip install -U`) without touching your
content, and new doc types are just rows in a file.

## Install

```bash
pip install git+https://github.com/peers8862/zplus.git   # PyPI later
```

Runtime tools it calls: `zensical`, `node`/`npx` (for staticrypt encryption), `git`.

## Use

```bash
zplus profiles                     # list available site kinds
zplus new my-site --profile projecthub   # zensical new + apply the profile's types
cd my-site
zplus apply              # (re)apply/update in an existing project — idempotent
zplus new-entry --fill   # scaffold a dated entry; --fill prompts each section
zplus gen-nav            # regenerate the managed nav region from the manifest
zplus serve              # regenerate nav, then live-preview at :8000
zplus build              # build + AES-encrypt (staticrypt) into ./site
zplus deploy             # build + push encrypted site to the deploy branch
```

Set `SITE_PASSWORD` in `.env` and `[project].deploy_remote` in `zplus.toml`
before deploying.

## What `apply` does (idempotent)

Materializes `templates/`, `zplus.toml`, `.env(.example)` if absent; generates a
unique `.staticrypt.json` salt; adds a managed nav region to `zensical.toml` and
fills it from the manifest; adds a managed `.gitignore` block; removes the
plaintext `.github/workflows/docs.yml` auto-deploy.

## Profiles and types

Two levels, both data:

- **Types** are a reusable library (`data/types/<name>/` = a `[[type]]` def +
  its template). A type — e.g. `meeting` — can belong to many profiles.
- **Profiles** are site kinds (`data/profiles/<name>.toml`): an ordered list of
  type names. `projecthub` today; `administration`, `sales`, … are drop-in
  folders later.

`zplus new --profile <kind>` **resolves** a profile into a **self-contained**
project `zplus.toml` (full type defs, in order) plus editable templates — the
project no longer depends on the library, so your edits and `pip install -U`
never fight. The chosen profile is recorded in `[project].profile`.

## Manifest (`zplus.toml`)

Each doc type is a `[[type]]` with `name`, `label`, `folder`, `template`, and
`[[type.section]]` blocks (`heading`, `shape` = prose|list|task, optional
`prompt`). Edit a template's prose in `templates/<file>`; change a type's
structure here.

`zplus add-type` and `zplus add-profile` create new types/profiles interactively,
saved to your user library (`~/.config/zplus/`, overlaying the built-ins). See
`docs/GUIDE.md` §10 and `QUESTIONS.md`. Roadmap: resource generators (e.g. calendar
pages).
