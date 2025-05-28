![image.png](fig/){width=1157 height=674}

To further clarify the structure and relationships in OIM-based taxonomies—especially for readers transitioning from XBRL 2.1—we also propose including a visual explanation of how **multi-level cube hierarchies** are structured using `domain-member` relationships.

Each **hierarchical level** in the framework forms its own **cube**, and **higher-level cubes connect to lower-level cubes** via a `domain-member` arc. The arc uses a `targetRole` that points to the lower-level cube’s `network role`, and the **target of the arc** is the **primary item** of the lower-level cube.

In this framework:

* Each cube is identified by its **hypercube** (e.g., `h_cor_accountingEntries`, `h_cor_entryHeader`, etc.).
* Each cube has an associated **primary item** prefixed with `p_` (e.g., `p_cor_accountingEntries`, `p_cor_entryHeader`, `p_cor_entryDetail`), which is **abstract** and serves as the parent in `domain-member` relationships to its reportable concepts.
* Reportable **member concepts** (e.g., `cor_entryNumber`, `cor_amount`) are attached to the `p_` primary item using the `domain-member` arc within the same network.
* Cube-specific dimensions are defined as typed dimensions (e.g., `d_cor_accountingEntries`, `d_cor_entryHeader`, etc.) and associated with the cube using `hypercube-dimension` arcs.

This layered model aligns directly with **XBRL Dimensions 1.0**, while offering a **hierarchical tidy data representation** well-suited for xBRL-CSV serialization.

We recommend including the corresponding figure as an informative annex to illustrate this pattern and support practical implementations.