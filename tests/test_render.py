import unittest

from zplus import render, manifest
from zplus.corpus import Entry, Corpus


def _corpus(entries):
    return Corpus(entries=entries, by_slug={e.slug: e for e in entries})


class SpliceRegion(unittest.TestCase):
    def test_appends_then_replaces_idempotently(self):
        once = render.splice_md_region("# Title\n\nprose\n",
                                       render.DASH_BEGIN, render.DASH_END, "BODY-A")
        self.assertIn("prose", once)
        self.assertIn("BODY-A", once)
        twice = render.splice_md_region(once, render.DASH_BEGIN, render.DASH_END, "BODY-B")
        self.assertIn("BODY-B", twice)
        self.assertNotIn("BODY-A", twice)
        self.assertEqual(twice.count(render.DASH_BEGIN), 1)


class DashboardTable(unittest.TestCase):
    def test_columns_from_fields_plus_backlinks(self):
        t = manifest.loads('''
[[type]]
name = "agent"
label = "Agents"
folder = "agents"
template = "agent.md"
landing = "x"
  [[type.field]]
  name = "owner"
  type = "owner"
  [[type.field]]
  name = "runs"
  type = "ref"
  ref = "automation"
  many = true
''', source="t").types[0]
        e = Entry("agent", "bot", "Bot", "p", {"owner": "steve", "runs": ["imp"]}, {})
        e.backlinks = {("incident", "involved"): ["inc-1"]}
        table = render.dashboard_table(t, [e], _corpus([e]))
        self.assertIn("| Entry | owner | runs | Referenced by |", table)
        self.assertIn("[Bot](bot.md)", table)
        self.assertIn("steve", table)
        self.assertIn("imp", table)      # ref list rendered
        self.assertIn("| 1 |", table)    # one inbound backlink


class ActionCenter(unittest.TestCase):
    def _m(self):
        return manifest.loads('''
[[type]]
name = "incident"
label = "Incidents"
folder = "incidents"
template = "incident.md"
landing = "x"
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["open", "resolved"]
''', source="t")

    def test_flags_unowned_open_and_dangling(self):
        m = self._m()
        e = Entry("incident", "inc-1", "Outage", "p",
                  {"owner": "", "status": "open"}, {})
        md = render.action_center_markdown(_corpus([e]), m)
        self.assertIn("Needs an owner", md)
        self.assertIn("Open / in progress", md)
        self.assertIn("../incidents/inc-1.md", md)

    def test_corpus_to_dict_shape(self):
        e = Entry("incident", "inc-1", "Outage", "p", {"status": "open"}, {})
        e.backlinks = {("automation", "touches"): ["a1"]}
        d = render.corpus_to_dict(_corpus([e]))
        self.assertEqual(d["entries"][0]["slug"], "inc-1")
        self.assertEqual(d["entries"][0]["backlinks"], {"automation.touches": ["a1"]})


if __name__ == "__main__":
    unittest.main()
