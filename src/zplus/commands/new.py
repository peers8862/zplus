"""new: create a fresh Zensical project, then apply the zplus overlay."""
import os
import subprocess
import sys

from . import apply as apply_mod


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        raise SystemExit("usage: zplus new <name>")
    name = argv[0]
    subprocess.check_call(["zensical", "new", name])
    project = os.path.abspath(name)
    for a in apply_mod.apply(project):
        print(f"  • {a}")
    print(f"✔ created and configured '{name}' — cd {name} && zplus serve")
    return 0
