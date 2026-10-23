// Print every iTerm2 session as a JSON array, including the tail of its scrollback.
// argv[0]: number of trailing lines to keep.
// Ids, names and contents use bulk reads; the cwd variable can only be read per session.
function run(argv) {
  const keep = parseInt(argv[0] || "300", 10);
  const iterm = Application("iTerm2");
  const sessions = iterm.windows.tabs.sessions;
  const ids = sessions.id();
  const names = sessions.name();
  const contents = sessions.contents();
  const windows = iterm.windows();
  const out = [];
  ids.forEach((tabs, w) => {
    const tabObjs = windows[w].tabs();
    tabs.forEach((sessionIds, t) => {
      const sessionObjs = tabObjs[t].sessions();
      sessionIds.forEach((id, s) => {
        const lines = contents[w][t][s].split("\n");
        while (lines.length && lines[lines.length - 1].trim() === "") lines.pop();
        out.push({
          source: "iterm",
          session_id: id,
          name: names[w][t][s],
          cwd: sessionObjs[s].variable({ named: "session.path" }) || "",
          tail: lines.slice(-keep).join("\n"),
        });
      });
    });
  });
  return JSON.stringify(out);
}
