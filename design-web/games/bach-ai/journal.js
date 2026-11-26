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
// "Trở lại" on every journal page (not the lobby: its own tabs already go back): an icon tab like the lobby's corner tabs.
addEventListener("DOMContentLoaded", () => {
  if (!document.querySelector(".book") || /screen-lobby/.test(location.pathname)) return;
  const el = document.createElement("div");
  el.className = "back-tab";
  el.title = "Trở lại (Esc)";
  el.innerHTML = '<img src="assets/lobby/back.svg" alt="Trở lại">';
  el.onclick = () => Journal.back();
  document.getElementById("game").appendChild(el);
  document.body.classList.add("has-back");
});
