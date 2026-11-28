// Shared by the "Sổ hành trình" screens: navigation for the web flow (flow.html) and a few drawing helpers.
// In the flow, a screen asks its host to go somewhere: Journal.go("equipment"), Journal.back(); alone, nothing happens.
const Journal = {
  go(screen, query) { try { sessionStorage.setItem("flip", "1"); } catch (e) {} if (parent !== window) parent.postMessage({ go: screen, query: query || "" }, "*"); },
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
// Page turn (user 2026-11-28: "không thấy hiệu ứng kiểu lật trang"): entering a journal screen, a paper leaf sweeps
// from the right page over the spine to the left in 0.32 s (8 whole-pixel steps: no blur, no rotation). Plays after
// Journal.go, on ?flip=1, and on F to try it again.
function journalFlip() {
  const book = document.querySelector(".book");
  if (!book) return;
  const leaf = document.createElement("div");
  leaf.className = "leaf";
  book.appendChild(leaf);
  const steps = 8, half = 550;
  let k = 0;
  const tick = () => {
    k++;
    const t = k / steps;   // 0..1: the leaf narrows to the spine over the right page, then opens over the left
    const w = Math.round(t < 0.5 ? half * (1 - t * 2) : half * (t * 2 - 1));
    leaf.style.width = Math.max(4, w) + "px";
    leaf.style.left = (t < 0.5 ? half : half - w) + "px";
    leaf.style.background = t < 0.5 ? "#e8d8b0" : "#d8c498";
    if (k < steps) setTimeout(tick, 40); else leaf.remove();
  };
  leaf.style.left = half + "px"; leaf.style.width = half + "px";
  setTimeout(tick, 40);
}
addEventListener("DOMContentLoaded", () => {
  const st = document.createElement("style");
  st.textContent = ".leaf { position: absolute; top: 0; height: 640px; z-index: 20; border: 4px solid #8a6a3a; box-shadow: 0 0 0 2px #0003; pointer-events: none; }";
  document.head.appendChild(st);
  let go = /[?&]flip=1/.test(location.search);
  try { go = go || sessionStorage.getItem("flip") === "1"; sessionStorage.removeItem("flip"); } catch (e) {}
  if (go) journalFlip();
});
addEventListener("keydown", (ev) => { if (ev.key === "f" || ev.key === "F") journalFlip(); });
