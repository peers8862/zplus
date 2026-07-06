# Ridgeline Roofing — a full `administration` demo

A worked example that populates every collection of the `administration` profile with
imaginary-but-realistic data for a roofing contractor, **Ridgeline Roofing Co.**, to
demonstrate zplus end to end: typed fields, `ref` links, backlinks, dashboards, boards,
faceting, the Action Center, and the graph page.

## Build it

Activate a venv that has both `zplus` and `zensical`, then:

```bash
./build-demo.sh            # → ~/making/ridgeline-roofing
# or: ./build-demo.sh /path/to/dir
cd ~/making/ridgeline-roofing
zplus serve                # view at http://localhost:8000
```

## What's in it

**Registries** (ref targets): 6 Roles · 8 Systems · 5 Policies · 5 Vendors · 3 Objectives ·
3 constellation Sites.

**Typed collections with fields + refs:**

| Collection | Fields | Links to |
|---|---|---|
| Automations (6) | owner, status (maturity), touches, governed_by | Systems, Policies |
| Agents (4) | owner, status (maturity), runs, governed_by | Automations, Policies |
| Incidents (3) | owner, severity, status, involved | Systems |
| Procedures (6) | owner, status, function (facet), uses | Roles, Systems |
| Decisions (5) | owner, status, supersedes | Decisions (a supersede chain) |

**Curated pages:** Mission Control, Company (+ mission/values + company record), How We Run,
Automation & AI (+ a hand-authored **division-of-duties** mermaid map), and a prose
monthly **Review**.

## What to look at once it's running

- **Any collection landing** — a generated dashboard table of entries + fields.
- **Automations / Agents landings** — a **board** (kanban by maturity ladder) + a state diagram.
- **Procedures landing** — faceted **By function** (finance / people / operations).
- **Mission Control → Action Center** — the open Payroll incident, the proposed shingle
  decision, the draft storm-claim procedure — surfaced automatically.
- **Mission Control → Graph** — the mermaid graph of every ref link.
- **`corpus.json`** (project root) — the whole graph as machine-readable data.

## How it's wired

Refs use slugs. Registry entries (section types) have clean slugs (`office-manager`,
`quickbooks`), so most refs read naturally. Refs to *templated* entries use their
date-prefixed slug (e.g. an agent's `runs = 2026-05-01-invoice-import`) — see the fixed
dates in `seed/automations.csv` and `seed/decisions.csv`.
