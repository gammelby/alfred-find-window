"""Score snapshot entries against a query and turn hits into Alfred items."""

import json
import os

TITLE_SCORE = 3
LOCATION_SCORE = 2
SCROLLBACK_SCORE = 1
SUBTITLE_MAX = 120

CHROME_ICON = "/Applications/Google Chrome.app"
ITERM_ICON = "/Applications/iTerm.app"


def _fields(entry):
    """Return (title text, location text, scrollback text) for an entry."""
    if entry["source"] == "chrome":
        return entry["title"], entry["url"], ""
    return entry["name"], entry["cwd"], entry["tail"]


def _last_matching_line(text, words):
    """Most recent scrollback line containing any query word, trimmed."""
    for line in reversed(text.splitlines()):
        lower = line.lower()
        if any(w in lower for w in words):
            return line.strip()
    return ""


def score(entry, words):
    """Return a score for entry, or 0 if some query word matches nowhere."""
    title, location, scrollback = (f.lower() for f in _fields(entry))
    total = 0
    for word in words:
        if word in title:
            total += TITLE_SCORE
        elif word in location:
            total += LOCATION_SCORE
        elif word in scrollback:
            total += SCROLLBACK_SCORE
        else:
            return 0
    return total


def _truncate(text):
    return text if len(text) <= SUBTITLE_MAX else text[: SUBTITLE_MAX - 1] + "…"


def to_item(entry, words):
    """Build one Alfred Script Filter item for entry."""
    if entry["source"] == "chrome":
        target = {"source": "chrome", "window_id": entry["window_id"], "tab_index": entry["tab_index"]}
        title = entry["title"] or entry["url"]
        subtitle = entry["url"]
        icon = CHROME_ICON
    else:
        target = {"source": "iterm", "session_id": entry["session_id"]}
        cwd = entry["cwd"]
        title = os.path.basename(cwd.rstrip("/")) or cwd or entry["name"]
        _, location, _ = (f.lower() for f in _fields(entry))
        if all(w in entry["name"].lower() or w in location for w in words):
            subtitle = cwd or entry["name"]
        else:
            subtitle = _last_matching_line(entry["tail"], words) or cwd
        icon = ITERM_ICON
    return {
        "title": title,
        "subtitle": _truncate(subtitle),
        "arg": json.dumps(target),
        "icon": {"type": "fileicon", "path": icon},
    }


def search(entries, query):
    """Return Alfred items for entries matching every word in query, best first."""
    words = query.lower().split()
    if not words:
        return []
    scored = [(score(e, words), i, e) for i, e in enumerate(entries)]
    hits = [s for s in scored if s[0] > 0]
    hits.sort(key=lambda s: (-s[0], s[1]))
    return [to_item(e, words) for _, _, e in hits]
