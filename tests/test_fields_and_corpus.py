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


if __name__ == "__main__":
    unittest.main()
