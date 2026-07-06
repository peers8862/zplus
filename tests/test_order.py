import os
import tempfile
import unittest

from zplus import manifest
from zplus.commands import nav


def _write(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class OrderStrategy(unittest.TestCase):
    def test_alpha_order_sorts_by_title_not_filename(self):
        # date-prefixed filenames, but titles order the other way → alpha uses titles
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "procedures", "2026-01-01-zeta.md"), "# Zeta\n")
            _write(os.path.join(d, "procedures", "2026-02-02-alpha.md"), "# Alpha\n")
            _write(os.path.join(d, "procedures", "index.md"), "# Procedures\n")
            paths = nav.ordered_paths(d, "procedures", "alpha")
            self.assertEqual(paths[0], "procedures/index.md")
            self.assertEqual(paths[1:], ["procedures/2026-02-02-alpha.md",
                                         "procedures/2026-01-01-zeta.md"])

    def test_date_desc_default(self):
        with tempfile.TemporaryDirectory() as d:
            _write(os.path.join(d, "log", "2026-01-01-old.md"), "# Old\n")
            _write(os.path.join(d, "log", "2026-02-02-new.md"), "# New\n")
            paths = nav.ordered_paths(d, "log", "date-desc")
            self.assertEqual(paths, ["log/2026-02-02-new.md", "log/2026-01-01-old.md"])

    def test_procedure_type_declares_alpha(self):
        m = manifest.resolve_profile("administration")
        proc = next(t for t in m.types if t.name == "procedure")
        self.assertEqual(proc.order, "alpha")


if __name__ == "__main__":
    unittest.main()
