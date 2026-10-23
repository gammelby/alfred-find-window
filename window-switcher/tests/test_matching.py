import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from matching import search  # noqa: E402

TAB = {"source": "chrome", "window_id": 7, "tab_index": 2,
       "title": "Nabto Edge docs", "url": "https://docs.nabto.com/developer"}
TERM = {"source": "iterm", "session_id": "ABC", "name": "-bash — ~/git/edge-sdk",
        "cwd": "/Users/ug/git/edge-sdk",
        "tail": "make test\nFAILED: tunnel_test\nugs-mbp$ "}
ENTRIES = [TAB, TERM]


class SearchTest(unittest.TestCase):
    def test_empty_query_returns_nothing(self):
        self.assertEqual(search(ENTRIES, "  "), [])

    def test_title_beats_location(self):
        # "nabto" is in the tab title but only in the session's cwd.
        term = dict(TERM, name="-bash", cwd="/Users/ug/git/nabto-sdk")
        items = search([term, TAB], "nabto")
        self.assertEqual([i["title"] for i in items], ["Nabto Edge docs", "nabto-sdk"])

    def test_all_words_must_match(self):
        self.assertEqual(search(ENTRIES, "nabto nonexistent"), [])

    def test_case_insensitive_url_match(self):
        items = search(ENTRIES, "DEVELOPER")
        self.assertEqual(json.loads(items[0]["arg"]),
                         {"source": "chrome", "window_id": 7, "tab_index": 2})

    def test_cwd_match_shows_cwd(self):
        items = search(ENTRIES, "edge-sdk")
        self.assertEqual(items[0]["title"], "edge-sdk")
        self.assertEqual(items[0]["subtitle"], "/Users/ug/git/edge-sdk")

    def test_scrollback_match_shows_line(self):
        items = search(ENTRIES, "tunnel_test")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["subtitle"], "FAILED: tunnel_test")
        self.assertEqual(json.loads(items[0]["arg"]),
                         {"source": "iterm", "session_id": "ABC"})

    def test_ties_keep_window_order(self):
        other = dict(TAB, tab_index=3, title="Edge other")
        items = search([TAB, other], "edge")
        self.assertEqual([json.loads(i["arg"])["tab_index"] for i in items], [2, 3])


if __name__ == "__main__":
    unittest.main()
