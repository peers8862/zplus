import os
import tempfile
import unittest

from zplus import manifest, paths
from zplus.commands import entry


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class Batch(unittest.TestCase):
    def _project(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        # materialize the templates batch needs (as `zplus new` would)
        _write(os.path.join(d, "templates", "automation.md"),
               paths.read_type_template("automation").decode("utf-8"))
        _write(os.path.join(d, "docs", "systems", "billing.md"),
               "---\ntitle: Billing\n---\n# Billing\n")

    def test_csv_creates_templated_entries_with_fields(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            csv_path = os.path.join(d, "autos.csv")
            _write(csv_path,
                   "title,date,owner,status,touches\n"
                   "Invoice Import,2026-03-01,steve,manual,billing\n"
                   "Late Nudge,2026-03-02,steve,assisted,billing\n")
            created = entry.create_from_file(d, "automation", csv_path)
            self.assertEqual(len(created), 2)
            body = open(os.path.join(d, "docs", "automations",
                                     "2026-03-01-invoice-import.md"),
                        encoding="utf-8").read()
            self.assertIn("owner: steve", body)
            self.assertIn("status: manual", body)
            self.assertIn("touches: [billing]", body)   # single value → one-item list

    def test_section_type_gets_plain_pages(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            csv_path = os.path.join(d, "roles.csv")
            _write(csv_path, "title\nBookkeeper\nOffice Manager\n")
            created = entry.create_from_file(d, "role", csv_path)
            self.assertEqual(len(created), 2)
            self.assertTrue(os.path.exists(
                os.path.join(d, "docs", "roles", "bookkeeper.md")))


class OneShotAndJot(unittest.TestCase):
    def _project(self, d):
        with open(os.path.join(d, "zplus.toml"), "w", encoding="utf-8") as f:
            f.write(manifest.resolve_profile_text("administration"))
        _write(os.path.join(d, "templates", "automation.md"),
               paths.read_type_template("automation").decode("utf-8"))
        _write(os.path.join(d, "templates", "idea.md"),
               paths.read_type_template("idea").decode("utf-8"))
        _write(os.path.join(d, "docs", "systems", "billing.md"),
               "---\ntitle: Billing\n---\n# Billing\n")

    def test_one_shot_set_flags(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            created = entry.create_one(d, "automation", "Invoice Import",
                                       sets=["owner=steve", "status=manual", "touches=billing"],
                                       date_str="2026-04-01")
            body = open(os.path.join(d, created[0]), encoding="utf-8").read()
            self.assertIn("owner: steve", body)
            self.assertIn("touches: [billing]", body)

    def test_like_clones_fields(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            entry.create_one(d, "automation", "Src",
                             sets=["owner=steve", "status=manual"], date_str="2026-04-01")
            created = entry.create_one(d, "automation", "Clone",
                                       like="2026-04-01-src", date_str="2026-04-02")
            body = open(os.path.join(d, created[0]), encoding="utf-8").read()
            self.assertIn("owner: steve", body)   # cloned from Src

    def test_jot_creates_idea(self):
        with tempfile.TemporaryDirectory() as d:
            self._project(d)
            created = entry.jot(d, "buy a better coffee machine for the office")
            body = open(os.path.join(d, created[0]), encoding="utf-8").read()
            self.assertIn("buy a better coffee machine", body)


if __name__ == "__main__":
    unittest.main()
