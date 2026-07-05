"""new: create a fresh Zensical project, then apply the zplus overlay for a profile."""
import os
import subprocess
import sys

from . import apply as apply_mod


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    profile = "projecthub"
    if "--profile" in argv:
        i = argv.index("--profile")
        if i + 1 >= len(argv):
            raise SystemExit("usage: zplus new <name> [--profile <profile>]")
        profile = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if not argv:
        raise SystemExit("usage: zplus new <name> [--profile <profile>]")
    name = argv[0]

    subprocess.check_call(["zensical", "new", name])
    project = os.path.abspath(name)
    for a in apply_mod.apply(project, profile=profile):
        print(f"  • {a}")
    print(f"✔ created '{name}' ({profile}) — cd {name} && zplus serve")
    return 0
