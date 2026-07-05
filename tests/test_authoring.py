import os
import tempfile
import unittest

from zplus import authoring, manifest, paths


class TestAuthoring(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._old = os.environ.get("ZPLUS_HOME")
        os.environ["ZPLUS_HOME"] = self.tmp

    def tearDown(self):
        if self._old is None:
            os.environ.pop("ZPLUS_HOME", None)
        else:
            os.environ["ZPLUS_HOME"] = self._old

    def test_write_type_appears_and_parses(self):
        secs = [authoring.section("What went well", "list"),
                authoring.section("What to improve", "list", "Be specific.")]
        authoring.write_type("retro", "Retros", "work/retros", secs)
        self.assertIn("retro", paths.list_types())
        t = manifest.loads(paths.read_type_fragment("retro"), "retro").types[0]
        self.assertEqual(t.folder, "work/retros")
        self.assertEqual([s.heading for s in t.sections],
                         ["What went well", "What to improve"])
        self.assertEqual(t.sections[0].shape, "list")
        tpl = paths.read_type_template("retro").decode("utf-8")
        self.assertIn("## What went well", tpl)
        self.assertIn("# Retro title —", tpl)

    def test_profile_resolves_bundled_plus_user_type(self):
        authoring.write_type("retro", "Retros", "work/retros",
                             [authoring.section("Notes", "prose", "…")])
        authoring.write_profile("sales", "Sales", ["meeting", "retro"])
        self.assertIn("sales", paths.list_profiles())
        m = manifest.resolve_profile("sales")
        self.assertEqual([t.name for t in m.types], ["meeting", "retro"])
        self.assertEqual(m.project.profile, "sales")

    def test_profile_rejects_unknown_type(self):
        authoring.write_profile("bad", "Bad", ["nope"])
        with self.assertRaises(ValueError):
            manifest.resolve_profile("bad")

    def test_toml_string_escaping_round_trips(self):
        frag = authoring.type_fragment("x", 'Label "Q"', "x", "x.md",
                                       [authoring.section("H", "prose", 'has "quote"')])
        t = manifest.loads(frag, "x").types[0]
        self.assertEqual(t.label, 'Label "Q"')
        self.assertEqual(t.sections[0].prompt, 'has "quote"')


if __name__ == "__main__":
    unittest.main()
