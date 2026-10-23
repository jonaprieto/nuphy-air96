# nuphy-air96

Vial keymap for a NuPhy Air96 V2 (ANSI). The `qmk_firmware` submodule is the
`nuphy-air96-v2` branch of
[jonaprieto/vial-qmk](https://github.com/jonaprieto/vial-qmk): Vial's QMK plus
the board from [ablasik/nuphy-qmk](https://github.com/ablasik/nuphy-qmk) v1.2.4.

```sh
git clone --recurse-submodules git@github.com:jonaprieto/nuphy-air96.git
make build   # QMK's Docker image -> nuphy_air96_v2_ansi_jonaprieto.bin
make flash   # build, then flash with dfu-util (brew install dfu-util)
```

To flash, connect the USB cable and put the board in the bootloader: hold
Fn+M+Esc for 3 s, or plug the cable in while holding Esc. If it ever fails to
boot, pull the Caps Lock keycap, hold the button under it and plug in.

Upgrade the firmware base: rebase the fork's `nuphy-air96-v2` branch on
`vial-kb/vial-qmk` `vial`, push it, then:

```sh
git -C qmk_firmware fetch origin nuphy-air96-v2
git -C qmk_firmware checkout FETCH_HEAD
git -C qmk_firmware submodule update --init --recursive
git add qmk_firmware && git commit -m "chore: bump vial-qmk"
```

Every push builds the firmware in GitHub Actions; the `.bin` is in the run's
artifacts.
