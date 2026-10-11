# Environment

## Requirements

Python >= 3.10 is required by the public base's pyproject.toml. The verified macOS environment used Python 3.10.1, arm64, with Tcl/Tk 8.6.12. The base's runtime.txt specifies Python 3.10.20; that exact version was not tested in this investigation.

Use a Tk-enabled Python distribution. tkinter, _tkinter and Tcl/Tk are interpreter/distribution or system prerequisites, not Arelle core dependencies installed by pip. Installing Arelle cannot provision a missing Tk runtime. See the [Python tkinter documentation](https://docs.python.org/3/library/tkinter.html).

## Clean installation example

After checking out the exact public base and applying the verified patch, run these commands from the separate Arelle checkout. Select a Tk-enabled python3 installation first.

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
./.venv/bin/python -m pip check
./.venv/bin/python -m tkinter
./.venv/bin/python arelleGUI.pyw --plugins OimTaxonomy
```

The tkinter command opens a small diagnostic window; close it before starting Arelle. Open the package's metadata JSON, not its CSV alone.

Do not copy or reuse another environment's site-packages. A fresh isolated venv with modern pip successfully resolved the core Python dependencies via editable installation. pip check and GUI/OimTaxonomy imports passed. The initial pip 21.2.4 lacked support for the project's editable pyproject installation; updating pip resolved that prerequisite. Optional plugin, development, server and database dependencies are outside this minimal installation.

The clean-environment check covered installation and imports. It did not rerun the complete native fact or GUI display acceptance in that new venv. Dependency versions are not locked by this package; other Python, Tcl/Tk and macOS combinations remain unverified.

## Known limitations / macOS notes

### Finder -10006

Arelle's existing CntlrWinMain.main() macOS activation code asks Finder to set the `python` process frontmost through AppleScript. The -10006 write failure was reproduced with the OimTaxonomy plugin both disabled and enabled. It is not specific to this plugin. The GUI itself starts and the controlled processes exited successfully. Process targeting and the OS-side reason for the denied write require separate investigation. This PoC patch does not fix it.

### IMKCFRunLoopWakeUpReliable

The message `error messaging the mach port for IMKCFRunLoopWakeUpReliable` was observed during manual GUI use. It was not reproduced in one controlled run each of minimal Tk, Arelle without OimTaxonomy, and Arelle with OimTaxonomy. Its cause remains undetermined. This PoC does not fix it.
