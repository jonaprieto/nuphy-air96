#!/bin/sh
# <xbar.title>NuPhy Air96</xbar.title>
# <xbar.desc>Active layer, last key and combo; keymap view and tap-hold settings.</xbar.desc>
# <swiftbar.type>streamable</swiftbar.type>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideLastUpdated>true</swiftbar.hideLastUpdated>
# Installed by `make watch` as a link in SwiftBar's plugin folder.
repo="$(cd "$(dirname "$(readlink "$0" || echo "$0")")/.." && pwd)"
exec "$repo/.venv/bin/python" "$repo/tools/watch.py"
