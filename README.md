# alfred-find-window

An Alfred workflow that finds open Chrome tabs and iTerm2 sessions from one search box.
Bring up Alfred, type `w` followed by a few words and pick a result. The matching tab or
session comes to the front.

A result matches when every word in the query appears somewhere in it:

- **Chrome tabs**: Page title or URL.
- **iTerm2 sessions**: Session name, current working directory or the last 300 lines of
  scrollback.

Title hits rank above URL or directory hits, which rank above scrollback hits. For a
scrollback hit the subtitle shows the most recent matching line.

## Requirements

- macOS with [Alfred 5](https://www.alfredapp.com/) and the Powerpack (needed for workflows).
- Google Chrome and/or iTerm2.
- iTerm2 [shell integration](https://iterm2.com/documentation-shell-integration.html)
  for working directory matching. Without it, names and scrollback still match.
- `python3` (Homebrew in `/opt/homebrew/bin` or the Apple one in `/usr/bin`). Only the
  standard library is used.

## Install

Clone the repo and link the workflow folder into Alfred's preferences:

```sh
git clone git@github.com:gammelby/alfred-find-window.git
cd alfred-find-window
make link
```

`make link` creates a symlink named `user.workflow.window-switcher` in
`~/Library/Application Support/Alfred/Alfred.alfredpreferences/workflows/`. Alfred picks it
up right away and edits in the repo take effect without reinstalling.

If you sync Alfred preferences to a custom folder (Alfred Preferences, Advanced, Set
preferences folder), link into that folder's `workflows/` directory instead:

```sh
make link WORKFLOW_DST="/path/to/Alfred.alfredpreferences/workflows/user.workflow.window-switcher"
```

To remove it again run `make unlink`.

### macOS permissions

The first search asks whether Alfred may control **Google Chrome**, **iTerm2** and
**System Events**. Allow all three. If you dismissed a prompt, re-enable it in System
Settings, Privacy & Security, Automation, Alfred.

## Usage

1. Press your Alfred hotkey (e.g. cmd-space).
2. Type `w` and a space, then one or more words, e.g. `w emudhra` or `w edge-sdk failed`.
3. Press Enter on a result to switch to that tab or session.

You can also start a search from the command line:

```sh
osascript -e 'tell application id "com.runningwithcrayons.Alfred" to search "w emudhra"'
```

## Configuration

Open the workflow in Alfred Preferences and click the `[x]` (Configure Workflow and
Variables) button:

- `SCROLLBACK_LINES`: How many trailing scrollback lines per iTerm2 session are searched.
  Default 300. More lines find older output but make the first search slower.

The keyword `w` can be changed by double-clicking the Script Filter in the workflow
editor.

## How it works

| File | Role |
| --- | --- |
| `window-switcher/info.plist` | Workflow definition: Script Filter (keyword `w`) connected to a Run Script action. |
| `window-switcher/search.py` | Script Filter. Collects a snapshot from both apps in parallel, filters it and prints Alfred JSON. |
| `window-switcher/collect_chrome.js` | JXA script listing every Chrome tab (window id, tab index, title, URL). |
| `window-switcher/collect_iterm.js` | JXA script listing every iTerm2 session (id, name, cwd, scrollback tail). |
| `window-switcher/matching.py` | Pure scoring and Alfred item building, unit tested. |
| `window-switcher/focus.py` | Run Script action. Activates the chosen Chrome tab or iTerm2 session. |

An app that is not running is skipped, so searching never launches Chrome or iTerm2. The
snapshot is cached for 3 seconds in Alfred's workflow cache folder so that each keystroke
does not have to query the apps again. A cold search takes about 1.5 s with around 20 iTerm2
sessions; most of that is reading scrollback.

## Development

Run the unit tests:

```sh
make test
```

Run the Script Filter directly to see the JSON Alfred would get:

```sh
cd window-switcher && python3 search.py some query
```

## Limitations

- Only Chrome and iTerm2. Safari could be added the same way. Firefox has no scripting
  interface for tabs, so switching to a Firefox tab would need a browser extension.
- tmux running inside an iTerm2 session is not looked into: The whole iTerm2 session is one
  result and only what iTerm2 itself holds in its buffer is searched.
