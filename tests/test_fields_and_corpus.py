import os
import tempfile
import unittest

from zplus import core


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


if __name__ == "__main__":
    unittest.main()
