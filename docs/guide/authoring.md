# Authoring — filling a site

zplus gives you several ways to create content, from all-hand to fully agent-driven. They
all end at the same place: a correctly-named markdown file with complete front matter.
Pick the mode that fits the moment.

## The ways to create an entry

| Mode | Command | Best for |
|---|---|---|
| **Scaffold + edit** | `zplus new-entry` | prose-heavy entries — stamps the template, opens your `$EDITOR` |
| **Guided wizard** | `zplus new-entry --fill` | non-technical authoring — prompts every field and section |
| **One-shot flags** | `zplus new-entry --type T --title "…" --set k=v …` | scripting and agents — no prompts, no editor |
| **Clone** | `zplus new-entry --type T --title "…" --like SLUG` | starting from an existing entry's field values |
| **Batch** | `zplus new-entry --type T --from data.csv` | standing up a whole registry at once |
| **Quick-capture** | `zplus jot "a thought"` | friction-free capture → a draft to triage later |
| **Section page** | `zplus add-page` | a plain page in a section-type folder (Roles, Systems) |
| **Raw** | write the `.md` file yourself | the escape hatch; always valid |

## The guided wizard (`--fill`)

After picking a type, title, and date, the wizard prompts each declared **field**:

- **enum / status** fields show a numbered pick-list.
- **ref** fields list the existing entries of the target type — pick by number, or type a
  slug. `many` refs collect several (blank line to finish).
- other fields take free text; required fields re-prompt until answered.

Then it walks each section. This is the friendliest way to keep the graph connected —
refs are chosen from real entries, so they resolve by construction.

## One-shot flags (`--set`)

Everything on the command line, no interaction:

```bash
zplus new-entry --type automation --title "Late-Payer Nudge" \
  --set owner=steve --set status=assisted --set touches=billing
```

A value with `|` becomes a list (`--set touches="billing|payroll"`). This mode is what
lets an **AI agent** create entries — it shells out to the same command a human uses.

## Batch (`--from`)

Populate a registry from a CSV (or YAML list). The header row names the columns; each row
becomes one entry. `title` is required; `date` is optional.

```csv
title,owner,status,touches
Invoice Import,steve,manual,billing
Late Nudge,kev,assisted,billing|payroll
```

```bash
zplus new-entry --type automation --from automations.csv
```

## One interface for humans and agents

Modes 3–6 (one-shot, batch, jot, clone) are all the same underlying operation with
different input sources — and they're the *same commands* a person runs. There's no
separate "agent mode": whoever is best suited (you, a script, an AI) creates entries
through one CLI, and `zplus check` guards the door regardless of who knocked. See
[zplus & AI agents](for-ai-agents.md).

## After authoring

Run `zplus check` to validate (broken refs, missing required fields, invalid enums), then
`zplus serve` / `build` — both regenerate derived content first, so new entries appear in
dashboards, boards, and the Action Center automatically.
