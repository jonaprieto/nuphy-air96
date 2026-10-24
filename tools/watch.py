"""Menu bar watcher for the Air96 (a SwiftBar streamable plugin, see nuphy-watch.sh).

Shows the active layer, the last key and the last combo; the menu opens a
picture of the keymap, changes tap-hold settings and saves the layout. Needs
the USB cable (Bluetooth carries no raw HID) and lets go while Vial is open.

    watch.py            run as the plugin
    watch.py ctl CMD    send CMD to the running plugin (used by the menu items)
"""

import html
import subprocess
import sys
import time

import kb

WATCH_CMD = 0x60  # answered by raw_hid_receive_kb in keymap.c
COMMANDS = kb.CACHE / "watch.cmd"
KEYMAP_HTML = kb.CACHE / "keymap.html"
COMBO_SHOWN = 2.0  # seconds a combo stays in the menu bar title
MODS = [(0x01, "Ctrl"), (0x02, "Shift"), (0x04, "Opt"), (0x08, "Cmd")]
SETTINGS = {
    7: "Tapping term",
    22: "Permissive Hold",
    26: "Chordal Hold",
    27: "Flow Tap",
}
CTL = f"bash={sys.executable} param1={__file__} param2=ctl"


def mods_text(mods):
    return "+".join(name for bit, name in MODS if mods & bit)


class Labels:
    """Short names for keycodes, from Vial's tables plus this keyboard's custom keys and macros."""

    def __init__(self, keyboard):
        self.custom = keyboard.custom_keycodes or []
        self.macros = [
            "".join(a[1] for a in m if a[0] == "text") for m in keyboard.save_macro()
        ]

    def basic(self, code):
        """Vial's label: two lines (shifted over plain) for keys like 7 or [."""
        from keycodes.keycodes import Keycode

        return Keycode.label(Keycode.serialize(code))

    def plain(self, code):
        return self.basic(code).split("\n")[-1]

    def __call__(self, code):
        if isinstance(code, str):
            from keycodes.keycodes import Keycode

            code = Keycode.deserialize(code)
        if code in (0x0000, 0x0001):  # KC_NO, KC_TRNS
            return ""
        if 0x0200 <= code <= 0x02FF and "\n" in self.basic(code & 0xFF):
            return self.basic(code & 0xFF).split("\n")[0]  # Shift + key: the shifted symbol
        if 0x0100 <= code <= 0x1FFF:
            return f"{mods_text(code >> 8)} {self.plain(code & 0xFF)}"
        if 0x2000 <= code <= 0x3FFF:
            return f"{self.plain(code & 0xFF)}\n{mods_text((code >> 8) & 0x1F)}"
        if 0x4000 <= code <= 0x4FFF:
            return f"{self.plain(code & 0xFF)}\nhold {kb.LAYERS[(code >> 8) & 0xF]}"
        if 0x5220 <= code <= 0x523F:
            return f"hold\n{kb.LAYERS[code & 0x1F]}"
        if 0x52C0 <= code <= 0x52DF:
            return f"{kb.LAYERS[code & 0x1F]}\nhold, 2 taps lock"
        if 0x7700 <= code <= 0x777F:
            n = code - 0x7700
            return (
                self.macros[n] if n < len(self.macros) and self.macros[n] else f"M{n}"
            )
        if 0x7E00 <= code <= 0x7FFF:
            n = code - 0x7E00
            return self.custom[n]["name"] if n < len(self.custom) else hex(code)
        return self.basic(code)

    def short(self, code):
        """One line: what a plain key types, or the tap action of a tap/hold key."""
        if isinstance(code, str):
            from keycodes.keycodes import Keycode

            code = Keycode.deserialize(code)
        if 0x0002 <= code <= 0x00FF:
            return self.plain(code)
        return self(code).split("\n")[0]


