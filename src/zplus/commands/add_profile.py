"""add-profile: interactively compose an ordered profile from library types."""
import re

from .. import authoring, core, paths


def _ask(prompt, default=None):
    while True:
        val = input(prompt).strip()
        if val:
            return val
        if default is not None:
            return default
        print("  (required)")


def run():
    print("zplus add-profile — compose a site kind from types (saved to user library)\n")
    name = core.slugify(_ask("Profile name (e.g. 'sales')  > "))
    if not name:
        raise SystemExit("error: invalid profile name")
    if name in paths.list_profiles():
        raise SystemExit(f"error: a profile named '{name}' already exists")
    label = _ask("Label (e.g. 'Sales')  > ")

    available = paths.list_types()
    print("\nAvailable types:", ", ".join(available))
    picked = [t for t in re.split(r"[,\s]+",
                                  _ask("Types in order (space- or comma-separated)  > ").strip())
              if t]
    unknown = [t for t in picked if t not in available]
    if unknown:
        raise SystemExit(f"error: unknown type(s): {', '.join(unknown)}")
    if not picked:
        raise SystemExit("error: a profile needs at least one type")

    path = authoring.write_profile(name, label, picked)
    print(f"\n✔ added profile '{name}' ({len(picked)} types) → {path}")
    print(f"  Create a site with it: zplus new my-site --profile {name}")
    return 0


def main(argv=None):
    return run()
