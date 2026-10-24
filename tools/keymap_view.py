"""Live keymap page for the menu bar app: every layer with the board's real key positions,
coloured like the keyboard's layer lighting, following the active layer and flashing each
key as it is pressed. Served on 127.0.0.1 with a random token in the path.
"""

import http.server
import json
import secrets
import threading

import kb
from math_keys import KEYS, group

BOARD_KEYCODES = 41  # custom keycodes before the math keys, as in vial.json

# Same colours and rules as rgb_matrix_indicators_user in keymap.c.
PALETTE = {
    "blue": "#0040ff",
    "cyan": "#00c0ff",
    "green": "#00ff30",
    "amber": "#ff9000",
    "orange": "#ff4000",
    "purple": "#9000ff",
    "pink": "#ff0080",
    "red": "#ff0000",
    "yellow": "#ffe000",
    "white": "#606060",
    "mint": "#30ffc0",
    "mustard": "#ffb010",
    "plain": "#34343a",
}
LAYER_COLOUR = {
    1: "mint",
    3: "mint",
    4: "mustard",
    5: "blue",
    6: "orange",
    7: "purple",
    8: "red",
}
MATH_GROUP = ["purple", "green", "cyan", "amber"]
LEGEND = {
    0: [
        ("blue", "hold Space: Nav"),
        ("orange", "hold right Cmd: Symbols"),
        ("purple", "tap right Ctrl: Math on/off"),
        ("mint", "hold Fn"),
        ("white", "tap/hold modifiers"),
    ],
    5: [
        ("blue", "arrows"),
        ("cyan", "word and line jumps"),
        ("green", "editing"),
        ("purple", "page up/down"),
        ("red", "hold right Cmd too: Mouse"),
        ("white", "modifiers"),
    ],
    6: [
        ("green", "numbers"),
        ("orange", "brackets"),
        ("cyan", "operator macros"),
        ("yellow", "other symbols"),
        ("purple", "hold right Ctrl too: LaTeX"),
    ],
    7: [
        ("purple", "Greek"),
        ("green", "sets"),
        ("cyan", "relations and logic"),
        ("amber", "operators and brackets"),
        ("pink", "with right Cmd held: LaTeX"),
        ("plain", "big: press the key; \u21e7 small: with Shift; corner: the key it is on"),
    ],
    8: [
        ("red", "pointer"),
        ("orange", "scroll"),
        ("yellow", "clicks"),
        ("white", "modifiers"),
    ],
}
BRACKETS = {0x2F, 0x30, 0x22F, 0x230, 0x226, 0x227, 0x236, 0x237}  # [ ] { } ( ) < >


def colour(layer, code):
    """Colour name of a key on a layer, or "" for a transparent key."""
    if code in (0x0000, 0x0001):
        return ""
    if 0xE0 <= code <= 0xE7 or 0x2000 <= code <= 0x3FFF:  # modifiers, mod-taps
        return "white"
    if 0x4000 <= code <= 0x4FFF:  # layer-tap
        return LAYER_COLOUR.get((code >> 8) & 0xF, "plain")
    if 0x5220 <= code <= 0x527F or 0x52C0 <= code <= 0x52DF:  # MO, TG, TT
        return LAYER_COLOUR.get(code & 0x1F, "plain")
    i = code - 0x7E00 - BOARD_KEYCODES
    if 0 <= i < len(KEYS):
        return MATH_GROUP[group(KEYS[i][1])]
    if layer == 5:
        if 0x4F <= code <= 0x52:
            return "blue"
        if 0x0100 <= code <= 0x1FFF and 0x4F <= code & 0xFF <= 0x52:
            return "cyan"
        return "purple" if code in (0x4B, 0x4E) else "green"
    if layer == 6:
        if 0x1E <= code <= 0x27:
            return "green"
        if 0x7700 <= code <= 0x777F:
            return "cyan"
        return "orange" if code in BRACKETS else "yellow"
    if layer == 8:
        if 0xCD <= code <= 0xD0:
            return "red"
        return "orange" if 0xD9 <= code <= 0xDC else "yellow"
    return LAYER_COLOUR.get(layer, "plain")


