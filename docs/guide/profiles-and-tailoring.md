# Profiles & tailoring

## Profiles

A **profile** is a named starter bundle — the nav arrangement, the set of types, and their
templates — that `zplus new --profile <name>` scaffolds into a self-contained project.

```bash
zplus profiles                          # list available profiles
zplus new my-site --profile administration
```

Two ship today:

- **`administration`** — a broad company operating system (22 types): Mission Control,
  Company, How We Run, Operating Rhythm, an Automation & AI program, a Knowledge Base, and
  registries (Roles, Systems, Policies, Vendors, Objectives, Sites).
- **`projecthub`** — the project-hub nav (curated sections + dated logs).

When you scaffold, the profile is resolved into a full, editable `zplus.toml` — you own it
from then on; upgrades never overwrite your content.

## The shared type library

Types live in a library and profiles compose from it, so a type authored once is reused
across the constellation. The library is `bundled ∪ user`:

- **bundled** — ships in the package;
- **user** — your own types/profiles at `$ZPLUS_HOME` (default `~/.config/zplus/`). User
  entries win on a name clash; the installed package is never edited in place.

## Authoring types and profiles

```bash
zplus add-type       # interactively define a new type → your user library
zplus add-profile    # interactively compose a profile from library types → user library
```

Both are interactive. New types and profiles land in `$ZPLUS_HOME` and are immediately
available to `zplus new`.

## Editing `zplus.toml` directly

A type is just a `[[type]]` block. Common knobs:

```toml
[[type]]
name = "procedure"
label = "Procedures"
folder = "procedures"
template = "procedure.md"
order = "alpha"        # A→Z by title (default: date-desc for templated types)
facet = "function"     # group the landing by this field
  [[type.section]]     # the layout — one block per section
  heading = "Steps"
  shape = "task"       # prose | list | task | diagram
  [[type.field]]       # typed front matter
  name = "status"
  type = "status"
  values = ["draft", "active", "deprecated"]
  done = ["active", "deprecated"]
```

- **`order`** — `alpha` (A→Z by title) or `date-desc` (newest first). Empty derives from
  `templated`.
- **`facet`** — a field name to group the landing by.
- **`[[type.section]]`** — the entry layout; `shape` drives how `--fill` scaffolds it.
- **`[[type.field]]`** — see [Fields & the graph](fields-and-graph.md).

After editing, run `zplus gen-nav` (or just `serve`/`build`, which regenerate nav and
derived content). Editing a template's prose is a file edit under `templates/`; changing a
type's *structure* is a manifest edit here.

## Keeping the toolkit updated

```bash
pip install -U git+https://github.com/peers8862/zplus.git
zplus apply        # re-patch config + materialize any new defaults; content is preserved
```
