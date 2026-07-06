import json
import os
import tempfile
import unittest

from zplus import manifest
from zplus.commands import derived


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class GenDerived(unittest.TestCase):
    def _project(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        _write(os.path.join(d, "docs", "automations", "index.md"),
               "# Automations\n\nAutomations.\n")
        _write(os.path.join(d, "docs", "mission-control", "index.md"),
               "# Mission Control\n\nStart here.\n")
        _write(os.path.join(d, "docs", "systems", "billing.md"),
               "---\ntitle: Billing\n---\n# Billing\n")
        _write(os.path.join(d, "docs", "automations", "invoice-import.md"),
               "---\ntitle: Invoice Import\nowner: steve\n"
               "status: proposed\ntouches: [billing]\n---\n# Invoice Import\n")

    def test_writes_dashboard_action_center_and_corpus_json(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            self.assertEqual(derived.gen_derived(d), 0)
            landing = open(os.path.join(d, "docs", "automations", "index.md"),
                           encoding="utf-8").read()
            self.assertIn("Automations.", landing)          # prose preserved
            self.assertIn("[Invoice Import](invoice-import.md)", landing)  # dashboard
            ac = os.path.join(d, "docs", "mission-control", "action-center.md")
            self.assertTrue(os.path.exists(ac))
            self.assertIn("status `proposed`", open(ac, encoding="utf-8").read())
            data = json.load(open(os.path.join(d, "corpus.json"), encoding="utf-8"))
            slugs = {e["slug"] for e in data["entries"]}
            self.assertIn("invoice-import", slugs)

    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            derived.gen_derived(d)
            first = open(os.path.join(d, "docs", "automations", "index.md"),
                         encoding="utf-8").read()
            derived.gen_derived(d)
            second = open(os.path.join(d, "docs", "automations", "index.md"),
                          encoding="utf-8").read()
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
