"""Vial's own protocol code (the vial-gui submodule), for scripts.

Importing this also lets Vial name custom keycodes past USER63: the board has
41 and the math layer 46 more, and Vial stops at 64.
"""

import contextlib
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
VIAL = ROOT / "vial-gui/src/main"
VIL = ROOT / "jonaprieto.vil"
CACHE = pathlib.Path.home() / ".cache/nuphy-air96"
VIAL_LOCK = CACHE / "vial.lock"  # present while the Vial window is open

sys.path.insert(0, str(VIAL / "python"))

from keycodes.keycodes_v5 import keycodes_v5  # noqa: E402
from keycodes.keycodes_v6 import keycodes_v6  # noqa: E402

for table in (keycodes_v5, keycodes_v6):
    for x in range(64, 128):
        table.kc["USER{:02}".format(x)] = table.kc["QK_KB"] + x

LAYERS = ["Mac", "Mac Fn", "Win", "Win Fn", "Board", "Nav", "Symbols", "Math", "Mouse"]
VIAL_PREFIX, UNLOCK_STATUS, UNLOCK_START, UNLOCK_POLL = 0xFE, 0x05, 0x06, 0x07


@contextlib.contextmanager
def watcher_paused():
    """Make the menu bar watcher let go of the keyboard while the block runs."""
    CACHE.mkdir(parents=True, exist_ok=True)
    VIAL_LOCK.touch()
    try:
        time.sleep(0.5)  # it checks the lock ten times a second
        yield
    finally:
        VIAL_LOCK.unlink(missing_ok=True)


def _send(dev, *msg):
    from util import hid_send

    return hid_send(dev, bytes(msg), retries=20)


def unlock(dev):
    """Vial unlock from the terminal: hold Esc + Enter (Vial's own version is a dialog)."""
    if _send(dev, VIAL_PREFIX, UNLOCK_STATUS)[0]:
        return
    print("Hold Esc + Enter until this continues...", flush=True)
    _send(dev, VIAL_PREFIX, UNLOCK_START)
    while not _send(dev, VIAL_PREFIX, UNLOCK_POLL)[0]:
        time.sleep(0.1)


def _use_terminal_unlock():
    from unlocker import Unlocker

    Unlocker.unlock = classmethod(lambda cls, keyboard: unlock(keyboard.dev))


def open_keyboard(on_pending_unlock=print):
    """The Air96 over USB as Vial's Keyboard object (layout, combos, settings loaded), or None.

    An unlock left half done (the cable came out mid-way; the board keeps running on
    battery) makes the firmware ignore everything else, so it is finished first.
    """
    import hid

    from editor.qmk_settings import QmkSettings
    from util import find_vial_devices

    class Resources:
        def get_resource(self, name):
            return str(VIAL / "resources/base" / name)

    QmkSettings.initialize(Resources())
    _use_terminal_unlock()
    for dev in find_vial_devices({"definitions": {}}, quiet=True):
        if "Air96" in dev.title():
            raw = hid.device()
            raw.open_path(dev.desc["path"])
            try:
                unlocked, pending = _send(raw, VIAL_PREFIX, UNLOCK_STATUS)[:2]
                if pending and not unlocked:
                    on_pending_unlock("A Vial unlock is waiting: hold Esc + Enter to finish it.")
                    unlock(raw)
            finally:
                raw.close()
            dev.open(None)
            return dev.keyboard
    return None
