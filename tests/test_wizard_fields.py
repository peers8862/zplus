import os
import tempfile
import unittest
from unittest import mock

from zplus import core


class SetFrontMatter(unittest.TestCase):
    def test_replaces_scalar_and_list(self):
        text = ("---\ndate: YYYY-MM-DD\ntitle: Bot\nowner:\nruns: []\n---\n# Bot\n")
        text = core.set_front_matter_value(text, "owner", "steve")
        text = core.set_front_matter_value(text, "runs", ["a", "b"])
        self.assertIn("owner: steve", text)
        self.assertIn("runs: [a, b]", text)

    def test_absent_key_is_noop(self):
        text = "---\ntitle: X\n---\n# X\n"
        self.assertEqual(core.set_front_matter_value(text, "owner", "steve"), text)


if __name__ == "__main__":
    unittest.main()
