KM  := jonaprieto
BIN := nuphy_air96_v2_ansi_$(KM).bin

.PHONY: build flash gui

# Same image and steps as CI (qmk/.github qmk_userspace_build.yml).
# -c: clean build, so objects stamped by the Docker VM clock never go stale.
build:
	docker info >/dev/null 2>&1 || colima start
	docker run --rm -v "$(CURDIR)":/userspace -w /userspace ghcr.io/qmk/qmk_cli:latest sh -c '\
		pip install -q -r qmk_firmware/requirements.txt && \
		qmk config user.qmk_home=/userspace/qmk_firmware user.overlay_dir=/userspace >/dev/null && \
		qmk userspace-compile -c'

# Board must be in the bootloader: Fn+M+Esc for 3 s on the cable, or plug in holding Esc.
flash: build
	dfu-util -w -a 0 -d 0483:DF11 -s 0x08000000:leave -D $(BIN)

PY := .venv/bin/python

# Vial's source, run natively; the released Mac app is Intel-only and unsigned.
$(PY):
	uv venv -q -p 3.12 .venv
	uv pip install -q -p $(PY) PyQt5==5.15.11 hidapi==0.15.0 simpleeval==1.0.8 certifi==2026.10.23
	uv pip install -q -p $(PY) --no-deps fbs==0.9.0

gui: $(PY)
	cd vial-gui/src/main/python && $(CURDIR)/$(PY) main.py
