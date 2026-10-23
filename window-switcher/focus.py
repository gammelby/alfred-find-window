"""Alfred action: bring the Chrome tab or iTerm2 session named by the argument forward."""

import json
import subprocess
import sys

CHROME = """
function run(argv) {
  const chrome = Application("Google Chrome");
  const win = chrome.windows.byId(parseInt(argv[0], 10));
  win.activeTabIndex = parseInt(argv[1], 10);
  win.index = 1;
  chrome.activate();
}
"""

ITERM = """
function run(argv) {
  const iterm = Application("iTerm2");
  for (const win of iterm.windows()) {
    for (const tab of win.tabs()) {
      for (const session of tab.sessions()) {
        if (session.id() === argv[0]) {
          tab.select();
          session.select();
          win.select();
          iterm.activate();
          return;
        }
      }
    }
  }
}
"""


def main():
    target = json.loads(sys.argv[1])
    if target["source"] == "chrome":
        script, args = CHROME, [str(target["window_id"]), str(target["tab_index"])]
    else:
        script, args = ITERM, [target["session_id"]]
    subprocess.run(["osascript", "-l", "JavaScript", "-e", script, *args], check=True)


if __name__ == "__main__":
    main()
