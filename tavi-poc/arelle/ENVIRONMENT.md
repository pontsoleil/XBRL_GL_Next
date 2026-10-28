# Arelle OimTaxonomy environment

The Tavi PoC extension runs in a separate Arelle source checkout at the base commit specified in [APPLY_PATCH.md](APPLY_PATCH.md), with its three patches applied in order. Use **Python 3.10 or later**, with working Tcl/Tk support for the GUI. Python packages cannot supply a missing system/interpreter Tk runtime.

## Installation

From the patched Arelle source root, using a Tk-enabled Python installation:

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -e .
./.venv/bin/python -m pip check
./.venv/bin/python -m tkinter
./.venv/bin/python arelleGUI.pyw
```

These commands use Unix/macOS virtual-environment paths. On Windows, use the corresponding `.venv/Scripts/python.exe` executable. Close the Tk test window before launching Arelle. In the GUI, open **Help → Manage plug-ins**, browse to `arelle/plugin/OimTaxonomy/__init__.py`, and enable **OIM Taxonomy**. Restart if requested.

Open taxonomy JSON files individually; for a sample xBRL-CSV report, open its JSON metadata entry point rather than the CSV alone. See the [PoC overview](../README.md) and [four-model guide](../README_REPRODUCE_4_MODELS.md).

The extension is scoped to the documented Arelle base and patches. A fresh environment does not itself establish a new native-fact, GUI or full specification-conformance PASS. No complete dependency lockfile or universal cross-platform compatibility is claimed.
