"""Start the Vial editor from the submodule, with the math keys named (see kb.py).

Holds kb.VIAL_LOCK while open, so the menu bar watcher lets go of the keyboard.
"""

import os
import runpy
import sys

import kb

with kb.watcher_paused():
    os.chdir(kb.VIAL / "python")
    sys.argv = ["main.py"]
    runpy.run_path("main.py", run_name="__main__")
