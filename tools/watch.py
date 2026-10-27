"""Keyboard side of the menu bar app (NuphyWatch.swift runs this and draws what it prints).

Shows the active layer, the last key and the last combo; the menu opens a
picture of the keymap, changes tap-hold settings and saves the layout. Those
need the USB cable (Bluetooth carries no raw HID); it lets go while Vial is open.
Over Bluetooth it still shows the keymap (as saved the last time the cable was
in), the last key and the typing metrics, which come from the keys the Mac gets.

Prints one JSON line per change, {"title": ..., "menu": [...]}; reads menu
commands (keymap, vial, save, set QSID VALUE) and the app's key events
(key USAGE 1|0) one per line on stdin.
"""

import html
import json
import os
import queue
import subprocess
import sys
import threading
import time

import kb
import keymap_view
from metrics import Metrics

WATCH_CMD = 0x60  # answered by raw_hid_receive_kb in keymap.c
COMBO_SHOWN = 2.0  # seconds a combo stays in the menu bar title
MODS = [(0x01, "Ctrl"), (0x02, "Shift"), (0x04, "Opt"), (0x08, "Cmd")]
SETTINGS = {
    7: "Tapping term",
    22: "Permissive Hold",
    26: "Chordal Hold",
    27: "Flow Tap",
}
COMMANDS = queue.Queue()


def mods_text(mods):
    return "+".join(name for bit, name in MODS if mods & bit)


class Labels:
    """Short names for keycodes, from Vial's tables plus this keyboard's custom keys and macros."""

    def __init__(self, keyboard):
        self.custom = keyboard.custom_keycodes or []
        self.macros = [
            "".join(a[1] for a in m if a[0] == "text") for m in keyboard.save_macro()
        ]

    @staticmethod
    def basic(code):
        """Vial's label: two lines (shifted over plain) for keys like 7 or [."""
        from keycodes.keycodes import Keycode

        return Keycode.label(Keycode.serialize(code))

    @staticmethod
    def plain(code):
        return Labels.basic(code).split("\n")[-1]

    def __call__(self, code):
        if isinstance(code, str):
            from keycodes.keycodes import Keycode

            code = Keycode.deserialize(code)
        if code in (0x0000, 0x0001):  # KC_NO, KC_TRNS
            return ""
        if 0x0200 <= code <= 0x02FF and "\n" in self.basic(code & 0xFF):
            return self.basic(code & 0xFF).split("\n")[
                0
            ]  # Shift + key: the shifted symbol
        if 0x0100 <= code <= 0x1FFF:
            return f"{mods_text(code >> 8)} {self.plain(code & 0xFF)}"
        if 0x2000 <= code <= 0x3FFF:
            return f"{self.plain(code & 0xFF)}\n{mods_text((code >> 8) & 0x1F)}"
        if 0x4000 <= code <= 0x4FFF:
            return f"{self.plain(code & 0xFF)}\nhold {kb.LAYERS[(code >> 8) & 0xF]}"
        if 0x5220 <= code <= 0x523F:
            return f"hold\n{kb.LAYERS[code & 0x1F]}"
        if 0x5260 <= code <= 0x527F:
            return f"{kb.LAYERS[code & 0x1F]}\non/off"
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
        if 0x2000 <= code <= 0x4FFF:  # mod-tap, layer-tap: the tap key
            return self(code).split("\n")[0]
        return self(code).replace("\n", " ")


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
        "row": r[16],
        "col": r[17],
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


def show(title, items):
    """items: menu entries, or plain strings for lines that do nothing when clicked."""
    entries = [{"title": i} if isinstance(i, str) else i for i in items]
    print(json.dumps({"title": title, "menu": entries}), flush=True)


SEP = {"sep": True}


def typing_lines(t):
    """The typing metrics (metrics.Metrics.summary) as menu lines."""
    if not t["today_chars"] and not t["week"]:
        return ["Typing: nothing typed yet"]
    lines = [f"Typing now: {t['now']} WPM"] if t["now"] else []
    if t["today_chars"]:
        lines.append(
            f"Today: {t['today'] or '–'} WPM · {t['today_corrected']}% corrected · {t['today_chars']:,} chars"
        )
    if t["week"]:
        lines.append(f"Last 7 days: {t['week']} WPM · {t['week_corrected']}% corrected")
    if t["worst"]:
        lines.append("Most corrected: " + "   ".join(f"{Labels.plain(u)} {p}%" for u, p in t["worst"]))
    return lines


def menu(keyboard, labels, s, combo, title, host, typing):
    if keyboard:
        items = [
            f"Layer: {layer_name(s['layers'])}",
            f"Last key: {labels.short(s['keycode'])}   ({s['keys']} keys since the board started)",
            f"Last combo: {combo or 'none yet'}",
        ]
        if s["mods"]:
            items.append(f"Held: {mods_text(s['mods'] | s['mods'] >> 4)}")
        if s["caps_word"]:
            items.append("Caps Word on")
    else:
        items = [
            "Layer: needs the cable (Bluetooth sends no layer)",
            f"Last key: {Labels.plain(host['usage']) if host['usage'] else 'none yet'}",
        ]
    items += [
        SEP,
        *typing_lines(typing),
        SEP,
        {"title": "Show keymap", "cmd": "keymap"},
        {"title": "Open Vial", "cmd": "vial"},
    ]
    if keyboard:
        st = keyboard.settings
        term, flow = st.get(7), st.get(27)
        settings = [
            {
                "title": f"Tapping term: {term} ms",
                "items": [
                    {"title": f"{v} ms", "cmd": f"set 7 {v}", "checked": v == term}
                    for v in (200, 225, 250, 275, 300)
                ],
            },
            *[
                {
                    "title": SETTINGS[q],
                    "cmd": f"set {q} {int(not st.get(q))}",
                    "checked": bool(st.get(q)),
                }
                for q in (22, 26)
            ],
            {
                "title": f"Flow Tap: {f'{flow} ms' if flow else 'off'}",
                "items": [
                    {
                        "title": f"{v} ms" if v else "off",
                        "cmd": f"set 27 {v}",
                        "checked": v == flow,
                    }
                    for v in (0, 100, 150, 200)
                ],
            },
        ]
        items += [
            SEP,
            {"title": "Tap-hold settings", "items": settings},
            SEP,
            {"title": f"Save layout to {kb.VIL.name}", "cmd": "save"},
        ]
    show(title, items)


