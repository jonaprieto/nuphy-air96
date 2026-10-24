# nuphy-air96

Vial keymap for a NuPhy Air96 V2 (ANSI). The `qmk_firmware` submodule is the
`nuphy-air96-v2` branch of
[jonaprieto/vial-qmk](https://github.com/jonaprieto/vial-qmk): Vial's QMK plus
the board from [ablasik/nuphy-qmk](https://github.com/ablasik/nuphy-qmk) v1.2.4.

```sh
git clone --recurse-submodules git@github.com:jonaprieto/nuphy-air96.git
make gui     # edit the layout live in Vial
make watch   # menu bar watcher (SwiftBar)
make flash   # build and flash the firmware (brew install dfu-util)
```

## Layers

| # | Layer | How |
|---|-------|-----|
| 0 | Mac | Caps taps Esc, holds Ctrl; A S D F and J K L ; hold Ctrl Opt Cmd Shift |
| 1 | Mac Fn | hold Fn: F-keys, Bluetooth, lighting; E S D F = Mission Control, Spaces, app windows; A app switcher; Z X V screenshots |
| 5 | Nav | hold Space: arrows on H J K L, line start/end on Y/O, word jumps on U/I, undo/cut/copy/paste/redo on Z X C V B |
| 6 | Symbols + Numbers | hold right Cmd: `\ { ( ) }` on the left home row, numpad on the right, `-> => \|> != <= >= :=` on the number row |
| 7 | Math | hold right Ctrl, or tap it twice to lock: Greek and math symbols; with Shift the capital (or the logic symbol) |
| 7 + 6 | LaTeX | hold right Cmd too: the same keys type `\alpha`, `\forall`, `\mathbb{R}` ... |
| 8 | Mouse | hold Space + right Cmd: pointer on H J K L, scroll on Y U I O, clicks on N M , |

Layers 2-4 (Windows, Windows Fn, board settings) are the board's own. Combos:
J+K is Esc, `,`+`.` is Enter, C+V is Tab.

Math symbols need macOS's "Unicode Hex Input" keyboard source (System Settings >
Keyboard > Text Input > Edit, then + and search for it), selected instead of "U.S.".
Option+letter accents stop working there; shortcuts do not change.

## How to change things

Most changes need no flashing:

1. `make gui` opens Vial. Security > Unlock, then hold Esc + Enter.
2. Keymap: pick a layer (0-8), click a key, pick its new action; it applies at
   once. Tap/hold keys are typed in "Any", e.g. `LSFT_T(KC_F)` or `LT5(KC_SPC)`.
3. Macros (M0-M6 are the operator keys), Combos, and QMK Settings > Tap-Hold
   (tapping term, Permissive Hold, Chordal Hold, Flow Tap) work the same way.
   Tap dance is off: it does not fit in the chip's memory.
4. File > Save current layout, to `jonaprieto.vil` here, then `make save` to
   commit and push it. File > Load saved layout puts it back.

The math table (symbols and LaTeX names) is in `tools/math_keys.py`. After
editing it, run `python3 tools/math_keys.py` and `make flash`.

`make flash` builds, asks you to hold Esc + Enter, sends the board to its
bootloader and flashes it; click Allow if macOS asks about the keyboard. The
saved layout is loaded back afterwards. If the firmware ever fails to start,
enter the bootloader by hand (hold Esc while plugging in, or pull the Caps
Lock keycap and hold the button under it while plugging in), then run
`make flash FLASH_ARGS=--clear-eeprom`, which starts from `keymap.c` before
the saved layout is loaded.

## Menu bar watcher

`make watch` adds a SwiftBar plugin that shows the active layer and the last
key, and for two seconds the combo you just used. Its menu shows held
modifiers and Caps Word, draws every layer of the current keymap in the
browser, changes the tap-hold settings, saves the layout to `jonaprieto.vil`,
and opens Vial. It needs the USB cable (Bluetooth carries no raw HID) and
pauses while Vial or `make flash` uses the keyboard.

## Upgrading the firmware base

Rebase the fork's `nuphy-air96-v2` branch on `vial-kb/vial-qmk` `vial`, push it,
then:

```sh
git -C qmk_firmware fetch origin nuphy-air96-v2
git -C qmk_firmware checkout FETCH_HEAD
git -C qmk_firmware submodule update --init --recursive
git add qmk_firmware && git commit -m "chore: bump vial-qmk"
```

Every push builds the firmware in GitHub Actions; the `.bin` is in the run's
artifacts.
