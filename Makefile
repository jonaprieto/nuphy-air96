KM  := jonaprieto
BIN := nuphy_air96_v2_ansi_$(KM).bin

.PHONY: build flash

# Same image and steps as CI (qmk/.github qmk_userspace_build.yml).
build:
	docker info >/dev/null 2>&1 || colima start
	docker run --rm -v "$(CURDIR)":/userspace -w /userspace ghcr.io/qmk/qmk_cli:latest sh -c '\
		pip install -q -r qmk_firmware/requirements.txt && \
		qmk config user.qmk_home=/userspace/qmk_firmware user.overlay_dir=/userspace >/dev/null && \
		qmk userspace-compile'

# Board must be in the bootloader: Fn+M+Esc for 3 s on the cable, or plug in holding Esc.
flash: build
	dfu-util -w -a 0 -d 0483:DF11 -s 0x08000000:leave -D $(BIN)
