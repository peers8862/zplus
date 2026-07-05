import os
import tempfile
import unittest

from zplus import core


class TestCore(unittest.TestCase):
    def test_slugify_basic(self):
        self.assertEqual(core.slugify("Supplier onboarding is slow"),
                         "supplier-onboarding-is-slow")

    def test_slugify_punctuation_and_edges(self):
        self.assertEqual(core.slugify("  R&D: Phase 2!! "), "r-d-phase-2")

    def test_collision_first_is_unsuffixed(self):
        with tempfile.TemporaryDirectory() as d:
            path, word = core.resolve_collision(d, "2026-07-05", "standup")
            self.assertTrue(path.endswith("2026-07-05-standup.md"))
            self.assertIsNone(word)

    def test_collision_sequences_word_forms(self):
        with tempfile.TemporaryDirectory() as d:
            open(os.path.join(d, "2026-07-05-standup.md"), "w").close()
            path, word = core.resolve_collision(d, "2026-07-05", "standup")
            self.assertTrue(path.endswith("2026-07-05-standup-TWO.md"))
            self.assertEqual(word, "TWO")

    def test_stamp_fills_date_title_and_h1(self):
        tpl = "---\ndate: YYYY-MM-DD\ntitle: Challenge title\n---\n# Challenge title — YYYY-MM-DD\n\n## The issue\n"
        out = core.stamp(tpl, "Supplier sync", "2026-07-05", None)
        self.assertIn("date: 2026-07-05", out)
        self.assertIn("title: Supplier sync", out)
        self.assertIn("# Supplier sync — 2026-07-05", out)

    def test_stamp_suffix_only_touches_h1(self):
        tpl = "---\ntitle: Challenge title\n---\n# Challenge title — YYYY-MM-DD\n"
        out = core.stamp(tpl, "Supplier sync", "2026-07-05", "TWO")
        self.assertIn("title: Supplier sync", out)
        self.assertIn("# Supplier sync (TWO) — 2026-07-05", out)

    def test_section_shape(self):
        self.assertEqual(core.section_shape("- [ ]"), "task")
        self.assertEqual(core.section_shape("- placeholder"), "list")
        self.assertEqual(core.section_shape("-"), "list")
        self.assertEqual(core.section_shape("The focused problem."), "prose")

    def test_render_body_by_shape(self):
        self.assertEqual(core.render_body(["a", "b"], "list"), "- a\n- b")
        self.assertEqual(core.render_body(["do x"], "task"), "- [ ] do x")
        self.assertEqual(core.render_body(["l1", "l2"], "prose"), "l1\nl2")

    def test_render_frontmatter_lists(self):
        self.assertEqual(core.render_attendees(["Morgen", "Priya"]),
                         "attendees: [Morgen, Priya]")
        self.assertEqual(core.render_tags(["Foundation", "Ops"]),
                         "tags:\n  - Foundation\n  - Ops")


if __name__ == "__main__":
    unittest.main()
