"""zplus command-line entry point — a subcommand framework (SP2 `add-type` slots in here)."""
import argparse
import os
import sys

from . import manifest as manifest_mod
from .commands import (add_page as add_page_cmd, add_profile as add_profile_cmd,
                       add_type as add_type_cmd, apply as apply_cmd,
                       check as check_cmd, derived as derived_cmd,
                       entry as entry_cmd, nav as nav_cmd, new as new_cmd,
                       site as site_cmd)


def build_parser():
    p = argparse.ArgumentParser(prog="zplus",
                                description="Zensical customization toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_new = sub.add_parser("new", help="create a new Zensical project and apply zplus")
    p_new.add_argument("name")
    p_new.add_argument("--profile", default="projecthub",
                       help="site kind to seed (default: projecthub)")

    p_apply = sub.add_parser("apply", help="apply/update zplus in the current project")
    p_apply.add_argument("--profile", default=None,
                         help="profile for a fresh project (default: projecthub)")

    sub.add_parser("profiles", help="list available profiles (site kinds)")
    sub.add_parser("add-type", help="interactively define a new doc type (user library)")
    sub.add_parser("add-profile", help="interactively compose a profile from types (user library)")
    p_entry = sub.add_parser("new-entry", help="scaffold a new entry")
    p_entry.add_argument("--fill", action="store_true",
                         help="prompt each field and section at the terminal")
    p_entry.add_argument("--from", dest="from_file", metavar="FILE",
                         help="batch-create entries from a CSV/YAML file")
    p_entry.add_argument("--type", dest="type_name", metavar="NAME",
                         help="type name (required with --from / one-shot)")
    p_entry.add_argument("--title", help="entry title (one-shot, non-interactive)")
    p_entry.add_argument("--set", dest="sets", action="append", metavar="k=v",
                         default=[], help="set a field value (repeatable)")
    p_entry.add_argument("--date", help="entry date (one-shot; default today)")
    p_entry.add_argument("--like", metavar="SLUG",
                         help="clone field values from an existing entry")

    p_jot = sub.add_parser("jot", help="quick-capture a draft entry from text")
    p_jot.add_argument("text")
    p_jot.add_argument("--type", dest="jot_type", default="idea",
                       help="target type (default: idea)")
    sub.add_parser("add-page", help="add a plain subpage to a non-templated section")
    sub.add_parser("gen-nav", help="regenerate the managed nav region")
    sub.add_parser("check", help="lint the corpus (refs, required fields, enums)")
    sub.add_parser("gen-derived",
                   help="regenerate dashboards, the action center, and corpus.json")
    sub.add_parser("serve", help="regenerate nav, then serve locally")
    sub.add_parser("build", help="build + encrypt into ./site")
    sub.add_parser("deploy", help="build + encrypt + push to the deploy branch")
    return p


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    args = build_parser().parse_args(argv)
    cwd = os.getcwd()

    if args.cmd == "new":
        a = [args.name] + (["--profile", args.profile] if args.profile else [])
        return new_cmd.main(a)
    if args.cmd == "apply":
        a = ["--profile", args.profile] if args.profile else []
        return apply_cmd.main(a)
    if args.cmd == "profiles":
        for name in manifest_mod.available_profiles():
            print(name)
        return 0
    if args.cmd == "add-type":
        return add_type_cmd.main([])
    if args.cmd == "add-profile":
        return add_profile_cmd.main([])
    if args.cmd == "new-entry":
        if args.from_file:
            if not args.type_name:
                raise SystemExit("error: --from requires --type NAME")
            created = entry_cmd.create_from_file(cwd, args.type_name, args.from_file)
            print(f"✔ created {len(created)} entr{'y' if len(created) == 1 else 'ies'}")
            return 0
        if args.sets or args.title or args.like:
            if not args.type_name or not args.title:
                raise SystemExit("error: one-shot needs --type NAME and --title TITLE")
            created = entry_cmd.create_one(cwd, args.type_name, args.title,
                                           sets=args.sets, date_str=args.date,
                                           like=args.like)
            print(f"✔ created {created[0]}" if created else "nothing created")
            return 0
        return entry_cmd.main(["--fill"] if args.fill else [])
    if args.cmd == "jot":
        created = entry_cmd.jot(cwd, args.text, args.jot_type)
        print(f"✔ jotted {created[0]}" if created else "nothing created")
        return 0
    if args.cmd == "add-page":
        return add_page_cmd.main([])
    if args.cmd == "gen-nav":
        return nav_cmd.main([])
    if args.cmd == "check":
        return check_cmd.run(cwd)
    if args.cmd == "gen-derived":
        return derived_cmd.gen_derived(cwd)
    if args.cmd == "serve":
        return site_cmd.serve(cwd)
    if args.cmd == "build":
        site_cmd.build(cwd)
        return 0
    if args.cmd == "deploy":
        site_cmd.deploy(cwd)
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
