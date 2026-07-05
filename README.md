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
zplus new my-site        # zensical new + apply the zplus overlay
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

## Manifest (`zplus.toml`)

Each doc type is a `[[type]]` with `name`, `label`, `folder`, `template`, and
`[[type.section]]` blocks (`heading`, `shape` = prose|list|task, optional
`prompt`). Edit a template's prose in `templates/<file>`; change a type's
structure here.

See `QUESTIONS.md` for decisions pending review. Roadmap: `zplus add-type`
(interactive type generator), resource generators (e.g. calendar pages).
