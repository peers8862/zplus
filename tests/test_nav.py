import os
import tempfile
import unittest

from zplus import manifest
from zplus.commands import nav


def _touch(d, folder, *names):
    os.makedirs(os.path.join(d, folder), exist_ok=True)
    for n in names:
        open(os.path.join(d, folder, n), "w").close()


class TestOrdering(unittest.TestCase):
    def test_index_first_then_newest(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "timeline", "index.md", "2026-07-02-a.md", "2026-07-05-b.md")
            self.assertEqual(
                nav.ordered_paths(d, "timeline"),
                ["timeline/index.md", "timeline/2026-07-05-b.md", "timeline/2026-07-02-a.md"])

    def test_build_region_skips_empty_types(self):
        with tempfile.TemporaryDirectory() as d:
            _touch(d, "ideas", "index.md")
            m = manifest.loads(
                '[[type]]\nname="idea"\nlabel="Ideas"\nfolder="ideas"\ntemplate="idea.md"\n'
                '[[type]]\nname="call"\nlabel="Calls"\nfolder="work/calls"\ntemplate="call.md"\n')
            body = nav.build_region_body(m, d)
            self.assertIn('"Ideas"', body)
            self.assertNotIn('"Calls"', body)


class TestRegenerate(unittest.TestCase):
    def test_regenerate_populates_region(self):
        with tempfile.TemporaryDirectory() as proj:
            _touch(os.path.join(proj, "docs"), "ideas", "index.md")
            with open(os.path.join(proj, "zplus.toml"), "w") as f:
                f.write('[project]\nmanaged_nav="ZPLUS_TYPES"\n'
                        '[[type]]\nname="idea"\nlabel="Ideas"\nfolder="ideas"\ntemplate="idea.md"\n')
            with open(os.path.join(proj, "zensical.toml"), "w") as f:
                f.write('[project]\nsite_name = "X"\n')
            self.assertEqual(nav.regenerate(proj), 1)
            toml = open(os.path.join(proj, "zensical.toml")).read()
            self.assertIn('{ "Ideas" = ["ideas/index.md"] }', toml)


if __name__ == "__main__":
    unittest.main()
