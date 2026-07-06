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


class GraphMermaid(unittest.TestCase):
    def test_edges_from_resolved_refs(self):
        m = manifest.loads('''
[[type]]
name = "agent"
label = "Agents"
folder = "agents"
template = "a.md"
landing = "x"
  [[type.field]]
  name = "runs"
  type = "ref"
  ref = "automation"
  many = true
[[type]]
name = "automation"
label = "Automations"
folder = "automations"
template = "au.md"
landing = "x"
''', source="t")
        bot = Entry("agent", "bot", "Bot", "p", {"runs": ["imp"]}, {})
        imp = Entry("automation", "imp", "Import", "p", {}, {})
        out = render.graph_mermaid(_corpus([bot, imp]), m)
        self.assertIn("```mermaid", out)
        self.assertIn("graph LR", out)
        self.assertIn('bot["Bot"]', out)
        self.assertIn("-->|runs|", out)
        self.assertIn("imp", out)


class Views(unittest.TestCase):
    def _incident_type(self):
        return manifest.loads('''
[[type]]
name = "incident"
label = "Incidents"
folder = "incidents"
template = "i.md"
landing = "x"
  [[type.field]]
  name = "owner"
  type = "owner"
  required = true
  [[type.field]]
  name = "status"
  type = "status"
  values = ["open", "mitigated", "resolved"]
  done = ["resolved"]
''', source="t")

    def test_board_has_columns_and_state_diagram(self):
        t = self._incident_type().types[0]
        e1 = Entry("incident", "a", "A", "p", {"status": "open"}, {})
        e2 = Entry("incident", "b", "B", "p", {"status": "resolved"}, {})
        board = render.board_markdown(t, [e1, e2])
        self.assertIn("### open", board)
        self.assertIn("### resolved", board)
        self.assertIn("stateDiagram", board)
        self.assertIn("[A](a.md)", board)

    def test_action_center_open_uses_done(self):
        m = self._incident_type()
        openi = Entry("incident", "a", "Open one", "p", {"owner": "s", "status": "open"}, {})
        donei = Entry("incident", "b", "Done one", "p", {"owner": "s", "status": "resolved"}, {})
        md = render.action_center_markdown(_corpus([openi, donei]), m)
        self.assertIn("Open one", md)          # open status flagged
        self.assertNotIn("Done one", md)       # resolved (in done) not flagged


if __name__ == "__main__":
    unittest.main()
