"""Flash a firmware build and put the saved layout back.

    flash.py FIRMWARE.bin [--clear-eeprom] [--no-restore]

With Vial firmware running, the board is sent to its bootloader over USB once
it is unlocked (hold Esc + Enter). Otherwise enter the bootloader by hand:
hold Esc while plugging in, or the button under the Caps Lock keycap.
"""

import argparse
import struct
import subprocess
import sys
import time

import kb

DFU = ["dfu-util", "-a", "0", "-d", "0483:DF11"]
EEPROM = 0x0801E000  # last 8 kB of flash: wear-leveled EEPROM
BOOTLOADER_JUMP = 0x0B


def wait(what, ready, timeout):
    end = time.time() + timeout
    while time.time() < end:
        if ready():
            return True
        time.sleep(0.5)
    sys.exit(f"timed out waiting for {what}")


def in_bootloader():
    out = subprocess.run(["dfu-util", "-l"], capture_output=True, text=True).stdout
    return "Found DFU: [0483:df11]" in out


def dfu(*args):
    # dfu-util can hang on exit after a good transfer (libusb on macOS), so cap it.
    try:
        out = subprocess.run(
            DFU + list(args), capture_output=True, text=True, timeout=90
        ).stdout
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode()
    if "File downloaded successfully" not in out:
        sys.exit("dfu-util failed:\n" + out[-500:])


def to_bootloader():
    keyboard = kb.open_keyboard()
    if keyboard is None:
        print(
            "Put the board in the bootloader: hold Esc while plugging in, or the button under Caps Lock."
        )
        return
    kb.unlock(keyboard)
    keyboard.dev.write(b"\x00" + struct.pack("B", BOOTLOADER_JUMP) + b"\x00" * 31)
    keyboard.dev.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("firmware")
    p.add_argument(
        "--clear-eeprom", action="store_true", help="start from keymap.c defaults"
    )
    p.add_argument(
        "--no-restore",
        action="store_true",
        help=f"do not load {kb.VIL.name} afterwards",
    )
    a = p.parse_args()

    with kb.watcher_paused():
        flash(a)


def flash(a):
    if not in_bootloader():
        to_bootloader()
    wait("the bootloader", in_bootloader, 300)
    time.sleep(1)
    if a.clear_eeprom:
        blank = kb.CACHE / "eeprom-blank.bin"
        blank.write_bytes(b"\xff" * 8192)
        dfu("-s", hex(EEPROM), "-D", str(blank))
    dfu("-s", "0x08000000:leave", "-D", a.firmware)
    print("Flashed. Click Allow if macOS asks about the keyboard.")

    keyboard = None

    def booted():
        nonlocal keyboard
        keyboard = kb.open_keyboard()
        return keyboard is not None

    wait("the keyboard to start", booted, 120)
    if not a.no_restore and kb.VIL.exists():
        keyboard.restore_layout(kb.VIL.read_bytes())
        print(f"Restored {kb.VIL.name}.")
    keyboard.dev.close()


if __name__ == "__main__":
    main()
