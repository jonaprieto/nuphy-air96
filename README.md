# nuphy-air96

QMK keymap for a NuPhy Air96 V2 (ANSI), built on
[ablasik/nuphy-qmk](https://github.com/ablasik/nuphy-qmk), pinned as the
`qmk_firmware` submodule.

```sh
git clone --recurse-submodules git@github.com:jonaprieto/nuphy-air96.git
make build   # QMK's Docker image -> nuphy_air96_v2_ansi_jonaprieto.bin
make flash   # build, then flash with dfu-util (brew install dfu-util)
```

To flash, connect the USB cable and put the board in the bootloader: hold
Fn+M+Esc for 3 s, or plug the cable in while holding Esc. If it ever fails to
boot, pull the Caps Lock keycap, hold the button under it and plug in.

Upgrade the firmware base:

```sh
git -C qmk_firmware fetch --tags
git -C qmk_firmware checkout <tag>
git -C qmk_firmware submodule update --init --recursive
git add qmk_firmware && git commit -m "chore: bump nuphy-qmk to <tag>"
```

Every push builds the firmware in GitHub Actions; the `.bin` is in the run's
artifacts.
