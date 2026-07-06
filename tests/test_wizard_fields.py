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


from zplus import manifest
from zplus.commands import entry


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class FillFields(unittest.TestCase):
    def _project(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\n---\n# Invoice Import\n")

    def test_prompts_status_and_ref_and_injects(self):
        m = manifest.resolve_profile("administration")
        agent = next(t for t in m.types if t.name == "agent")
        template = ("---\ndate: YYYY-MM-DD\ntitle: Bot\nowner:\nstatus:\n"
                    "runs: []\ngoverned_by: []\n---\n# Bot\n")
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            answers = iter(["steve", "3", "1", "", ""])
            with mock.patch("builtins.input", lambda *_a: next(answers)):
                out = entry.fill_fields(template, agent, d)
        self.assertIn("owner: steve", out)
        self.assertIn("status: supervised", out)       # 3rd maturity value
        self.assertIn("runs: [invoice-import]", out)   # picked existing automation


if __name__ == "__main__":
    unittest.main()
