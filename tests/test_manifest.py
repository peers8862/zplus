import unittest

from zplus import manifest


class TestDefaultManifest(unittest.TestCase):
    def setUp(self):
        self.m = manifest.load_default()

    def test_eight_types_in_order(self):
        names = [t.name for t in self.m.types]
        self.assertEqual(names, ["challenge", "meeting", "call", "idea",
                                 "reference", "timeline", "automation", "operation"])

    def test_type_registry_fields(self):
        idea = self.m.type_by_name("idea")
        self.assertEqual(idea.label, "Ideas")
        self.assertEqual(idea.folder, "ideas")
        self.assertEqual(idea.template, "idea.md")

    def test_challenge_sections_all_prose(self):
        ch = self.m.type_by_name("challenge")
        self.assertEqual(len(ch.sections), 7)
        self.assertTrue(all(s.shape == "prose" for s in ch.sections))
        self.assertEqual(ch.sections[0].heading, "The issue")

    def test_meeting_action_items_is_task(self):
        mtg = self.m.type_by_name("meeting")
        shapes = {s.heading: s.shape for s in mtg.sections}
        self.assertEqual(shapes["Action items"], "task")
        self.assertEqual(shapes["Agenda"], "list")

    def test_timeline_has_no_sections(self):
        self.assertEqual(self.m.type_by_name("timeline").sections, [])

    def test_project_defaults(self):
        self.assertEqual(self.m.project.managed_nav, "ZPLUS_TYPES")
        self.assertEqual(self.m.project.deploy_branch, "gh-pages")


class TestValidation(unittest.TestCase):
    def test_duplicate_name_rejected(self):
        text = ('[[type]]\nname="x"\nlabel="X"\nfolder="x"\ntemplate="x.md"\n'
                '[[type]]\nname="x"\nlabel="Y"\nfolder="y"\ntemplate="y.md"\n')
        with self.assertRaises(ValueError):
            manifest.loads(text)

    def test_invalid_shape_rejected(self):
        text = ('[[type]]\nname="x"\nlabel="X"\nfolder="x"\ntemplate="x.md"\n'
                '[[type.section]]\nheading="H"\nshape="bogus"\n')
        with self.assertRaises(ValueError):
            manifest.loads(text)

    def test_missing_required_field_rejected(self):
        text = '[[type]]\nname="x"\nlabel="X"\nfolder="x"\n'  # no template
        with self.assertRaises(ValueError):
            manifest.loads(text)


class TestProfiles(unittest.TestCase):
    def test_projecthub_available(self):
        self.assertIn("projecthub", manifest.available_profiles())

    def test_resolve_projecthub_is_selfcontained(self):
        text = manifest.resolve_profile_text("projecthub")
        self.assertIn("[project]", text)
        self.assertIn('profile = "projecthub"', text)
        m = manifest.loads(text, "projecthub")
        self.assertEqual(len(m.types), 8)
        self.assertEqual(m.project.profile, "projecthub")
        self.assertEqual([t.name for t in m.types][:2], ["challenge", "meeting"])

    def test_missing_profile_raises(self):
        with self.assertRaises(Exception):
            manifest.resolve_profile_text("does-not-exist")

    def test_every_library_fragment_parses(self):
        from zplus import paths
        for name in paths.list_types():
            m = manifest.loads(paths.read_type_fragment(name), name)
            self.assertEqual(m.types[0].name, name)


if __name__ == "__main__":
    unittest.main()