def read_commands():
    for line in sys.stdin:
        COMMANDS.put((time.time(), line.split() or [""]))
    os._exit(0)  # the app is gone; sys.exit here would only end this thread


def run_commands(keyboard, typing, host):
    """Menu clicks, and the app's key events for the metrics. Settings and saving need the cable."""
    while not COMMANDS.empty():
        at, (cmd, *args) = COMMANDS.get()
        if cmd == "key":
            usage, pressed = int(args[0]), args[1] == "1"
            if pressed and usage not in typing.down and not 0xE0 <= usage <= 0xE7:
                host["keys"] += 1
                host["usage"] = usage
            typing.key(usage, pressed, at)
        elif cmd == "vial":
            subprocess.Popen(
                ["/usr/bin/make", "-C", str(kb.ROOT), "gui"], start_new_session=True
            )
        elif cmd == "set" and keyboard:
            keyboard.qmk_settings_set(int(args[0]), int(args[1]))
        elif cmd == "keymap":
            subprocess.run(["open", SERVER.url])
        elif cmd == "save" and keyboard:
            kb.VIL.write_bytes(keyboard.save_layout())


STATE = {"connected": False}  # what the live keymap page polls
SERVER = None
PAGE = kb.CACHE / "keymap.html"  # the keymap as last seen over USB, shown over Bluetooth


def watch():
    global SERVER
    kb.CACHE.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=read_commands, daemon=True).start()
    current = {}

    def render():
        if current.get("keyboard"):
            return keymap_view.page(current["keyboard"], current["labels"])
        if PAGE.exists():
            return PAGE.read_text()
        return "<!doctype html><meta charset=utf-8><p>Plug the Air96 in over USB once to see its keymap here."

    SERVER = keymap_view.Server(render, STATE)
    (kb.CACHE / "keymap-url").write_text(
        SERVER.url + "\n"
    )  # for a bookmark-free reopen from the shell
    typing = Metrics(kb.CACHE / "metrics.json")
    host = {"keys": 0, "usage": None}  # the last key the Mac got: all there is over Bluetooth
    stats, stats_at = typing.summary(), 0.0
    keyboard = labels = None
    last = None
    retry_at = 0.0
    combo, combo_at, combos = None, 0.0, None
    while True:
        if kb.VIAL_LOCK.exists():
            STATE["connected"] = False
            if keyboard:
                keyboard.dev.close()
                keyboard = last = None
                show("Vial", ["Paused while Vial or a flash uses the keyboard"])
            run_commands(None, typing, host)
            time.sleep(0.1)
            continue
        if keyboard is None and time.time() >= retry_at:
            try:
                keyboard = kb.open_keyboard(
                    on_pending_unlock=lambda msg: show("Esc+Enter", [msg])
                )
            except Exception:
                keyboard = None
            if keyboard:
                labels = Labels(keyboard)
                current.update(keyboard=keyboard, labels=labels)
                PAGE.write_text(keymap_view.page(keyboard, labels))
                last = combos = None
            else:
                retry_at = time.time() + 2
        try:
            run_commands(keyboard, typing, host)
            s = poll(keyboard) if keyboard else None
        except Exception as e:
            show("!", [f"Lost the keyboard: {e}"])
            try:
                keyboard.dev.close()
            except Exception:
                pass
            keyboard = last = None
            time.sleep(1)
            continue
        if time.time() - stats_at >= 1:
            stats, stats_at = typing.summary(), time.time()
            typing.save()
        STATE.update(host_keys=host["keys"], usage=host["usage"], heat=stats["heat"])
        if s:
            if combos is not None and s["combos"] != combos:
                combo, combo_at = (
                    combo_text(keyboard, labels, s["combo_keycode"]),
                    time.time(),
                )
            combos = s["combos"]
            STATE.update(
                connected=True,
                layer=s["layers"].bit_length() - 1 if s["layers"] else 0,
                latex=bool(s["layers"] & (1 << 6) and s["layers"] & (1 << 7)),
                keys=s["keys"],
                row=s["row"],
                col=s["col"],
                combos=s["combos"],
                combo=combo or "",
            )
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
        else:
            STATE["connected"] = False
            title = f"Air96 · {Labels.plain(host['usage'])}" if host["usage"] else "–"
            state = (title, host["keys"])
        state += tuple(typing_lines(stats))
        if state != last:
            menu(keyboard, labels, s, combo, title, host, stats)
            last = state
        time.sleep(0.05)


if __name__ == "__main__":
    watch()
