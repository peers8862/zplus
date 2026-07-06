# Fields & the graph

Fields turn entries from prose into a queryable, linked dataset. This is what makes the
derived output (dashboards, boards, the Action Center, the graph) possible.

## Field types

Declared per type as `[[type.field]]` blocks:

| Type | Value | Notes |
|---|---|---|
| `text` | free string | |
| `enum` | one of `values` | validated by `check` |
| `multi-enum` | several of `values` | list |
| `date` | a date | |
| `number` | a number | |
| `bool` | true/false | |
| `owner` | a person | required-owner drives the Action Center |
| `status` | one of `values` | supports a workflow (see below) |
| `ref` | another entry's slug | an **edge** in the graph |

```toml
[[type.field]]
name = "owner"
type = "owner"
required = true
```

## Refs and backlinks

A `ref` points at another entry by slug; `many = true` makes it a list. `ref` names the
target type:

```toml
[[type.field]]
name = "touches"
type = "ref"
ref = "system"
many = true
```

At build time zplus resolves refs and computes **backlinks** — the reverse edges — for
free. So a System's dashboard row shows how many entries reference it, and the
[graph page](derived-output.md) draws every connection. You never maintain a link twice.

## Status workflows

A `status` field's `values` list is an ordered pipeline. Add `done` to mark which states
*don't* need attention:

```toml
[[type.field]]
name = "status"
type = "status"
values = ["open", "mitigated", "resolved", "postmortem"]
done   = ["resolved", "postmortem"]
```

This one declaration powers three things:

- **The Action Center** flags entries whose status is *not* in `done` (open incidents,
  proposed decisions, draft procedures) — read from the workflow, not guessed.
- **Boards** render a column per status value, in workflow order.
- **State diagrams** draw the workflow as a mermaid `stateDiagram`.

Types without a `done` (e.g. the automation maturity ladder) still get a board, but their
entries are never flagged as "needing attention" — maturity isn't a to-do.

## Validation — `zplus check`

`zplus check` reads the whole corpus and reports:

- **broken refs** — a `ref` value that isn't a real entry, or is the wrong type;
- **missing required fields** — a `required` field left empty;
- **invalid enum/status values** — a value not in the declared `values`.

It exits non-zero on any problem, so you can run it in CI. Because agents create entries
through the same CLI, `check` is what lets you trust the corpus no matter who filled it.

```bash
zplus check
# ✔ corpus OK: 42 entries
# — or —
# docs/automations/bad.md: ref 'touches' → unknown entry 'ghost-system'
# ✗ 1 problem(s) across 42 entries
```
