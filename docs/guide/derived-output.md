# Derived output

`zplus gen-derived` reads the corpus and writes generated content **before** the site is
built. It runs automatically inside `zplus serve` and `zplus build`, so you rarely call it
directly. It only ever writes *tool-owned* files — it never edits your hand-authored
entries.

## Dashboards

Each collection's landing (`docs/<folder>/index.md`) gets a **dashboard table** injected
into a marker-guarded region: one row per entry, a column per declared field, and a
"Referenced by" count from the backlinks. Your hand-written landing prose stays above the
region and is preserved on every regeneration.

## Boards

Types with a `status` field also get a **board** — a section per status value in workflow
order (a kanban), followed by a mermaid **state diagram** of the workflow. The automation
maturity ladder (`manual → assisted → supervised → autonomous`) renders as a board for
free.

## Faceting

If a type sets `facet = "<field>"`, its landing also gets a **By &lt;field&gt;** grouping —
entries bucketed by that field's values. For example, Procedures faceted by `function`
group into Finance / People / Operations / Legal / IT.

## The Action Center

A generated page at `docs/mission-control/action-center.md` (a Mission Control subpage)
aggregates, across the *whole* corpus:

- **Needs an owner** — entries with an empty required `owner`;
- **Open / in progress** — entries whose status isn't in its type's `done`;
- **Broken links** — dangling refs.

Nobody curates it, so it can't go stale — and it's exactly the worklist an AI agent would
compute to decide what to do next.

## The graph page

`docs/mission-control/graph.md` renders the corpus as a mermaid `graph LR`: a node per
ref-connected entry, an edge per ref labelled by field name. This is the "trace any
automation's connections at a glance" view.

## The agent contract: `corpus.json` + `llms.txt`

Two files are written to the **project root** (outside `docs/`, so they are *not*
published into the built/encrypted site):

- **`corpus.json`** — every entry with its fields, resolved refs, and computed backlinks.
  The machine-readable read-API of your site.
- **`llms.txt`** — a plain-text index of types and entries, pointing at `corpus.json`.

Both stay in the working tree for local AI tools. See [zplus & AI agents](for-ai-agents.md).

> Note: `corpus.json` is regenerated on every `gen-derived`, so it shows a git diff
> whenever content changes. If that churn bothers you, add it to `.gitignore` — it's fully
> regenerable.
