import os
import tempfile
import unittest

from zplus import core
from zplus import manifest

FIELD_FRAG = '''
[[type]]
name = "agent"
label = "Agents"
folder = "agents"
template = "agent.md"
landing = "Agents."
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["manual", "assisted", "supervised", "autonomous"]
  [[type.field]]
  name = "runs"
  type = "ref"
  ref = "automation"
  many = true
'''


class FrontMatter(unittest.TestCase):
    def test_parses_scalars_and_lists(self):
        text = ("---\n"
                "date: 2026-07-06\n"
                "title: Invoice Bot\n"
                "owner: steve\n"
                "runs: [invoice-import, late-nudge]\n"
                "---\n"
                "# Invoice Bot\n\nbody here\n")
        fm, body = core.split_front_matter(text)
        self.assertEqual(fm["owner"], "steve")
        self.assertEqual(fm["runs"], ["invoice-import", "late-nudge"])
        self.assertIn("body here", body)

    def test_no_front_matter(self):
        fm, body = core.split_front_matter("# Just a heading\n")
        self.assertEqual(fm, {})
        self.assertIn("Just a heading", body)


class FieldModel(unittest.TestCase):
    def test_parses_fields(self):
        m = manifest.loads(FIELD_FRAG, source="agent")
        t = m.types[0]
        self.assertEqual([f.name for f in t.fields], ["owner", "status", "runs"])
        owner, status, runs = t.fields
        self.assertTrue(owner.required)
        self.assertEqual(status.values, ["manual", "assisted", "supervised", "autonomous"])
        self.assertEqual(runs.type, "ref")
        self.assertEqual(runs.ref, "automation")
        self.assertTrue(runs.many)

    def test_rejects_unknown_field_type(self):
        bad = FIELD_FRAG.replace('type = "owner"', 'type = "wizard"')
        with self.assertRaises(ValueError):
            manifest.loads(bad, source="bad")

    def test_ref_requires_target(self):
        bad = ('[[type]]\nname="x"\nlabel="X"\nfolder="x"\ntemplated=false\n'
               'landing="x"\n  [[type.field]]\n  name="r"\n  type="ref"\n')
        with self.assertRaises(ValueError):
            manifest.loads(bad, source="bad")

    def test_diagram_is_a_valid_shape(self):
        self.assertIn("diagram", manifest.VALID_SHAPES)


from zplus import corpus as corpus_mod


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


AGENT_TYPES = manifest.loads(FIELD_FRAG + '''
[[type]]
name = "automation"
label = "Automations"
folder = "automations"
template = "automation.md"
landing = "Automations."
''', source="fixture")


class CorpusGraph(unittest.TestCase):
    def _project(self, d):
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")
        _write(os.path.join(d, "docs", "agents", "invoice-bot.md"),
               "---\ntitle: Invoice Bot\nowner: steve\n"
               "status: supervised\nruns: [invoice-import]\n---\n# Invoice Bot\n")

    def test_reads_entries_and_declared_fields(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            c = corpus_mod.read_corpus(d, AGENT_TYPES)
            slugs = sorted(e.slug for e in c.entries)
            self.assertEqual(slugs, ["invoice-bot", "invoice-import"])
            bot = c.get("invoice-bot")
            self.assertEqual(bot.fields["owner"], "steve")
            self.assertEqual(bot.fields["runs"], ["invoice-import"])

    def test_resolve_populates_backlinks_on_target(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            c = corpus_mod.resolve(corpus_mod.read_corpus(d, AGENT_TYPES), AGENT_TYPES)
            target = c.get("invoice-import")
            self.assertEqual(target.backlinks[("agent", "runs")], ["invoice-bot"])


from zplus.commands import check as check_cmd


class Check(unittest.TestCase):
    def _project(self, d, runs_slug, owner="steve"):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write('[project]\nprofile="fixture"\n' + FIELD_FRAG + '''
[[type]]
name = "automation"
label = "Automations"
folder = "automations"
template = "automation.md"
landing = "Automations."
''')
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")
        _write(os.path.join(d, "docs", "agents", "invoice-bot.md"),
               f"---\ntitle: Invoice Bot\nowner: {owner}\n"
               f"status: supervised\nruns: [{runs_slug}]\n---\n# Invoice Bot\n")

    def test_clean_corpus_returns_zero(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d, runs_slug="invoice-import")
            self.assertEqual(check_cmd.run(d), 0)

    def test_dangling_ref_and_missing_required_return_one(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d, runs_slug="does-not-exist", owner="")
            self.assertEqual(check_cmd.run(d), 1)


class DiagramShape(unittest.TestCase):
    def test_render_body_wraps_mermaid(self):
        out = core.render_body(["graph TD", "A --> B"], "diagram")
        self.assertTrue(out.startswith("```mermaid\n"))
        self.assertIn("A --> B", out)
        self.assertTrue(out.rstrip().endswith("```"))


class AdminFields(unittest.TestCase):
    def test_graph_types_declare_expected_ref_fields(self):
        m = manifest.resolve_profile("administration")
        by = {t.name: t for t in m.types}
        agent_refs = {f.name: f.ref for f in by["agent"].fields if f.type == "ref"}
        self.assertEqual(agent_refs.get("runs"), "automation")
        self.assertEqual(agent_refs.get("governed_by"), "policy")
        auto_refs = {f.name: f.ref for f in by["automation"].fields if f.type == "ref"}
        self.assertEqual(auto_refs.get("touches"), "system")
        for name in ["agent", "automation", "decision", "incident", "procedure"]:
            owners = [f for f in by[name].fields if f.name == "owner"]
            self.assertTrue(owners and owners[0].required, f"{name} needs required owner")

    def test_templates_have_field_keys(self):
        from zplus import paths
        agent_tpl = paths.read_type_template("agent").decode("utf-8")
        for key in ("owner:", "status:", "runs:", "governed_by:"):
            self.assertIn(key, agent_tpl)


if __name__ == "__main__":
    unittest.main()
