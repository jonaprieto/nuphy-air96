#pragma once

// Default tapping term. Permissive Hold, Chordal Hold and Flow Tap are set in
// Vial (QMK Settings > Tap-Hold) and saved in jonaprieto.vil.
#undef TAPPING_TERM
#define TAPPING_TERM 250

// Vial: keyboard type id, and Esc + Enter to unlock it for editing.
#define VIAL_KEYBOARD_UID {0xA4, 0x68, 0x5C, 0x41, 0xA4, 0xF3, 0xFC, 0xCC}
#define VIAL_UNLOCK_COMBO_ROWS { 0, 3 }
#define VIAL_UNLOCK_COMBO_COLS { 0, 13 }
#define VIAL_COMBO_ENTRIES 8

// Layers 6-8: Symbols + Numbers, Math, Mouse.
#undef DYNAMIC_KEYMAP_LAYER_COUNT
#define DYNAMIC_KEYMAP_LAYER_COUNT 9
