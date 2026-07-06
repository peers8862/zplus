"""gen-derived: write dashboards, the Action Center, and corpus.json from the corpus.

Runs before `zensical build`. Writes only tool-owned files — landing dashboards
(marker-guarded), docs/mission-control/action-center.md, and root corpus.json.
Never touches hand-authored entry files.
"""
import json
import os

from .. import manifest as manifest_mod, corpus as corpus_mod, render


def gen_derived(project_dir):
    m = manifest_mod.load(os.path.join(project_dir, "zplus.toml"))
    c = corpus_mod.resolve(corpus_mod.read_corpus(project_dir, m), m)
    docs = os.path.join(project_dir, "docs")

    by_type = {}
    for e in c.entries:
        by_type.setdefault(e.type_name, []).append(e)

    n_dash = 0
    for t in m.types:
        ents = by_type.get(t.name)
        landing = os.path.join(docs, t.folder, "index.md")
        if not ents or not os.path.exists(landing):
            continue
        with open(landing, encoding="utf-8") as f:
            text = f.read()
        table = render.dashboard_table(t, ents, c)
        text = render.splice_md_region(text, render.DASH_BEGIN, render.DASH_END, table)
        with open(landing, "w", encoding="utf-8") as f:
            f.write(text)
        n_dash += 1

    mc = os.path.join(docs, "mission-control")
    if os.path.isdir(mc):
        with open(os.path.join(mc, "action-center.md"), "w", encoding="utf-8") as f:
            f.write(render.action_center_markdown(c, m))

    with open(os.path.join(project_dir, "corpus.json"), "w", encoding="utf-8") as f:
        json.dump(render.corpus_to_dict(c), f, indent=2)

    print(f"zplus gen-derived: {n_dash} dashboard(s), action center, corpus.json")
    return 0


def main(argv=None):
    return gen_derived(os.getcwd())
