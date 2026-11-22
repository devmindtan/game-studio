(() => {
  const params = new URLSearchParams(location.search);
  const body = document.body;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  const variant = params.get("variant") === "b" ? "b" : "a";
  let state = params.get("state") === "menu" ? "menu" : "gate";
  body.dataset.variant = variant;
  body.dataset.state = state;
  body.classList.toggle("show-safe", params.get("safe") === "1");
  body.classList.toggle("show-grid", params.get("grid") === "1");
  body.classList.toggle("still", params.get("still") === "1");

  const buttons = [...document.querySelectorAll(".menu .btn")];
  const toast = document.querySelector(".toast");
  let focusIndex = 0;
  let toastTimer = 0;

  function setState(next, moveFocus = true) {
    state = next;
    body.dataset.state = next;
    if (next === "menu") {
      if (moveFocus) focus(0);
    } else {
      buttons.forEach((b) => b.classList.remove("focused"));
      document.activeElement?.blur?.();
    }
  }

  function focus(index) {
    if (!buttons.length) return;
    focusIndex = (index + buttons.length) % buttons.length;
    buttons.forEach((b, i) => b.classList.toggle("focused", i === focusIndex));
    buttons[focusIndex].focus({ preventScroll: true });
  }

  function activate(index) {
    const b = buttons[index];
    if (!b) return;
    showToast("Bản thử: " + b.dataset.action);
  }

  function showToast(text) {
    toast.textContent = text;
    toast.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("show"), 1700);
  }

  // ---- rune rings -----------------------------------------------------------
  const rings = [...document.querySelectorAll(".rune-ring")];
  rings.forEach((ring) => {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < 24; i++) frag.appendChild(document.createElement("i"));
    ring.appendChild(frag);
  });

  const dots = rings.map((ring) => [...ring.children]);
  function paintRunes(t) {
    dots.forEach((list, r) => {
      const phase = t * 0.35 + r * 1.7;
      list.forEach((dot, i) => {
        const a = (i * Math.PI * 2) / 24 + phase;
        dot.style.left = 50 + Math.cos(a) * 46 + "%";
        dot.style.top = 50 + Math.sin(a) * 38 + "%";
        dot.style.opacity = (0.5 + 0.5 * Math.sin(t * 2 + i * 0.8)).toFixed(3);
      });
    });
  }

  let start = performance.now();
  function tick(now) {
    paintRunes((now - start) / 1000);
    if (!reduce) requestAnimationFrame(tick);
  }
  paintRunes(0);
  if (!reduce) requestAnimationFrame(tick);

  // ---- input ----------------------------------------------------------------
  addEventListener("keydown", (e) => {
    if (state === "gate") {
      if (e.key === "Tab" || e.key === "Shift" || e.key === "Control" || e.key === "Alt" || e.key === "Meta") return;
      e.preventDefault();
      setState("menu");
      return;
    }
    switch (e.key) {
      case "ArrowUp":
      case "w":
      case "W":
        e.preventDefault();
        focus(focusIndex - 1);
        break;
      case "ArrowDown":
      case "s":
      case "S":
        e.preventDefault();
        focus(focusIndex + 1);
        break;
      case "Enter":
      case " ":
        e.preventDefault();
        activate(focusIndex);
        break;
      case "Escape":
        e.preventDefault();
        setState("gate");
        break;
      case "Tab":
        e.preventDefault();
        focus(focusIndex + (e.shiftKey ? -1 : 1));
        break;
      default:
        break;
    }
  });

  addEventListener("pointerdown", (e) => {
    if (state === "gate") {
      e.preventDefault();
      setState("menu");
    }
  });

  buttons.forEach((b, i) => {
    b.addEventListener("pointerenter", () => {
      if (state === "menu") focus(i);
    });
    b.addEventListener("click", () => {
      if (state !== "menu") return;
      focus(i);
      activate(i);
    });
  });

  // Focus the stage itself so keyboard input works as soon as the page opens.
  addEventListener("load", () => {
    if (state === "menu") focus(0);
  });

  if (state === "menu") focus(0);
})();