def parts(labels, code, base):
    """[big, small, corner] for one key: what a press types, the Shift (or hold) variant,
    and on upper layers the base-layer key it sits on."""
    if code in (0x0000, 0x0001):
        return ["", "", ""]
    corner = labels.short(base) if base not in (0x0000, 0x0001) else ""
    i = code - 0x7E00 - BOARD_KEYCODES
    if 0 <= i < len(KEYS):
        plain, shifted = KEYS[i][1], KEYS[i][2]
        return [plain, "\u21e7 " + shifted if shifted != plain else "", corner]
    lines = labels(code).split("\n")
    if 0x5220 <= code <= 0x523F:  # MO: "hold Symbols"
        return [lines[-1], "hold", corner]
    if len(lines) == 2 and code <= 0xFF:  # Vial's shifted-over-plain label, e.g. "!" over "1"
        return [lines[1], "\u21e7 " + lines[0], corner]
    return [lines[0], " ".join(lines[1:]), corner]


def page(keyboard, labels):
    from keycodes.keycodes import Keycode

    keys = [
        {"x": k.x, "y": k.y, "w": k.width, "h": k.height, "r": k.row, "c": k.col}
        for k in keyboard.keys
    ]
    layers = []
    for n in range(keyboard.layers):
        codes = [
            Keycode.deserialize(keyboard.layout.get((n, k.row, k.col), "KC_NO"))
            for k in keyboard.keys
        ]
        bases = [Keycode.deserialize(keyboard.layout.get((0, k.row, k.col), "KC_NO")) for k in keyboard.keys]
        layers.append(
            {
                "name": kb.LAYERS[n],
                "labels": [parts(labels, c, b if n else 0) for c, b in zip(codes, bases)],
                "colours": [PALETTE.get(colour(n, c), "") for c in codes],
                "legend": [[PALETTE[c], text] for c, text in LEGEND.get(n, [])],
            }
        )
    data = json.dumps(
        {"keys": keys, "layers": layers, "pink": PALETTE["pink"]}, ensure_ascii=False
    )
    return HTML.replace("/*DATA*/", data)


class Server:
    """Serves the page and the live state; state is the dict the watcher loop keeps updating."""

    def __init__(self, render, state):
        token = secrets.token_urlsafe(16)

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == f"/{token}/":
                    body, kind = render().encode(), "text/html; charset=utf-8"
                elif self.path == f"/{token}/state":
                    body, kind = json.dumps(state).encode(), "application/json"
                else:
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", kind)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}/{token}/"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()


