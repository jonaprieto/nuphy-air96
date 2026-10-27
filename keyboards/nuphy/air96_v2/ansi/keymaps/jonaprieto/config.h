#pragma once

// Default tapping term. Permissive Hold, Chordal Hold and Flow Tap are set in
// Vial (QMK Settings > Tap-Hold) and saved in jonaprieto.vil.
#undef TAPPING_TERM
#define TAPPING_TERM 250

// How long a tap the board makes up is held: the tap of a tap/hold key, math
// keys, LaTeX strings, Vial macros. The board's 2 ms is fine on the cable but
// over Bluetooth and 2.4G the press can be lost. Vial keeps its own copy for
// tap/hold keys and math keys (QMK Settings > Tap code delay, saved in
// jonaprieto.vil); this is its default and the one LaTeX strings use.
#undef TAP_CODE_DELAY
#define TAP_CODE_DELAY 20
#undef DYNAMIC_KEYMAP_MACRO_DELAY
#define DYNAMIC_KEYMAP_MACRO_DELAY TAP_CODE_DELAY

// Vial: keyboard type id, and Esc + Enter to unlock it for editing.
#define VIAL_KEYBOARD_UID {0xA4, 0x68, 0x5C, 0x41, 0xA4, 0xF3, 0xFC, 0xCC}
#define VIAL_UNLOCK_COMBO_ROWS { 0, 3 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 13 }
#define VIAL_COMBO_ENTRIES 8

// Layers 6-8: Symbols + Numbers, Math, Mouse.
#undef DYNAMIC_KEYMAP_LAYER_COUNT
#define DYNAMIC_KEYMAP_LAYER_COUNT 9
