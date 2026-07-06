import os
import tempfile
import unittest

from zplus import manifest, paths

NEW_TEMPLATED = ["decision", "review", "procedure", "agent", "incident"]


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


if __name__ == "__main__":
    unittest.main()
