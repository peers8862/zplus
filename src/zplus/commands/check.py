"""zplus check — lint the corpus against the manifest's field declarations."""
import os

from .. import manifest as manifest_mod, corpus as corpus_mod


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def run(project_dir):
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    c = corpus_mod.resolve(corpus_mod.read_corpus(project_dir, m), m)
    type_by_name = {t.name: t for t in m.types}
    problems = []
    for e in c.entries:
        t = type_by_name[e.type_name]
        for fl in t.fields:
            val = e.fields.get(fl.name)
            if fl.required and (val is None or val == "" or val == []):
                problems.append(f"{e.path}: missing required field '{fl.name}'")
                continue
            if val is None:
                continue
            if fl.type in ("enum", "status"):
                if val not in fl.values:
                    problems.append(
                        f"{e.path}: field '{fl.name}'='{val}' not in {fl.values}")
            elif fl.type == "multi-enum":
                for v in _as_list(val):
                    if v not in fl.values:
                        problems.append(
                            f"{e.path}: field '{fl.name}' value '{v}' not in {fl.values}")
            elif fl.type == "ref":
                for slug in _as_list(val):
                    target = c.by_slug.get(slug)
                    if target is None:
                        problems.append(
                            f"{e.path}: ref '{fl.name}' → unknown entry '{slug}'")
                    elif fl.ref and target.type_name != fl.ref:
                        problems.append(
                            f"{e.path}: ref '{fl.name}' → '{slug}' is a "
                            f"{target.type_name}, expected {fl.ref}")
    for p in problems:
        print(p)
    if problems:
        print(f"✗ {len(problems)} problem(s) across {len(c.entries)} entries")
        return 1
    print(f"✔ corpus OK: {len(c.entries)} entries")
    return 0


def main(argv=None):
    return run(os.getcwd())