HTML = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">
<title>Air96 keymap</title>
<style>
:root { color-scheme: dark; }
body { background: #121214; color: #ddd; font: 14px -apple-system, sans-serif; margin: 20px; }
header { display: flex; flex-wrap: wrap; align-items: baseline; gap: 10px 18px; margin-bottom: 14px; }
h1 { font-size: 22px; font-weight: 600; margin: 0; min-width: 9em; }
nav button { background: #26262b; color: #bbb; border: 0; border-radius: 6px; padding: 5px 10px; margin: 2px; font: inherit; cursor: pointer; }
nav button.on { background: #ddd; color: #111; }
#status { color: #888; }
.kb { position: relative; width: 100%; container-type: inline-size; }
.k { position: absolute; box-sizing: border-box; border-radius: 6px; background: #1e1e22; display: flex;
     flex-direction: column; align-items: center; justify-content: center; text-align: center; overflow: hidden;
     font-size: clamp(7px, 1.35cqw, 20px); line-height: 1.15; color: #fff; transition: background .12s; border: 1px solid #0003; }
.k.dim { color: #666; }
.k b { font-weight: 500; font-size: 1.25em; }
.k small { font-size: .78em; opacity: .85; margin-top: 2px; }
.k i { position: absolute; top: 3px; left: 5px; font-style: normal; font-size: .7em; opacity: .6; }
.k.hit { animation: hit .45s ease-out; }
@keyframes hit { from { box-shadow: 0 0 0 4px #fff, 0 0 18px 6px #fff; transform: scale(1.08); } to { box-shadow: none; transform: none; } }
#legend { display: flex; flex-wrap: wrap; gap: 8px 18px; margin-top: 16px; }
#legend span::before { content: ""; display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -1px; background: var(--c); }
#combo { position: fixed; top: 16px; right: 20px; background: #fff; color: #111; border-radius: 8px; padding: 8px 14px; font-weight: 600; opacity: 0; transition: opacity .2s; }
#combo.show { opacity: 1; }
</style>
<header><h1 id=title></h1><nav id=tabs></nav><span id=status></span></header>
<div class=kb id=kb></div>
<div id=legend></div>
<div id=combo></div>
<script>
const D = /*DATA*/;
const kbEl = document.getElementById("kb"), tabs = document.getElementById("tabs");
const W = Math.max(...D.keys.map(k => k.x + k.w)), H = Math.max(...D.keys.map(k => k.y + k.h));
kbEl.style.aspectRatio = W + " / " + H;
const els = D.keys.map(k => {
  const e = document.createElement("div");
  e.className = "k";
  Object.assign(e.style, { left: 100 * k.x / W + "%", top: 100 * k.y / H + "%",
    width: "calc(" + 100 * k.w / W + "% - 4px)", height: "calc(" + 100 * k.h / H + "% - 4px)" });
  kbEl.appendChild(e);
  return e;
});
let shown = -1, latex = false, pinned = null, keys = -1, combos = null;
function draw(n, tex) {
  if (n === shown && tex === latex) return;
  shown = n; latex = tex;
  const L = D.layers[n];
  document.getElementById("title").textContent = tex ? "LaTeX" : n + " " + L.name;
  els.forEach((e, i) => {
    const [big, small, corner] = L.labels[i], c = L.colours[i], label = big;
    const esc = t => t.replace(/[&<>]/g, s => ({"&": "&amp;", "<": "&lt;", ">": "&gt;"})[s]);
    e.innerHTML = (corner ? `<i>${esc(corner)}</i>` : "") + `<b>${esc(big)}</b>` + (small ? `<small>${esc(small)}</small>` : "");
    e.style.background = c ? (tex && n === 7 && label ? D.pink : c) + "cc" : "";
    e.classList.toggle("dim", !c);
  });
  document.getElementById("legend").innerHTML = L.legend.map(([c, t]) => `<span style="--c:${c}">${t}</span>`).join("");
  [...tabs.children].forEach((b, i) => b.classList.toggle("on", i === n));
}
D.layers.forEach((L, i) => {
  const b = document.createElement("button");
  b.textContent = i + " " + L.name;
  b.onclick = () => { pinned = pinned === i ? null : i; draw(i, false); };
  tabs.appendChild(b);
});
const follow = document.createElement("button");
follow.textContent = "following the keyboard";
follow.onclick = () => { pinned = null; };
tabs.appendChild(follow);
async function tick() {
  try {
    const s = await (await fetch("state", { cache: "no-store" })).json();
    document.getElementById("status").textContent = s.connected ? (pinned === null ? "live" : "pinned, click the tab again to follow") : "keyboard not connected over USB";
    follow.classList.toggle("on", pinned === null);
    if (pinned === null && s.connected) draw(s.layer, s.latex);
    if (s.keys !== keys && keys !== -1 && s.layer === shown) {
      const i = D.keys.findIndex(k => k.r === s.row && k.c === s.col);
      if (i >= 0) { els[i].classList.remove("hit"); void els[i].offsetWidth; els[i].classList.add("hit"); }
    }
    keys = s.keys;
    if (combos !== null && s.combos !== combos) {
      const c = document.getElementById("combo");
      c.textContent = s.combo; c.classList.add("show");
      setTimeout(() => c.classList.remove("show"), 1500);
    }
    combos = s.combos;
  } catch (e) {
    document.getElementById("status").textContent = "menu bar app not running";
  }
  setTimeout(tick, 60);
}
draw(0, false);
tick();
</script>
"""
