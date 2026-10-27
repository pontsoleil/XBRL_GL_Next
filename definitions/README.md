# Definitions and bindings

This directory provides supporting taxonomy definitions: `taxonomy/datatype_mapping.csv`, `taxonomy/datatype_override.csv`, `taxonomy/selector_overlay.csv` and `taxonomy/XBRL_GL_Next_VD.csv`. Consult the consuming generator and its documented authority to determine which files it actually reads. Part 1 governs common semantics/value domains; Parts 2 and 3 govern binding-specific use. The `hmd_to_tavi.py` PoC currently uses its **own in-code 15-type mapping**, not these external CSV files. Do not infer a tested external mapping dependency from file co-location.
