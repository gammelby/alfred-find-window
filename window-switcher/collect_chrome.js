// Print every Chrome tab as a JSON array. Uses bulk property reads for speed.
function run() {
  const chrome = Application("Google Chrome");
  const ids = chrome.windows.id();
  const titles = chrome.windows.tabs.title();
  const urls = chrome.windows.tabs.url();
  const out = [];
  ids.forEach((windowId, w) => {
    titles[w].forEach((title, t) => {
      out.push({
        source: "chrome",
        window_id: windowId,
        tab_index: t + 1,
        title: title,
        url: urls[w][t],
      });
    });
  });
  return JSON.stringify(out);
}
