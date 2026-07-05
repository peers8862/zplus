"""Ensure and fill the managed nav region inside a project's zensical.toml.

String-level (not tomllib round-trip) so comments and formatting are preserved.
The region is bounded by a marker pair; `gen-nav` regenerates its body from the
manifest. Placement is a sensible default the user can relocate once.
"""
import re


def region_markers(name):
    return (f"# >>> {name} — managed by zplus; do not hand-edit >>>",
            f"# <<< {name} <<<")


def has_active_nav(text):
    """True if an uncommented `nav = [` exists."""
    return re.search(r"(?m)^[ \t]*nav[ \t]*=[ \t]*\[", text) is not None


def ensure_nav_region(text, region_name):
    """Ensure the managed region markers exist inside an active nav array.

    - If the region is already present, return unchanged.
    - If an active nav array exists, insert an empty region just after `nav = [`.
    - Otherwise create a fresh `nav = [...]` under `[project]` with the region.
    Body is populated separately by `splice_region`.
    """
    begin, end = region_markers(region_name)
    if begin in text:
        return text
    region = f"  {begin}\n  {end}"
    if has_active_nav(text):
        return re.sub(r"(?m)^([ \t]*nav[ \t]*=[ \t]*\[)",
                      lambda m: m.group(1) + "\n" + region, text, count=1)
    nav_block = f'nav = [\n  {{ "Home" = ["index.md"] }},\n{region}\n]\n'
    if re.search(r"(?m)^\[project\][ \t]*$", text):
        return re.sub(r"(?m)^(\[project\][ \t]*)$",
                      lambda m: m.group(1) + "\n\n" + nav_block, text, count=1)
    return nav_block + "\n" + text


def splice_region(text, region_name, body):
    """Replace the region's body (between markers) with `body` (may be empty)."""
    begin, end = region_markers(region_name)
    pat = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    mid = ("\n" + body) if body else ""
    return pat.sub(lambda _: begin + mid + "\n  " + end, text)
