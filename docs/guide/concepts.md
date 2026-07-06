# Concepts — the model

zplus is built on a small set of nested primitives. Understanding them is the whole game.

```
PROFILE          a named starter bundle (administration, projecthub, …)
  └ NAV          a tree of pages + collections in zensical.toml
      ├ PAGE       a singleton doc (a landing, an orientation page)
      └ COLLECTION a folder of homogeneous entries of a TYPE, grown with new-entry
            └ TYPE     label + folder + layout (sections) + fields + order + facet
                  ├ SECTION  a heading block: shape (prose|list|task|diagram) + prompt
                  └ FIELD    typed front-matter: text·enum·date·owner·status·ref…
                                └ a `ref` field is an edge → the corpus is a GRAPH
```

## Types: templated vs. section

Every doc type is one of two kinds, set by its `templated` flag:

- **Templated** (`templated = true`) — a stream of dated entries created with
  `zplus new-entry`, ordered newest-first by default. Meetings, Decisions, Automations.
- **Section** (`templated = false`) — a folder of plain pages added with
  `zplus add-page`, ordered A→Z. Used for curated areas and registries (Roles, Systems).

Both kinds are "collections" — folders that grow. A type may also carry a one-line
`landing` that becomes the folder's `index.md`, so a fresh site shows its whole skeleton.

## Fields make entries structured

A type declares **fields** — typed front-matter that every entry carries:

```toml
[[type.field]]
name = "status"
type = "status"
values = ["manual", "assisted", "supervised", "autonomous"]
```

Field types: `text · enum · multi-enum · date · number · bool · owner · status · ref`.
Fields are what make the corpus queryable, dashboards possible, and the Action Center
correct. See [Fields & the graph](fields-and-graph.md).

## Refs make the corpus a graph

A `ref` field's value *is another entry* (by slug). That turns fields into **edges**:

```toml
[[type.field]]
name = "runs"
type = "ref"
ref = "automation"   # target type
many = true          # a list of them
```

An Agent that `runs` an Automation that `touches` a System is a path through the graph.
zplus computes the reverse edges (**backlinks**) for free, so you can trace any entry's
connections without maintaining links by hand.

## The corpus

At build time zplus reads every entry's front matter into an in-memory **corpus** — all
entries indexed by slug, with refs resolved and backlinks computed. Everything the build
generates (dashboards, boards, the Action Center, the graph page, `corpus.json`) is
*derived* from this one structure. Nothing is hand-maintained; nothing can go stale.

## The manifest: `zplus.toml`

All of the above lives in a per-project `zplus.toml` — the single source of truth the
engine reads and the `add-*` commands write. A profile is just a curated, self-contained
`zplus.toml` plus its templates. See [Profiles & tailoring](profiles-and-tailoring.md).
