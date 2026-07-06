# zplus

A pip-installable toolkit for building [Zensical](https://zensical.org) sites whose
content is **structured data**, not just prose. Doc types are declared once in a
per-project `zplus.toml` manifest; zplus scaffolds the site, helps you (and your AI agents)
fill it, links entries into a graph via typed `ref` fields, and generates dashboards, an
action feed, and a machine-readable export on every build.

## 📖 Guide

Full documentation lives in **[`docs/guide/`](docs/guide/index.md)**:

- [Getting started](docs/guide/getting-started.md) · [Concepts](docs/guide/concepts.md) ·
  [Authoring](docs/guide/authoring.md) · [Fields & the graph](docs/guide/fields-and-graph.md)
- [Derived output](docs/guide/derived-output.md) ·
  [Profiles & tailoring](docs/guide/profiles-and-tailoring.md) ·
  [CLI reference](docs/guide/cli-reference.md) · [zplus & AI agents](docs/guide/for-ai-agents.md)

## Install

```bash
pip install git+https://github.com/peers8862/zplus.git   # PyPI later
```

Runtime tools it calls: `zensical`, `node`/`npx` (staticrypt encryption), `git`.

## Quick start

```bash
zplus profiles                                # list site kinds (administration, projecthub)
zplus new my-company --profile administration # scaffold a complete, seeded site
cd my-company
zplus new-entry --fill                        # add an entry (wizard prompts fields + sections)
zplus check                                   # lint the corpus (broken refs, missing fields)
zplus serve                                   # regenerate everything, preview at :8000
```

## What you get

From a set of typed entries, every build derives — automatically, from one in-memory
corpus:

- **Dashboards** on each collection landing, **boards** (kanban by status), and **facets**;
- an **Action Center** worklist (unowned entries, open items, broken links) across the site;
- a **mermaid graph page** of how entries connect;
- **`corpus.json` + `llms.txt`** — a machine-readable export for local AI agents (kept out
  of the published site).

## How it fits together

- **Profiles** (`administration`, `projecthub`) are named starter bundles resolved into a
  self-contained, editable `zplus.toml` — upgrades never overwrite your content.
- **Types** are a reusable library (`data/types/<name>/`), templated (dated logs) or
  section (curated pages); `zplus add-type` / `add-profile` extend your user library at
  `~/.config/zplus/`.
- **Fields** (incl. `ref`) make entries a queryable graph; `zplus check` keeps it valid.

See the [guide](docs/guide/index.md) for everything. Design docs and the decision log are
in [`docs/`](docs/) and [`QUESTIONS.md`](QUESTIONS.md).
