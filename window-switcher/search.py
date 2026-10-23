"""Alfred Script Filter: list Chrome tabs and iTerm2 sessions matching the query."""

import json
import os
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

from matching import search

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_TTL = 3.0
COLLECTORS = {
    "Google Chrome": "collect_chrome.js",
    "iTerm2": "collect_iterm.js",
}


def _is_running(app):
    # Asking System Events avoids launching the app just by scripting it.
    script = f'Application("System Events").processes.whose({{name: "{app}"}}).length > 0'
    out = subprocess.run(
        ["osascript", "-l", "JavaScript", "-e", script],
        capture_output=True, text=True,
    )
    return out.stdout.strip() == "true"


def _collect(app, script):
    if not _is_running(app):
        return []
    args = ["osascript", "-l", "JavaScript", os.path.join(HERE, script)]
    if app == "iTerm2":
        args.append(os.environ.get("SCROLLBACK_LINES", "300"))
    out = subprocess.run(args, capture_output=True, text=True, timeout=10)
    if out.returncode != 0:
        print(f"{script}: {out.stderr.strip()}", file=sys.stderr)
        return []
    return json.loads(out.stdout)


def _cache_path():
    base = os.environ.get("alfred_workflow_cache") or tempfile.gettempdir()
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "window-switcher-snapshot.json")


def snapshot():
    """All entries from all sources, cached briefly so typing stays fast."""
    path = _cache_path()
    try:
        if time.time() - os.path.getmtime(path) < CACHE_TTL:
            with open(path) as f:
                return json.load(f)
    except (OSError, ValueError):
        pass
    with ThreadPoolExecutor() as pool:
        results = pool.map(lambda kv: _collect(*kv), COLLECTORS.items())
    entries = [e for result in results for e in result]
    with open(path, "w") as f:
        json.dump(entries, f)
    return entries


def main():
    query = " ".join(sys.argv[1:])
    items = search(snapshot(), query)
    if not items:
        items = [{"title": "No matching windows", "subtitle": query, "valid": False}]
    json.dump({"items": items}, sys.stdout)


if __name__ == "__main__":
    main()
