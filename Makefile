KM  := jonaprieto
BIN := nuphy_air96_v2_ansi_$(KM).bin
PY  := .venv/bin/python

.PHONY: build flash gui save watch

# Same image and steps as CI (qmk/.github qmk_userspace_build.yml).
# -c: clean build, so objects stamped by the Docker VM clock never go stale.
build:
	docker info >/dev/null 2>&1 || colima start
	docker run --rm -v "$(CURDIR)":/userspace -w /userspace ghcr.io/qmk/qmk_cli:latest sh -c '\
		pip install -q -r qmk_firmware/requirements.txt && \
		qmk config user.qmk_home=/userspace/qmk_firmware user.overlay_dir=/userspace >/dev/null && \
		qmk userspace-compile -c'

# Unlock with Esc + Enter when asked; the board then enters its bootloader by itself.
# The saved layout is loaded back afterwards. FLASH_ARGS=--clear-eeprom starts from keymap.c.
flash: build $(PY)
	$(PY) tools/flash.py $(BIN) $(FLASH_ARGS)

# Vial's source, run natively; the released Mac app is Intel-only and unsigned.
$(PY):
	uv venv -q -p 3.12 .venv
	uv pip install -q -p $(PY) PyQt5==5.15.11 hidapi==0.15.0 simpleeval==1.0.8 certifi==2026.10.23
	uv pip install -q -p $(PY) --no-deps fbs==0.9.0

gui: $(PY)
	$(PY) tools/vial.py

# Commit and push the layout saved from Vial (File > Save current layout) or the menu bar.
save:
	git add jonaprieto.vil
	git diff --cached --quiet && echo "layout unchanged" || { git commit -q -m "layout: update saved Vial layout" && git push -q; }

# Menu bar watcher: link the plugin into SwiftBar's plugin folder.
SWIFTBAR = $(shell defaults read com.ameba.SwiftBar PluginDirectory)
watch: $(PY)
	ln -sf "$(CURDIR)/tools/nuphy-watch.sh" "$(SWIFTBAR)/nuphy-watch.sh"
