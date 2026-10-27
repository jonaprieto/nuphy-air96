"""Typing metrics from the keys the Mac gets from the Air96, the same over USB and Bluetooth.

The menu bar app passes each key press and release (HID usage) to watch.py, which feeds
them here. Only counts are kept, per day: characters typed, time spent typing, corrections
(Backspace), and per key how often it was typed and how often a Backspace deleted it.
Nothing typed is stored.
"""

import collections
import json
import os
import time

PAUSE = 5.0  # seconds; a longer gap between keys is a pause, not typing time
NOW = 60.0  # "now" WPM covers the last minute
DAYS = 7
MIN_TYPED = 30  # a key needs this many presses before its correction rate is shown
BACKSPACE = 0x2A
SHORTCUT_MODS = {0xE0, 0xE3, 0xE4, 0xE7}  # Ctrl, Cmd: not typing


def is_char(usage):
    """Keys that type something: letters, digits, Enter, Space, punctuation, keypad."""
    return 0x04 <= usage <= 0x28 or 0x2C <= usage <= 0x38 or 0x54 <= usage <= 0x63


def wpm(chars, seconds):
    return round(chars / 5 / (seconds / 60)) if seconds >= 5 else None


class Metrics:
    def __init__(self, path):
        self.path = path
        try:
            self.days = json.loads(path.read_text())
        except (OSError, ValueError):
            self.days = {}
        self.down = set()
        self.typed = []  # chars typed since the cursor last moved, for Backspace to blame
        self.last = None  # time of the last char
        self.recent = (
            collections.deque()
        )  # (time, active seconds it added), last minute
        self.dirty = False
        self.saved = 0.0

    def today(self, now):
        day = time.strftime("%Y-%m-%d", time.localtime(now))
        return self.days.setdefault(
            day, {"chars": 0, "active": 0.0, "corrections": 0, "keys": {}}
        )

    def key(self, usage, pressed, now=None):
        now = time.time() if now is None else now
        if not pressed:
            self.down.discard(usage)
            return
        if usage in self.down:  # the same press reported twice (two HID interfaces)
            return
        self.down.add(usage)
        if 0xE0 <= usage <= 0xE7:
            return
        day = self.today(now)
        shortcut = bool(self.down & SHORTCUT_MODS)
        if usage == BACKSPACE:
            day["corrections"] += 1
            if self.typed and not (
                self.down & {0xE2, 0xE6} or shortcut
            ):  # Opt/Cmd+Bksp: a word or line
                blamed = day["keys"].setdefault(str(self.typed.pop()), [0, 0])
                blamed[1] += 1
            else:
                self.typed.clear()
        elif is_char(usage) and not shortcut:
            gap = now - self.last if self.last is not None else PAUSE
            active = gap if gap < PAUSE else 0.0
            day["chars"] += 1
            day["active"] += active
            day["keys"].setdefault(str(usage), [0, 0])[0] += 1
            self.typed = self.typed[-63:] + [usage]
            self.last = now
            self.recent.append((now, active))
        else:  # arrows, Tab, shortcuts: the cursor may have moved
            self.typed.clear()
        self.dirty = True

    def summary(self, now=None):
        now = time.time() if now is None else now
        while self.recent and now - self.recent[0][0] > NOW:
            self.recent.popleft()
        today = self.today(now)
        week = [d for k, d in sorted(self.days.items())[-DAYS:]]
        keys = collections.Counter()
        fixed = collections.Counter()
        for d in week:
            for usage, (n, c) in d["keys"].items():
                keys[int(usage)] += n
                fixed[int(usage)] += c
        rate = (
            lambda d: round(100 * d["corrections"] / d["chars"]) if d["chars"] else None
        )  # noqa: E731
        week_total = {
            k: sum(d[k] for d in week) for k in ("chars", "active", "corrections")
        }
        worst = sorted(
            (u for u in keys if keys[u] >= MIN_TYPED and fixed[u]),
            key=lambda u: fixed[u] / keys[u],
            reverse=True,
        )[:5]
        return {
            "now": wpm(len(self.recent), sum(a for _, a in self.recent)),
            "today": wpm(today["chars"], today["active"]),
            "today_chars": today["chars"],
            "today_corrected": rate(today),
            "week": wpm(week_total["chars"], week_total["active"]),
            "week_corrected": rate(week_total),
            "worst": [(u, round(100 * fixed[u] / keys[u])) for u in worst],
            "heat": {u: [keys[u], fixed[u]] for u in keys},
        }

    def save(self, every=30.0):
        if not self.dirty or time.time() - self.saved < every:
            return
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.days))
        os.replace(tmp, self.path)
        self.dirty, self.saved = False, time.time()


if __name__ == "__main__":
    import pathlib
    import tempfile

    A, S, LCMD, LALT = 0x04, 0x16, 0xE3, 0xE2
    m = Metrics(pathlib.Path(tempfile.mkdtemp()) / "m.json")
    t = 1_000_000.0
    for i in range(60):  # 60 chars, 0.2 s apart: 12 s of typing, 60 WPM
        m.key(A if i % 2 else S, True, t + i * 0.2)
        m.key(A if i % 2 else S, False, t + i * 0.2 + 0.05)
    m.key(A, True, t + 20)  # an 'a' after a pause: no typing time added
    m.key(A, True, t + 20)  # reported twice: counted once
    m.key(A, False, t + 20.1)
    m.key(BACKSPACE, True, t + 20.3)  # deletes that 'a'
    m.key(BACKSPACE, False, t + 20.4)
    m.key(LCMD, True, t + 21)
    m.key(S, True, t + 21.1)  # Cmd+S: not typing
    s = m.summary(t + 22)
    assert s["today_chars"] == 61, s
    assert s["now"] == s["today"] == 62, s  # 61 chars over 11.8 s of typing
    assert s["today_corrected"] == 2, s  # 1 correction in 61 chars
    assert s["heat"][A] == [31, 1] and s["heat"][S] == [30, 0], s["heat"]
    assert s["worst"] == [(A, 3)], s["worst"]
    m.key(LCMD, False, t + 23)
    m.key(S, False, t + 23)
    m.key(S, True, t + 23.5)
    m.key(LALT, True, t + 24)
    m.key(BACKSPACE, True, t + 24.1)  # Opt+Bksp deletes a word: no single key to blame
    assert m.summary(t + 25)["heat"][S] == [31, 0]
    m.save(every=0)
    assert Metrics(m.path).days == m.days
    print("ok")
