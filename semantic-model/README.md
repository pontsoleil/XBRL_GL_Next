# Semantic model and HMD inputs

The common meaning layer is defined in Taxonomy Framework **Part 1**. **COR** and **BTX** are Shared models; **COR-JPN** specialises COR classes and **BTX-PINT** specialises BTX classes as Aligned extensions governed by **Part 4**. The four model outputs must be treated as independent, self-contained HMD/taxonomy results.

## Processing and ownership

1. FSM → BSM through Specialisation (see `tools/semantic/specialisation.py`).
2. BSM → Candidate LHM through Graph Walk (`graphwalk.py`).
3. Human-reviewed LHM is authoritative within its approved scope; do not overwrite it by regenerating a candidate.
4. Reviewed LHM → formal 18-column `value_domain` HMD via Post-Graph Walk (`post_graphwalk.py`).
5. The selected formal HMD is input to the Tuple/OIM or Tavi taxonomy generator; these do **not** repeat Specialisation/Graph Walk.

Review `FSM/`, `BSM/`, `LHM/`, `HMD/`, and `views/` in their distinct roles. The four accepted Tavi source HMDs are model-specific (460/482/470/787 rows), and the old published COR/BTX HMDs are not automatically identical to their 2026-10-26 successors. Use the verified revision and SHA in the [Tavi guide](../tavi-poc/README_REPRODUCE_4_MODELS.md).

View-defined instance generation is a separate workstream; no generic Tavi instance automation is claimed here.
