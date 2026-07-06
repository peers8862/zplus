# Getting started

## Install

```bash
pip install git+https://github.com/peers8862/zplus.git
```

You also need `zensical` on your `PATH` (zplus calls it to build/serve), plus `node`/`npx`
for encrypted builds and `git` for deploys.

## Create a site (the express path)

One command scaffolds a complete, seeded, ready-to-serve site from a **profile**:

```bash
zplus new my-company --profile administration
cd my-company
zplus serve          # regenerates nav + derived content, then serves at :8000
```

`zplus new` runs `zensical new`, then applies the profile: it writes a self-contained
`zplus.toml`, materializes editable `templates/`, creates a landing page for every
section, and wires the navigation. No further questions — you have a running site.

See the available profiles with:

```bash
zplus profiles       # e.g. administration, projecthub
```

## Add your first entry

Collections (Meetings, Decisions, Agents, …) grow one entry at a time. The interactive
wizard prompts each field and section:

```bash
zplus new-entry --fill
```

Pick a type, give it a title, and the wizard walks you through its fields (picking from
enum lists, choosing existing entries for references) and its sections. When you save, the
entry is a correctly-named, front-matter-complete markdown file.

Prefer to type it all at once? Use one-shot flags:

```bash
zplus new-entry --type agent --title "Invoice Bot" \
  --set owner=steve --set status=supervised --set runs=invoice-import
```

## See the derived output

```bash
zplus gen-derived    # dashboards, boards, action center, graph, corpus.json, llms.txt
zplus check          # lint the corpus (broken refs, missing required fields, bad enums)
zplus serve          # gen-derived + gen-nav run automatically before serving
```

Open <http://localhost:8000> — each collection's landing shows a dashboard, Mission
Control has an **Action Center** and a **Graph** subpage, and everything is linked.

## Build & deploy

```bash
# .env must contain SITE_PASSWORD (builds refuse to run unprotected)
zplus build          # build + AES-encrypt (staticrypt) into ./site
zplus deploy         # build + push the encrypted site to your deploy branch
```

Set `[project].deploy_remote` in `zplus.toml` before deploying.

## Where to go next

- [Concepts](concepts.md) to understand the model behind all of this.
- [Authoring](authoring.md) for every way to create content (including batch and agents).
