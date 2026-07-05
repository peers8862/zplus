import unittest

from zplus.patch import gitignore, toml_nav


class TestGitignore(unittest.TestCase):
    def test_append_then_idempotent(self):
        first = gitignore.ensure_block("*.log\n")
        self.assertIn("/site/", first)
        self.assertIn(gitignore.BEGIN, first)
        self.assertEqual(first, gitignore.ensure_block(first))  # idempotent

    def test_empty_input(self):
        self.assertTrue(gitignore.ensure_block("").startswith(gitignore.BEGIN))


class TestTomlNav(unittest.TestCase):
    def test_creates_nav_when_absent(self):
        out = toml_nav.ensure_nav_region('[project]\nsite_name = "X"\n', "ZPLUS_TYPES")
        self.assertIn("nav = [", out)
        self.assertIn(">>> ZPLUS_TYPES", out)
        self.assertEqual(out, toml_nav.ensure_nav_region(out, "ZPLUS_TYPES"))  # idempotent

    def test_inserts_into_active_nav_without_duplicating(self):
        text = '[project]\nnav = [\n  { "Home" = ["index.md"] },\n]\n'
        out = toml_nav.ensure_nav_region(text, "ZPLUS_TYPES")
        self.assertIn(">>> ZPLUS_TYPES", out)
        self.assertEqual(out.count("nav = ["), 1)

    def test_splice_fills_and_replaces(self):
        base = toml_nav.ensure_nav_region('[project]\nsite="x"\n', "ZPLUS_TYPES")
        filled = toml_nav.splice_region(
            base, "ZPLUS_TYPES", '  { "Challenges" = ["business-challenges/index.md"] },')
        self.assertIn("Challenges", filled)
        refilled = toml_nav.splice_region(
            filled, "ZPLUS_TYPES", '  { "Ideas" = ["ideas/index.md"] },')
        self.assertIn("Ideas", refilled)
        self.assertNotIn("Challenges", refilled)  # old body replaced, not appended


if __name__ == "__main__":
    unittest.main()
