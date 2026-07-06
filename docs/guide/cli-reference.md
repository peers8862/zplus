# CLI reference

Every command runs in a zplus project directory (one containing a `zplus.toml`), except
`new`, which creates one.

## Project lifecycle

| Command | Does |
|---|---|
| `zplus new <name> [--profile P]` | Create a Zensical project and apply a profile (default `projecthub`). |
| `zplus apply [--profile P]` | Re-apply/update zplus in the current project — idempotent; safe after `pip install -U`. |
| `zplus profiles` | List available profiles (bundled ∪ user). |

## Authoring content

| Command | Does |
|---|---|
| `zplus new-entry` | Scaffold a templated entry and open `$EDITOR`. |
| `zplus new-entry --fill` | Guided wizard: prompt each field and section. |
| `zplus new-entry --type T --title "…" --set k=v …` | One-shot, non-interactive creation. |
| `zplus new-entry --type T --title "…" --like SLUG` | Clone field values from an existing entry. |
| `zplus new-entry --type T --from FILE` | Batch-create from a CSV/YAML file. |
| `zplus new-entry --date YYYY-MM-DD` | Set the entry date (one-shot). |
| `zplus jot "text" [--type NAME]` | Quick-capture a draft entry (default type `idea`). |
| `zplus add-page` | Add a plain page to a non-templated section type. |

Fields on `--set`: repeatable; `k=v`; a value with `|` becomes a list
(`--set touches="a|b"`). `--from` requires `--type`.

## Defining types & profiles

| Command | Does |
|---|---|
| `zplus add-type` | Interactively define a new type → user library. |
| `zplus add-profile` | Interactively compose a profile from library types → user library. |

## Generating & checking

| Command | Does |
|---|---|
| `zplus gen-nav` | Regenerate the managed nav region in `zensical.toml` from the manifest. |
| `zplus gen-derived` | Regenerate dashboards, boards, the Action Center, the graph page, `corpus.json`, `llms.txt`. |
| `zplus check` | Lint the corpus: broken refs, missing required fields, invalid enums. Exit non-zero on problems. |

## Building & deploying

| Command | Does |
|---|---|
| `zplus serve` | `gen-derived` + `gen-nav`, then live-preview at `:8000` (unencrypted). |
| `zplus build` | `gen-derived` + `gen-nav` + `zensical build`, then AES-encrypt (staticrypt) into `./site`. Requires `SITE_PASSWORD` in `.env`. |
| `zplus deploy` | `build`, then force-push the encrypted `site/` to `[project].deploy_remote` on `[project].deploy_branch` (default `gh-pages`). |

## Environment & config

- **`.env`** — `SITE_PASSWORD` (required to build), optional `GIT_NAME` / `GIT_EMAIL` for deploys.
- **`zplus.toml` `[project]`** — `profile`, `managed_nav`, `deploy_branch`, `deploy_remote`.
- **`$ZPLUS_HOME`** — user library location (default `~/.config/zplus/`).

`new-entry` is also exposed as a bare `new-entry` console command for parity with older
setups.
