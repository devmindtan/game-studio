// Shared by the "Sổ hành trình" screens: navigation for the web flow (flow.html) and a few drawing helpers.
// In the flow, a screen asks its host to go somewhere: Journal.go("equipment"), Journal.back(); alone, nothing happens.
const Journal = {
  go(screen, query) { if (parent !== window) parent.postMessage({ go: screen, query: query || "" }, "*"); },
  back() { if (parent !== window) parent.postMessage({ back: true }, "*"); },
  G: "../../../games/bach-ai/assets/",
  SP: "../../../games/bach-ai/assets/sprites/custom/",
  json(p) { return fetch(this.G + p).then((r) => r.json()); },
  // a list moved with ↑/↓ (or ←/→ when horizontal); onPick(i) on Enter; returns {get, set}
  list(n, draw, onPick, horizontal) {
    let sel = 0;
    addEventListener("keydown", (ev) => {
      const next = horizontal ? ["ArrowRight", "d"] : ["ArrowDown", "s"], prev = horizontal ? ["ArrowLeft", "a"] : ["ArrowUp", "w"];
      if (next.includes(ev.key)) sel = (sel + 1) % n();
      else if (prev.includes(ev.key)) sel = (sel + n() - 1) % n();
      else if (ev.key === "Enter" || ev.key === " ") { onPick && onPick(sel); return; }
      else return;
      ev.preventDefault(); draw(sel);
    });
    return { get: () => sel, set: (i) => { sel = i; draw(sel); } };
  },
};
addEventListener("keydown", (ev) => { if (ev.key === "Escape") Journal.back(); });
// "Trở lại" on every journal page (not the lobby: its ribbon already changes character). ?back=b shows direction B.
addEventListener("DOMContentLoaded", () => {
  const book = document.querySelector(".book");
  if (!book || /screen-lobby/.test(location.pathname)) return;
  const b = new URLSearchParams(location.search).get("back") === "b";
  const el = document.createElement("div");
  el.className = b ? "back-b" : "back-a";
  el.innerHTML = b ? "◂ Trở lại <kbd>· Esc</kbd>" : "Trở lại";
  el.onclick = () => Journal.back();
  (b ? document.getElementById("game") : document.getElementById("game")).appendChild(el);
  if (b) document.body.classList.add("has-back-b");
});
