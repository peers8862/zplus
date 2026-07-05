# zplus SP1 (foundation) — implementation plan

> Executed inline by Claude under Morgen's blanket authorization. TDD on the pure
> logic; integration-verified with a scratch Zensical project. Questions logged in
> `../QUESTIONS.md`.

**Goal:** A pip-installable `zplus` toolkit that brings the ABS Zensical
customizations into any project and is centrally updatable, with doc types driven
by a per-project `zplus.toml` manifest.

**Tech stack:** Python ≥3.11 (stdlib `tomllib`, `argparse`, `subprocess`),
hatchling build backend, `unittest`. Shells out to `zensical`, `npx staticrypt`,
`git` at runtime.

## File map

| File | Responsibility |
|---|---|
| `pyproject.toml` | Package metadata; `console_scripts` `zplus`, `new-entry`; bundles `data/**`. |
| `src/zplus/core.py` | Pure helpers: slugify, ordinals, collision, template stamping, fill-body formatting. |
| `src/zplus/manifest.py` | Load/validate `zplus.toml` → `Manifest`/`DocType`/`Section`. |
| `src/zplus/patch/toml_nav.py` | Ensure zensical.toml settings + managed nav region (string-level, preserves comments). |
| `src/zplus/patch/gitignore.py` | Ensure the managed `.gitignore` block (idempotent). |
| `src/zplus/commands/nav.py` | `gen-nav`: regenerate managed nav region from manifest + `docs/`. |
| `src/zplus/commands/entry.py` | `new-entry`: manifest-driven entry creator (scaffold + `--fill`). |
| `src/zplus/commands/apply.py` | Idempotent overlay/update: materialize, patch, secrets, cleanup. |
| `src/zplus/commands/new.py` | `zensical new` → `apply`. |
| `src/zplus/commands/site.py` | `serve`/`build`/`deploy` (migrated from `build.sh`). |
| `src/zplus/cli.py` | argparse subcommand dispatch (extensible for SP2 `add-type`). |
| `src/zplus/data/` | Seed `templates/`, `overrides/`, `env.example`, `zplus.default.toml`. |
| `tests/` | Unit tests for core, manifest, nav, patch. |

## Tasks (each ends testable)

1. **Pure core** (`core.py` + `test_core.py`) — migrate slug/ordinals/collision/stamp/fill-formatting from the hub's `new_entry.py`; all unit-tested.
2. **Manifest** (`manifest.py` + `test_manifest.py`) — dataclasses + `load()`; author `data/zplus.default.toml` for the 8 types.
3. **Patchers** (`patch/*.py` + `test_patch.py`) — idempotent zensical.toml settings/nav-region + `.gitignore` block.
4. **gen-nav** (`commands/nav.py` + `test_nav.py`) — build managed region from manifest, splice into toml.
5. **entry** (`commands/entry.py`) — manifest-driven interactive creator; reuses `core`.
6. **apply / new / site** (`commands/*.py`) — overlay, project creation, migrated build/deploy.
7. **CLI + packaging** (`cli.py`, `pyproject.toml`) — dispatch + console scripts.
8. **Integration** — `pip install -e .` into a venv with `zensical`, run `zplus apply` on a scratch `zensical new` project, `zplus build` → no issues, `new-entry` → appears in nav.

## Out of scope (SP2/SP3): `add-type`, resource generators, PyPI publish.
