// Level-up redesign (user 2026-11-28: "phần chọn thẻ khi lên cấp cần thiết kế lại"): the real offer of 04-level-up
// (Kiếm sĩ, cấp 1; Đất nứt from 04b-level-up-milestones, to show a Hiếm card) shared by the three directions. icon: assets/levelup/*. tier: thuong | hiem | suthi | huyenthoai.
const LU = {
  level: 8, hero: "Kiếm sĩ",
  odds: [["Thường", 70, "thuong"], ["Hiếm", 20, "hiem"], ["Sử thi", 7, "suthi"], ["Huyền thoại", 3, "huyenthoai"]],
  tierName: { thuong: "Thường", hiem: "Hiếm", suthi: "Sử thi", huyenthoai: "Huyền thoại" },
  tierCol: { thuong: "#9a9a9a", hiem: "#3a78c8", suthi: "#9a4ad0", huyenthoai: "#e0a020" },
  cards: [
    { name: "Mài kiếm", kind: "Chỉ số", tier: "thuong", icon: "assets/levelup/broadsword.svg", vector: true, lv: [0, 1], max: 0,
      key: ["Sát thương", "17", "20"], lines: [["Sát thương", "17", "20"]], desc: "+15% sát thương mọi đòn.", isNew: true },
    { name: "Đất nứt", kind: "Chiêu", tier: "hiem", icon: "assets/levelup/earth_strike.png", lv: [1, 2], max: 5,
      key: ["Số lượng", "1", "2"], lines: [["Sát thương", "21", "26"], ["Cỡ", "×0.97", "×1.04"], ["Hồi chiêu", "4.2s", "4.2s"], ["Số lượng", "1", "2"]],
      milestone: "Bậc II · hình mới", desc: "Đất nứt ở phía quái gần nhất. Mỗi cấp: +25% sát thương, +8% vùng. Làm chậm quái; cấp 2: nổ ở 2 quái; cấp 4: 3 quái; cấp 5: 4 quái." },
    { name: "Chém kiếm", kind: "Chiêu", tier: "thuong", icon: "assets/levelup/blade_arc.png", lv: [1, 2], max: 5,
      key: ["Sát thương", "27", "31"], lines: [["Sát thương", "27", "31"], ["Hồi chiêu", "0.9s", "0.9s"]],
      milestone: "Bậc II · hình mới", desc: "Tự chém một nhát kiếm ngắn về phía quái gần nhất. Mỗi cấp: +20% sát thương. Cấp 4: gây chảy máu." },
  ],
  owned: [["assets/levelup/blade_arc.png", 1], ["assets/levelup/whirlwind.png", 2]],
  actions: [["R", "Đổi", "×2"], ["X", "Loại", "×1"], ["S", "Bỏ qua", "×2 · +10 vàng"]],
};
// ←→ / ↑↓ move, 1-3 pick, Enter takes; each page calls LU.bind(count, paint).
LU.bind = (n, paint, axis = "x") => {
  let i = 0;
  const go = (k) => { i = (k + n) % n; paint(i); };
  addEventListener("keydown", (e) => {
    const prev = axis === "x" ? "ArrowLeft" : "ArrowUp", next = axis === "x" ? "ArrowRight" : "ArrowDown";
    if (e.key === prev) go(i - 1); else if (e.key === next) go(i + 1);
    else if ("123".includes(e.key)) go(+e.key - 1);
  });
  paint(i);
  return go;
};
LU.img = (c, cls = "") => `<img class="${cls}" src="${c.icon}"${c.vector ? ' style="image-rendering:auto"' : ""}>`;
LU.pips = (c) => c.max ? Array.from({ length: c.max }, (_, k) => `<i class="pip${k < c.lv[1] ? " on" : ""}${k === c.lv[1] - 1 ? " new" : ""}"></i>`).join("") : "";
