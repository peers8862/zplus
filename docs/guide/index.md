# The zplus Guide

**zplus** is a pip-installable toolkit for building [Zensical](https://zensical.org)
sites whose content is *structured data*, not just prose. You describe your doc types
once (in a `zplus.toml` manifest); zplus scaffolds the site, helps you and your AI agents
fill it, links the entries into a graph, and generates dashboards, an action feed, and a
machine-readable export on every build.

## Why it exists

zplus is built to grow a **constellation of company sites** that let humans run a
business *and* let it evolve into an **Automated Enterprise** — one whose changing
workings stay continuously documented, and therefore comprehensible to its human owners.
The first full profile, `administration`, is a company operating system: mission control
for running the whole enterprise.

The core idea: as you hand more work to automations and AI agents, you need to be able to
**trace what any of them is connected to** — what it runs, touches, and is governed by —
without maintaining those links by hand. zplus makes that mechanical.

## What it produces

From a set of typed entries, every build derives:

- **Dashboards** — each collection's landing renders a table of its entries and fields.
- **Boards** — a kanban-by-status view (e.g. the automation maturity ladder).
- **An Action Center** — a generated worklist of what needs attention (unowned entries,
  open items, broken links) across the whole site.
- **A graph page** — a mermaid diagram of how entries connect.
- **`corpus.json` + `llms.txt`** — a machine-readable export for local AI agents.

## Install

```bash
pip install git+https://github.com/peers8862/zplus.git
```

zplus shells out to `zensical` (the site builder), `node`/`npx` (staticrypt encryption),
and `git` at runtime.

## Read next

1. [Getting started](getting-started.md) — from install to a live site in two commands.
2. [Concepts](concepts.md) — the model: profiles, types, collections, fields, the graph.
3. [Authoring](authoring.md) — the ways to create and populate content.
4. [Fields & the graph](fields-and-graph.md) — typed data, refs, status workflows, `check`.
5. [Derived output](derived-output.md) — what the build generates.
6. [Profiles & tailoring](profiles-and-tailoring.md) — customize per enterprise.
7. [CLI reference](cli-reference.md) — every command.
8. [zplus & AI agents](for-ai-agents.md) — using the corpus with machines.
