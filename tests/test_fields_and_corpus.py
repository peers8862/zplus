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


if __name__ == "__main__":
    unittest.main()