def poll(keyboard):
    r = keyboard.usb_send(keyboard.dev, bytes([WATCH_CMD]), retries=3)
    if r[0] != WATCH_CMD:
        raise RuntimeError("firmware has no watcher support; flash the current build")
    u16 = lambda i: r[i] | r[i + 1] << 8  # noqa: E731
    return {
        "layers": int.from_bytes(r[2:6], "little"),
        "mods": r[10],
        "caps_word": r[11],
        "keys": u16(12),
        "keycode": u16(14),
        "combos": u16(18),
        "combo_keycode": u16(20),
    }


def layer_name(layers):
    if layers & (1 << 6) and layers & (1 << 7):
        return "LaTeX"
    top = layers.bit_length() - 1
    return kb.LAYERS[top] if top > 0 else "Mac"


def combo_text(keyboard, labels, keycode):
    from keycodes.keycodes import Keycode

    out = Keycode.serialize(keycode)
    for entry in keyboard.combo_entries:
        if entry[4] == out:
            keys = "+".join(labels.short(k) for k in entry[:4] if k != "KC_NO")
            return f"{keys} → {labels.short(keycode)}"
    return labels.short(keycode)


def show(title, lines):
    print("~~~")
    print(f"{title} | sfimage=keyboard")
    print("---")
    print("\n".join(lines))
    sys.stdout.flush()


def menu(keyboard, labels, s, combo, title):
    lines = [
        f"Layer: {layer_name(s['layers'])}",
        f"Last key: {labels.short(s['keycode'])}   ({s['keys']} keys since the board started)",
        f"Last combo: {combo or 'none yet'}",
    ]
    if s["mods"]:
        lines.append(f"Held: {mods_text(s['mods'] | s['mods'] >> 4)}")
    if s["caps_word"]:
        lines.append("Caps Word on")
    lines += ["---", f"Show keymap | {CTL} param3=keymap terminal=false"]
    lines.append(
        f"Open Vial | bash=/usr/bin/make param1=-C param2={kb.ROOT} param3=gui terminal=false"
    )
    lines += ["---", "Tap-hold settings"]
    st = keyboard.settings
    term = st.get(7)
    lines.append(f"--Tapping term: {term} ms")
    for v in (200, 225, 250, 275, 300):
        lines.append(
            f"----{v} ms | {CTL} param3=set param4=7 param5={v} terminal=false checked={str(v == term).lower()}"
        )
    for q in (22, 26):
        on = bool(st.get(q))
        lines.append(
            f"--{SETTINGS[q]} | {CTL} param3=set param4={q} param5={int(not on)} terminal=false checked={str(on).lower()}"
        )
    flow = st.get(27)
    lines.append(f"--Flow Tap: {flow or 'off'}{' ms' if flow else ''}")
    for v in (0, 100, 150, 200):
        name = f"{v} ms" if v else "off"
        lines.append(
            f"----{name} | {CTL} param3=set param4=27 param5={v} terminal=false checked={str(v == flow).lower()}"
        )
    lines += ["---", f"Save layout to {kb.VIL.name} | {CTL} param3=save terminal=false"]
    show(title, lines)


