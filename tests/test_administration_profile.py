import os
import tempfile
import unittest

from zplus import manifest, paths

NEW_TEMPLATED = ["decision", "review", "procedure", "agent", "incident"]

NEW_SECTIONS = ["mission-control", "company", "how-we-run", "operating-rhythm",
                "automation-program", "knowledge-base", "site-docs", "role",
                "system", "policy", "vendor", "constellation", "objective"]


class TemplatedTypes(unittest.TestCase):
    def test_each_parses_as_templated_with_template_and_valid_shapes(self):
        for name in NEW_TEMPLATED:
            frag = paths.read_type_fragment(name)          # raises if dir absent
            m = manifest.loads(frag, source=name)          # raises on invalid shape
            self.assertEqual(len(m.types), 1)
            t = m.types[0]
            self.assertEqual(t.name, name)
            self.assertTrue(t.templated)
            self.assertTrue(t.template, f"{name} needs a template")
            self.assertTrue(t.landing, f"{name} needs a landing")
            self.assertTrue(t.sections, f"{name} needs sections")

    def test_each_template_file_present_with_headings(self):
        for name in NEW_TEMPLATED:
            body = paths.read_type_template(name).decode("utf-8")
            self.assertIn("date: YYYY-MM-DD", body)
            self.assertIn("## ", body)


class SectionTypes(unittest.TestCase):
    def test_each_parses_as_section_with_landing(self):
        for name in NEW_SECTIONS:
            frag = paths.read_type_fragment(name)
            m = manifest.loads(frag, source=name)
            self.assertEqual(len(m.types), 1)
            t = m.types[0]
            self.assertEqual(t.name, name)
            self.assertFalse(t.templated, f"{name} must be a section (templated=false)")
            self.assertFalse(t.template, f"{name} must not declare a template")
            self.assertTrue(t.landing, f"{name} needs a landing")


EXPECTED_ORDER = [
    "mission-control", "constellation",
    "company", "role", "objective",
    "how-we-run", "procedure", "policy", "system", "vendor",
    "operating-rhythm", "review", "meeting", "decision",
    "automation-program", "agent", "automation", "incident", "idea",
    "knowledge-base", "reference",
    "site-docs",
]


class AdministrationProfile(unittest.TestCase):
    def test_profile_is_available(self):
        self.assertIn("administration", manifest.available_profiles())

    def test_resolves_to_expected_types_in_order(self):
        m = manifest.resolve_profile("administration")
        self.assertEqual([t.name for t in m.types], EXPECTED_ORDER)
        self.assertEqual(m.project.profile, "administration")

    def test_every_type_has_a_landing(self):
        m = manifest.resolve_profile("administration")
        for t in m.types:
            self.assertTrue(t.landing, f"{t.name} missing landing")


class LandingMaterialization(unittest.TestCase):
    def test_apply_writes_a_landing_index_per_type(self):
        from zplus.commands import apply as apply_cmd
        m = manifest.resolve_profile("administration")
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "docs"))
            with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
                f.write(manifest.resolve_profile_text("administration"))
            written = apply_cmd._materialize_landings(d)
            self.assertEqual(len(written), len(m.types))
            for t in m.types:
                idx = os.path.join(d, "docs", t.folder, "index.md")
                self.assertTrue(os.path.exists(idx), f"missing landing for {t.name}")
                self.assertIn(t.label, open(idx, encoding="utf-8").read())


if __name__ == "__main__":
    unittest.main()
