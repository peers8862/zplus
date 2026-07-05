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
