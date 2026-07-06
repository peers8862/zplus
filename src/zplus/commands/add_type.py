"""add-type: interactively define a new doc type (templated or section), user library."""
from .. import authoring, core, paths

_SHAPES = ("prose", "list", "task")


def _ask(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        if default is not None:
            return default
        print("  (required)")


def _yesno(prompt, default=True):
    v = input(prompt).strip().lower()
    return default if not v else v[0] == "y"


def _collect_landing():
    print("\nLanding/intro text (optional) — end with a line containing only '.', "
          "or '.' to skip:")
    lines = []
    while True:
        line = input()
        if line.strip() == ".":
            break
        lines.append(line)
    return "\n".join(lines).strip("\n")


def run():
    print("zplus add-type — define a new doc type (saved to your user library)\n")
    name = core.slugify(_ask("Type key (lowercase, e.g. 'retro')  > "))
    if not name:
        raise SystemExit("error: invalid type key")
    if name in paths.list_types():
        raise SystemExit(f"error: a type named '{name}' already exists")
    label = _ask("Nav label (e.g. 'Retros')  > ")
    folder = _ask(f"Docs folder (e.g. 'work/{name}')  > ", default=f"work/{name}")
    templated = _yesno("Templated? — dated entries via new-entry (Y), "
                       "or a plain section grown via add-page (n)  [Y/n]  > ", True)

    sections = []
    if templated:
        print("\nSections — enter a heading, then its shape. Blank heading to finish.")
        while True:
            heading = input("  Section heading  > ").strip()
            if not heading:
                break
            shape = input("  Shape [prose/list/task] (prose)  > ").strip().lower() or "prose"
            if shape not in _SHAPES:
                print("    (unknown shape, using prose)")
                shape = "prose"
            prompt = input("  Prompt (optional)  > ").strip()
            sections.append(authoring.section(heading, shape, prompt))

    landing = _collect_landing()
    d = authoring.write_type(name, label, folder, sections,
                             templated=templated, landing=landing)
    kind = "templated" if templated else "section"
    print(f"\n✔ added {kind} type '{name}' → {d}")
    if templated:
        print("  Create entries with `zplus new-entry`; add it to a profile with `zplus add-profile`.")
    else:
        print("  Add pages with `zplus add-page`; add it to a profile with `zplus add-profile`.")
    return 0


def main(argv=None):
    return run()
