"""add-type: interactively define a new doc type, saved to the user library."""
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


def run():
    print("zplus add-type — define a new doc type (saved to your user library)\n")
    name = core.slugify(_ask("Type key (lowercase, e.g. 'retro')  > "))
    if not name:
        raise SystemExit("error: invalid type key")
    if name in paths.list_types():
        raise SystemExit(f"error: a type named '{name}' already exists")
    label = _ask("Nav label (e.g. 'Retros')  > ")
    folder = _ask(f"Docs folder (e.g. 'work/{name}')  > ", default=f"work/{name}")

    print("\nSections — enter a heading, then its shape. Blank heading to finish.")
    sections = []
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

    d = authoring.write_type(name, label, folder, sections)
    print(f"\n✔ added type '{name}' ({len(sections)} section(s)) → {d}")
    print("  Use it in a profile (`zplus add-profile`) or a project's zplus.toml.")
    return 0


def main(argv=None):
    return run()
