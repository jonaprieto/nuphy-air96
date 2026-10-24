/*
Copyright 2023 @ Nuphy <https://nuphy.com/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include QMK_KEYBOARD_H
#include "layer_names.h"
#include "math_keys.h"
#include "user_kb.h"

#define NAV   (M_LAYER + 1)
#define SYM   (NAV + 1)
#define MATH  (SYM + 1)
#define MOUSE (MATH + 1)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {

// layer 0 Mac
[MAC_BASE] = LAYOUT_96_ansi(
   KC_ESC,    KC_BRID,   KC_BRIU,   TASK,        SEARCH,       MAC_VOICE, MAC_DND,   KC_MPRV,     KC_MPLY,   KC_MNXT,    KC_MUTE,    KC_VOLD,    KC_VOLU,     PRT_AREA,  KC_DEL,     KC_HOME,   KC_END,    KC_PGUP,   KC_PGDN,
   KC_GRV,    KC_1,      KC_2,      KC_3,        KC_4,         KC_5,      KC_6,      KC_7,        KC_8,      KC_9,       KC_0,       KC_MINS,    KC_EQL,      KC_BSPC,               KC_NUM,    KC_PSLS,   KC_PAST,   KC_PMNS,
   KC_TAB,    KC_Q,      KC_W,      KC_E,        KC_R,         KC_T,      KC_Y,      KC_U,        KC_I,      KC_O,       KC_P,       KC_LBRC,    KC_RBRC,     KC_BSLS,               KC_P7,     KC_P8,     KC_P9,     KC_PPLS,
   LCTL_T(KC_ESC), LCTL_T(KC_A), LALT_T(KC_S), LGUI_T(KC_D), LSFT_T(KC_F), KC_G, KC_H, RSFT_T(KC_J), RGUI_T(KC_K), RALT_T(KC_L), RCTL_T(KC_SCLN), KC_QUOT, KC_ENT,              KC_P4,     KC_P5,     KC_P6,
   KC_LSFT,              KC_Z,      KC_X,        KC_C,         KC_V,      KC_B,      KC_N,        KC_M,      KC_COMM,    KC_DOT,     KC_SLSH,    KC_RSFT,                KC_UP,      KC_P1,     KC_P2,     KC_P3,     KC_PENT,
   KC_LCTL,   KC_LALT,   KC_LGUI,                              LT(NAV, KC_SPC),                                          MO(SYM),    MO(1),      TG(MATH),     KC_LEFT,   KC_DOWN,    KC_RGHT,   KC_P0,     KC_PDOT),
// layer 1 Mac Fn
[MAC_FN] = LAYOUT_96_ansi(
   LOCK_SCR,  KC_F1,     KC_F2,     KC_F3,       KC_F4,        KC_F5,     KC_F6,     KC_F7,       KC_F8,     KC_F9,      KC_F10,     KC_F11,     KC_F12,      PRT_SCR,   KC_INS,     _______,   _______,   _______,   _______,
   _______,   LNK_BLE1,  LNK_BLE2,  LNK_BLE3,    LNK_RF,       _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   LINK_PREV,  _______,   LGUI(KC_GRV), LCTL(KC_UP), _______,   _______,   _______,   _______,     _______,   _______,    _______,    DEV_RESET,  SLEEP_MODE,  BAT_SHOW,              _______,   _______,   _______,   _______,
   _______,   LGUI(KC_TAB), LCTL(KC_LEFT), LCTL(KC_DOWN), LCTL(KC_RGHT), _______, _______, _______,  _______,   _______,    _______,    _______,    _______,                            _______,   _______,   _______,
   MO(4),                SCMD(LCTL(KC_4)), SCMD(KC_3), RGB_TEST,  SCMD(KC_5), BAT_NUM,   _______,     MO(4),     RM_SPDD,    RM_SPDU,    _______,    MO(4),                  RM_VALU,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    _______,    _______,     RM_NEXT,   RM_VALD,    RM_HUEU,   _______,   _______),
// layer 2 win
[WIN_BASE] = LAYOUT_96_ansi(
   KC_ESC,    KC_F1,     KC_F2,     KC_F3,       KC_F4,        KC_F5,     KC_F6,     KC_F7,       KC_F8,     KC_F9,      KC_F10,     KC_F11,     KC_F12,      KC_PSCR,   KC_DEL,      KC_HOME,  KC_END,    KC_PGUP,   KC_PGDN,
   KC_GRV,    KC_1,      KC_2,      KC_3,        KC_4,         KC_5,      KC_6,      KC_7,        KC_8,      KC_9,       KC_0,       KC_MINS,    KC_EQL,      KC_BSPC,                KC_NUM,   KC_PSLS,   KC_PAST,   KC_PMNS,
   KC_TAB,    KC_Q,      KC_W,      KC_E,        KC_R,         KC_T,      KC_Y,      KC_U,        KC_I,      KC_O,       KC_P,       KC_LBRC,    KC_RBRC,     KC_BSLS,                KC_P7,    KC_P8,     KC_P9,     KC_PPLS,
   KC_CAPS,   KC_A,      KC_S,      KC_D,        KC_F,         KC_G,      KC_H,      KC_J,        KC_K,      KC_L,       KC_SCLN,    KC_QUOT,    KC_ENT,                              KC_P4,    KC_P5,     KC_P6,
   KC_LSFT,              KC_Z,      KC_X,        KC_C,         KC_V,      KC_B,      KC_N,        KC_M,      KC_COMM,    KC_DOT,     KC_SLSH,    KC_RSFT,                KC_UP,       KC_P1,    KC_P2,     KC_P3,     KC_PENT,
   KC_LCTL,   KC_LGUI,   KC_LALT,                              KC_SPC,                                                   KC_RALT,    MO(3),      KC_RCTL,     KC_LEFT,   KC_DOWN,     KC_RGHT,  KC_P0,     KC_PDOT),
// layer 3 win Fn
[WIN_FN] = LAYOUT_96_ansi(
   LOCK_SCR,  KC_BRID,   KC_BRIU,   KC_CALC,     SEARCH,       KC_F5,     KC_F6,     KC_MPRV,     KC_MPLY,   KC_MNXT,    KC_MUTE,    KC_VOLD,    KC_VOLU,     PRT_AREA,  KC_INS,       _______,  _______,   _______,   _______,
   _______,   LNK_BLE1,  LNK_BLE2,  LNK_BLE3,    LNK_RF,       _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,                _______,  _______,   _______,   _______,
   LINK_PREV,  _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    DEV_RESET,  SLEEP_MODE,  BAT_SHOW,               _______,  _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,                             _______,  _______,   _______,
   MO(4),                _______,   _______,     RGB_TEST,     _______,   BAT_NUM,   _______,     MO(4),     RM_SPDD,    RM_SPDU,    _______,    MO(4),                  RM_VALU,     _______,  _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    _______,    _______,     RM_NEXT,   RM_VALD,     RM_HUEU,  _______,   _______),
// layer 4 function
[M_LAYER] = LAYOUT_96_ansi(
   QK_REBOOT, DB_TOGG,   RF_DFU,    _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    DEBOUNCE_D,  DEBOUNCE_I, _______,   _______,     _______,   _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    SLEEP_D,    SLEEP_I,     _______,                _______,   _______,   _______,   _______,
   _______,   _______,   MACWIN_TG, _______,     _______,      _______,   _______,   _______,     _______,   SIDE_1,     _______,    _______,    SLEEP_NOW,   _______,                _______,   _______,   _______,   _______,
   CAPS_WORD, AWAKE_TG,   _______,   DEBOUNCE_T,  FROW_SWAP,    GAME_MODE, _______,   _______,     SOCD_TOG,  _______,    _______,    _______,    _______,                             _______,   _______,   _______,
   _______,              _______,   _______,     _______,      _______,   _______,   NUMLOCK_IND, _______,   SIDE_SPD,   SIDE_SPI,   _______,    _______,                SIDE_VAI,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    MO(4),      _______,     SIDE_MOD,  SIDE_VAD,    SIDE_HUI,  _______,   _______),
// layer 5 nav (hold Space on the Mac layer)
[NAV] = LAYOUT_96_ansi(
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   LGUI(KC_LEFT), LALT(KC_LEFT), LALT(KC_RGHT), LGUI(KC_RGHT), _______,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   _______,   KC_LCTL,   KC_LALT,   KC_LGUI,     KC_LSFT,      _______,   KC_LEFT,   KC_DOWN,     KC_UP,     KC_RGHT,    _______,    _______,    _______,                            _______,   _______,   _______,
   _______,              LGUI(KC_Z), LGUI(KC_X), LGUI(KC_C), LGUI(KC_V), SCMD(KC_Z), KC_BSPC,   KC_DEL,    KC_PGDN,    KC_PGUP,    _______,    _______,                _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  MO(MOUSE),  _______,    _______,     _______,   _______,    _______,   _______,   _______),
// layer 6 symbols + numbers (hold right Cmd); number row 6..= are Vial macros M0-M6
[SYM] = LAYOUT_96_ansi(
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______,   _______,
   _______,   KC_EXLM,   KC_AT,     KC_HASH,     KC_PERC,      KC_AMPR,   MC_0,      MC_1,        MC_2,      MC_3,       MC_4,       MC_5,       MC_6,        _______,               _______,   _______,   _______,   _______,
   _______,   KC_CIRC,   KC_UNDS,   KC_LBRC,     KC_RBRC,      KC_DLR,    KC_PLUS,   KC_7,        KC_8,      KC_9,       KC_ASTR,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   _______,   KC_BSLS,   KC_LCBR,   KC_LPRN,     KC_RPRN,      KC_RCBR,   KC_MINS,   KC_4,        KC_5,      KC_6,       KC_SLSH,    KC_EQL,     _______,                            _______,   _______,   _______,
   _______,              KC_TILD,   KC_PIPE,     KC_LT,        KC_GT,     KC_GRV,    KC_0,        KC_1,      KC_2,       KC_3,       KC_DOT,     _______,                _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    _______,    MO(MATH),    _______,   _______,    _______,   _______,   _______),
// layer 7 math (tap right Ctrl: on, tap again: off); LaTeX while Symbols is held too
[MATH] = LAYOUT_96_ansi(
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______,   _______,
   _______,   MA_1,      MA_2,      MA_3,        MA_4,         MA_5,      MA_6,      MA_7,        MA_8,      MA_9,       MA_0,       MA_MINS,    MA_EQL,      _______,               _______,   _______,   _______,   _______,
   _______,   MA_Q,      MA_W,      MA_E,        MA_R,         MA_T,      MA_Y,      MA_U,        MA_I,      MA_O,       MA_P,       MA_LBRC,    MA_RBRC,     MA_BSLS,               _______,   _______,   _______,   _______,
   _______,   MA_A,      MA_S,      MA_D,        MA_F,         MA_G,      MA_H,      MA_J,        MA_K,      MA_L,       MA_SCLN,    MA_QUOT,    _______,                            _______,   _______,   _______,
   _______,              MA_Z,      MA_X,        MA_C,         MA_V,      MA_B,      MA_N,        MA_M,      MA_COMM,    MA_DOT,     MA_SLSH,    _______,                _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______),
// layer 8 mouse (hold Space + right Cmd)
[MOUSE] = LAYOUT_96_ansi(
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   _______,   _______,     _______,   _______,    _______,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   _______,   _______,   _______,   _______,     _______,      _______,   MS_WHLL,   MS_WHLD,     MS_WHLU,   MS_WHLR,    _______,    _______,    _______,     _______,               _______,   _______,   _______,   _______,
   _______,   KC_LCTL,   KC_LALT,   KC_LGUI,     KC_LSFT,      _______,   MS_LEFT,   MS_DOWN,     MS_UP,     MS_RGHT,    _______,    _______,    _______,                            _______,   _______,   _______,
   _______,              _______,   _______,     _______,      _______,   _______,   MS_BTN1,     MS_BTN2,   MS_BTN3,    _______,    _______,    _______,                _______,    _______,   _______,   _______,   _______,
   _______,   _______,   _______,                              _______,                                                  _______,    _______,    _______,     _______,   _______,    _______,   _______,   _______)
};

// Chordal Hold: a hold counts only with a key on the other hand. The numpad
// skews the geometric guess on a 96% board, so spell it out. Caps and Space
// are '*' so they hold with either hand (e.g. Caps+C).
const char chordal_hold_layout[MATRIX_ROWS][MATRIX_COLS] PROGMEM = LAYOUT_96_ansi(
    'L', 'L', 'L', 'L', 'L', 'L',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
    'L', 'L', 'L', 'L', 'L', 'L',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
    'L', 'L', 'L', 'L', 'L', 'L',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
    '*', 'L', 'L', 'L', 'L', 'L',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
    'L', 'L', 'L', 'L', 'L', 'L',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R',
    'L', 'L', 'L',  '*',  'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'
);

// While Nav, Symbols, Math or Mouse is on, light the keys that do something there and turn
// the rest off, like the board does for Fn (mint) and M (mustard). Each kind of key has its
// own colour, so a layer's shape is easy to remember.
enum { BLUE, CYAN, GREEN, AMBER, ORANGE, PURPLE, PINK, RED, YELLOW, WHITE };
static const uint8_t palette[][3] = {
    [BLUE] = {0x00, 0x40, 0xFF}, [CYAN] = {0x00, 0xC0, 0xFF},   [GREEN] = {0x00, 0xFF, 0x30},
    [AMBER] = {0xFF, 0x90, 0x00}, [ORANGE] = {0xFF, 0x40, 0x00}, [PURPLE] = {0x90, 0x00, 0xFF},
    [PINK] = {0xFF, 0x00, 0x80},  [RED] = {0xFF, 0x00, 0x00},    [YELLOW] = {0xFF, 0xE0, 0x00},
    [WHITE] = {0x60, 0x60, 0x60},
};

static uint8_t key_colour(uint8_t layer, uint16_t kc) {
    if (IS_MODIFIER_KEYCODE(kc)) {
        return WHITE;
    }
    if (kc >= MA_1 && kc < MA_END) {
        static const uint8_t math[] = {PURPLE, GREEN, CYAN, AMBER}; // Greek, sets, relations, operators
        return IS_LAYER_ON(SYM) ? PINK : math[math_groups[kc - MA_1]];
    }
    switch (layer) {
        case NAV:
            if (kc >= KC_RIGHT && kc <= KC_UP) return BLUE;            // arrows
            if (IS_QK_MODS(kc) && (kc & 0xFF) >= KC_RIGHT && (kc & 0xFF) <= KC_UP) return CYAN; // word, line
            if (kc == KC_PGUP || kc == KC_PGDN) return PURPLE;
            return GREEN;                                              // undo ... redo, Bksp, Del
        case SYM:
            if (kc >= KC_1 && kc <= KC_0) return GREEN;                // numbers
            if (IS_QK_MACRO(kc)) return CYAN;                          // -> => |> ...
            switch (kc) {
                case KC_LBRC: case KC_RBRC: case KC_LCBR: case KC_RCBR:
                case KC_LPRN: case KC_RPRN: case KC_LT: case KC_GT:
                    return ORANGE;                                     // brackets
            }
            return YELLOW;                                             // other symbols
        case MOUSE:
            if (kc >= MS_UP && kc <= MS_RGHT) return RED;              // pointer
            if (kc >= MS_WHLU && kc <= MS_WHLR) return ORANGE;         // scroll
            return YELLOW;                                             // clicks
    }
    return WHITE;
}

bool rgb_matrix_indicators_user(void) {
    uint8_t layer = get_highest_layer(layer_state);
    if (layer < NAV) {
        return true;
    }
    rgb_required = 1; // shows with the backlight off too
    for (uint8_t row = 0; row < MATRIX_ROWS; row++) {
        for (uint8_t col = 0; col < MATRIX_COLS; col++) {
            uint8_t led = g_led_config.matrix_co[row][col];
            if (led == NO_LED) {
                continue;
            }
            uint16_t kc = keycode_at_keymap_location(layer, row, col);
            if (kc == KC_TRNS || kc == KC_NO) {
                rgb_matrix_set_color(led, 0, 0, 0);
            } else {
                const uint8_t *c = palette[key_colour(layer, kc)];
                rgb_matrix_set_color(led, c[0], c[1], c[2]);
            }
        }
    }
    return true;
}

// Math keys: the LaTeX name while Symbols is held, else a shortcut the menu bar app turns into
// the symbol (macOS's Unicode Hex Input garbles typed code points). Shift picks the second of
// each pair. Key i sends F13 + i % 8 with modifier set i / 8, plus Shift for the second symbol.
static const uint8_t math_mods[] = {
    MOD_BIT(KC_LCTL), MOD_BIT(KC_LALT), MOD_BIT(KC_LGUI),
    MOD_BIT(KC_LCTL) | MOD_BIT(KC_LALT), MOD_BIT(KC_LCTL) | MOD_BIT(KC_LGUI), MOD_BIT(KC_LALT) | MOD_BIT(KC_LGUI),
};
_Static_assert(MA_END - MA_1 <= 8 * sizeof(math_mods), "more math keys than shortcuts");

// Menu bar watcher (tools/watch.py): last key and combo, reported on request.
static uint16_t watch_keys, watch_keycode, watch_combos, watch_combo_keycode;
static uint8_t  watch_row, watch_col;

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (record->event.pressed) {
        if (IS_COMBOEVENT(record->event)) {
            watch_combos++;
            watch_combo_keycode = keycode;
        } else if (IS_KEYEVENT(record->event)) {
            watch_keys++;
            watch_keycode = keycode;
            watch_row     = record->event.key.row;
            watch_col     = record->event.key.col;
        }
    }

    if (keycode < MA_1 || keycode >= MA_END) {
        return true;
    }
    if (record->event.pressed) {
        const math_key_t *k     = &math_keys[keycode - MA_1];
        const uint8_t     mods  = get_mods();
        const bool        shift = (mods | get_oneshot_mods()) & MOD_MASK_SHIFT;
        clear_mods();
        clear_oneshot_mods();
        if (IS_LAYER_ON(SYM)) {
            send_string(shift ? k->tex_shift : k->tex);
        } else {
            const uint8_t i = keycode - MA_1;
            const uint8_t m = math_mods[i / 8] | (shift ? MOD_BIT(KC_LSFT) : 0);
            register_mods(m);
            tap_code(KC_F13 + i % 8);
            unregister_mods(m);
        }
        set_mods(mods);
    }
    return false;
}

// Watcher status: [cmd, version, layer state (4), default layer state (4), mods,
// caps word, key count (2), last keycode (2), row, col, combo count (2), combo keycode (2)].
#define WATCH_CMD 0x60

void raw_hid_receive_kb(uint8_t *data, uint8_t length) {
    if (data[0] != WATCH_CMD) {
        data[0] = id_unhandled;
        return;
    }
    const uint32_t layers = layer_state, defaults = default_layer_state;
    data[1] = 1;
    memcpy(&data[2], &layers, 4);
    memcpy(&data[6], &defaults, 4);
    data[10] = get_mods() | get_oneshot_mods();
    data[11] = is_caps_word_on();
    memcpy(&data[12], &watch_keys, 2);
    memcpy(&data[14], &watch_keycode, 2);
    data[16] = watch_row;
    data[17] = watch_col;
    memcpy(&data[18], &watch_combos, 2);
    memcpy(&data[20], &watch_combo_keycode, 2);
}