def keymap_page(keyboard, labels, current):
    """Every layer drawn with the board's real key positions; the current one first."""
    unit = 46
    width = max(k.x + k.width for k in keyboard.keys) * unit
    height = max(k.y + k.height for k in keyboard.keys) * unit
    order = [current] + [n for n in range(keyboard.layers) if n != current]
    parts = []
    for n in order:
        keys = []
        for k in keyboard.keys:
            text = labels(keyboard.layout.get((n, k.row, k.col), "KC_NO"))
            cls = "k" if text else "k empty"
            keys.append(
                f'<div class="{cls}" style="left:{k.x * unit}px;top:{k.y * unit}px;'
                f'width:{k.width * unit - 4}px;height:{k.height * unit - 4}px">'
                + "<br>".join(html.escape(t) for t in text.split("\n"))
                + "</div>"
            )
        mark = " (active now)" if n == current else ""
        parts.append(
            f"<h2>{n} {html.escape(kb.LAYERS[n])}{mark}</h2>"
            f'<div class="kb" style="width:{width}px;height:{height}px">{"".join(keys)}</div>'
        )
    KEYMAP_HTML.write_text(
        "<!doctype html><meta charset=utf-8><title>Air96 keymap</title><style>"
        "body{background:#151517;color:#ddd;font:14px -apple-system,sans-serif;margin:24px}"
        "h2{font-weight:500;margin:28px 0 10px}"
        ".kb{position:relative}"
        ".k{position:absolute;box-sizing:border-box;border-radius:6px;background:#34343a;display:flex;"
        "flex-direction:column;align-items:center;justify-content:center;text-align:center;"
        "font-size:11px;line-height:1.2;overflow:hidden}"
        ".empty{background:#222226}"
        "</style>"
        "<p>Transparent keys are dark: they do what the layer below does. Edit with Vial (menu bar: Open Vial).</p>"
        + "".join(parts)
    )
    subprocess.run(["open", str(KEYMAP_HTML)])


def run_commands(keyboard, labels, layers):
    if not COMMANDS.exists():
        return
    lines = COMMANDS.read_text().split("\n")
    COMMANDS.unlink()
    for line in filter(None, lines):
        cmd, *args = line.split()
        if cmd == "set":
            keyboard.qmk_settings_set(int(args[0]), int(args[1]))
        elif cmd == "keymap":
            keymap_page(keyboard, labels, layers.bit_length() - 1 if layers else 0)
        elif cmd == "save":
            kb.VIL.write_bytes(keyboard.save_layout())


def plugin():
    kb.CACHE.mkdir(parents=True, exist_ok=True)
    keyboard = labels = None
    last = shown = None
    combo, combo_at, combos = None, 0.0, None
    while True:
        if kb.VIAL_LOCK.exists():
            if keyboard:
                keyboard.dev.close()
                keyboard = None
                show("Vial", ["Paused while Vial or a flash uses the keyboard"])
            time.sleep(0.1)
            continue
        if keyboard is None:
            try:
                keyboard = kb.open_keyboard(on_pending_unlock=lambda msg: show("Esc+Enter", [msg]))
            except Exception:
                keyboard = None
            if keyboard is None:
                if shown != "off":
                    show(
                        "–",
                        [
                            "Air96 not found over USB",
                            "The watcher needs the cable; Bluetooth has no raw HID.",
                        ],
                    )
                    shown = "off"
                time.sleep(2)
                continue
            labels = Labels(keyboard)
            last = shown = combos = None
        try:
            s = poll(keyboard)
            run_commands(keyboard, labels, s["layers"])
        except Exception as e:
            show("!", [f"Lost the keyboard: {e}"])
            try:
                keyboard.dev.close()
            except Exception:
                pass
            keyboard, shown = None, "error"
            time.sleep(1)
            continue
        if combos is not None and s["combos"] != combos:
            combo, combo_at = (
                combo_text(keyboard, labels, s["combo_keycode"]),
                time.time(),
            )
        combos = s["combos"]
        name = layer_name(s["layers"])
        title = (
            f"{name} · {combo}"
            if time.time() - combo_at < COMBO_SHOWN
            else f"{name} · {labels.short(s['keycode'])}"
        )
        state = (
            title,
            s["layers"],
            s["keys"],
            s["mods"],
            s["caps_word"],
            tuple(sorted(keyboard.settings.items())),
        )
        if state != last:
            menu(keyboard, labels, s, combo, title)
            last = state
        time.sleep(0.1)


def main():
    if sys.argv[1:2] == ["ctl"]:
        kb.CACHE.mkdir(parents=True, exist_ok=True)
        with COMMANDS.open("a") as f:
            f.write(" ".join(sys.argv[2:]) + "\n")
        return
    plugin()


if __name__ == "__main__":
    main()
