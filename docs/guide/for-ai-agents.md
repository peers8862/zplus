# zplus & AI agents

zplus is designed so that humans and AI agents operate a site through **one interface**.
That symmetry is the core of the "Automated Enterprise" idea: the documentation system is
populated and maintained by whoever — or whatever — is best suited, and it stays valid
because the same guardrails apply to all of them.

## The two APIs

- **Write API — the CLI.** Everything a human does, an agent does with the same commands.
  There is no separate agent mode.
- **Read API — `corpus.json`.** Every build emits a structured export of the whole corpus
  (entries, fields, resolved refs, computed backlinks) at the project root, plus an
  `llms.txt` index pointing at it. These are *not* published into the built site — they
  live in the working tree for local tools.

## An agent creating content

An agent that has read the corpus can create a fully-linked entry with one-shot flags —
no interactive prompts required:

```bash
zplus new-entry --type agent --title "Invoice Bot" \
  --set owner=steve --set status=supervised \
  --set runs=invoice-import --set governed_by=financial-controls
```

Because refs are chosen by slug, the agent references *existing* entries and the graph
stays connected. Batch creation (`--from`) lets an agent stand up many entries from a
generated data file in one call.

## An agent deciding what to do

The **Action Center** (`docs/mission-control/action-center.md`) is a derived worklist —
unowned entries, open items, broken links — computed from the same corpus an agent reads.
Humans and agents literally consume the same to-do list. An agent can read `corpus.json`,
find the open items, act, and create the follow-up entries, all through the CLI.

## Trust: `zplus check`

Whoever creates content, `zplus check` validates it — dangling refs, missing required
fields, invalid enum/status values — and exits non-zero on failure. Run it in CI so a bad
write (human or agent) is caught before it reaches the corpus that everything else is
derived from.

## The comprehensibility guarantee

As you hand work to agents, the graph + backlinks let a human trace any automation's
connections in a couple of clicks: *this automation → run by this agent → governed by this
policy → owned by this role → touching these systems.* That traceability — maintained
mechanically, never by hand — is what keeps an increasingly-automated enterprise
comprehensible to the people who own it.

## Suggested agent loop

1. Read `corpus.json` (and `llms.txt` for orientation).
2. Read the Action Center to find what needs attention.
3. Act; create/update entries via `zplus new-entry --set …` (or `--from` for batches).
4. Run `zplus check`; fix anything it flags.
5. `zplus build` regenerates every derived view from the updated corpus.
