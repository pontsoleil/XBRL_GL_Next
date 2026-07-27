# ADR-0006: Logical module-qualified Class identity

## Status

Proposed for design approval on 2026-07-26. Program and data migration are
deferred to separately approved tasks.

## Context

XBRL GL Next combines multiple logical modules to define one message. A Class
name alone is therefore not sufficient when different modules contain the
same `class_term`. The existing FSM and BSM have no `associated_module`
column. The existing LHM also mixes owner and referenced module meaning in
some R rows.

QName prefixes and namespace URIs belong to syntax bindings. Using them to
identify logical Classes would couple the semantic model to one binding and
would make multi-binding support ambiguous.

## Decision

1. Class identity is `(module, class_term)`.
2. Referenced Class identity is
   `(associated_module, associated_class)`.
3. Association property identity is
   `(property_term, associated_module, associated_class)`.
4. `property_type`, `multiplicity`, property ID, FSM ID, `sequence` and input
   order are not Association identity fields.
5. `module` and `associated_module` are logical module identifiers. They are
   not QName prefixes, XML namespace prefixes or namespace URIs.
6. QName, prefix and namespace URI mapping is performed only by syntax
   bindings.
7. FSM and BSM add `associated_module` and retain `associated_class`.
   LHM/HMD retains `associated_module` but does not carry `associated_class`;
   Graph Walk resolves the target from BSM and preserves it in traversal state
   and hierarchy.
8. Both reference fields are required for Association and Specialization rows,
   including references within the same module.
9. Empty or unknown reference fields are input model errors. A processor may
   continue unaffected PoC work, but must not infer a target or reflect the
   invalid Association in the BSM.
10. Managed strings use XML Schema `token`-equivalent whitespace collapse.
    Free-text definitions preserve line breaks and internal whitespace.
11. After collapse, ASCII uppercase in `module` and `associated_module` is
    lowercased. Other identifiers remain case-sensitive; collisions are errors.
12. QName-form semantic names or Class references are input errors. Normal
    processing never splits them or infers module, prefix or namespace.
13. A Specialization super Class is identified by
    `(associated_module, associated_class)`.
14. Reference emits R and PK-derived `type=A, identifier=REF` rows, then stops
    traversal. REF inherits the referenced module from R and never parses its
    name to infer the target.
15. The R name is `property_term + "_ " + associated_class` when role exists,
    otherwise `associated_class`, without a QName prefix.
16. The contracts apply from taxonomy version `2026-12-31`.
17. BSM consists of the fourteen FSM columns followed only by `id`; it has no
    `element` column.
18. LHM is the complete logical hierarchy table. HMD is the part identified or
    extracted for one root Class. Both use the same 17-column contract, and
    HMD identity is `(module, class_term)`.
19. If a Specialization super Class cannot be resolved uniquely, the complete
    child Class and all its properties are excluded from normal BSM output.
    Child-local properties remain visible only in diagnostics.
20. FSM and BSM may contain same-named Class candidates from different
    modules. Within one HMD, however, each `class_term` is selected from
    exactly one module. Associations that would mix same-named Classes from
    different modules in the same hierarchy are input-selection errors.
21. HMD Class selection is explicit as `(selected_module, class_term)`.
    Processors must not select a candidate by input order, Association order,
    Class name, QName or naming convention.
22. When an Aligned Class specializes a Shared Class, the selected concrete
    specialized Class is emitted in the HMD. The Shared super Class may be
    used during Specialization but is not emitted as a second same-named Class
    in that HMD.
23. After module selection and hierarchy expansion, `semantic_path` must be
    unique in the LHM/HMD. A duplicate is an input-selection or modeling
    error; it is not repaired by `element` suffixing.

## Consequences

- The proposed contracts are FSM 14 columns, BSM 15 columns and LHM/HMD 17
  columns.
- LHM/HMD removes `path`, `abbreviation_path`, `xpath` and `associated_class`
  and retains `semantic_path`, `associated_module` and `class_term`.
- Existing FSM, BSM and LHM/HMD require an explicit reviewed migration. No
  owner-module fallback or name-based inference is permitted.
- `specialization.py`, `graphwalk.py`, their fixtures and the taxonomy
  generator require coordinated but separately approved implementation work.
- A manifest must identify the contract version so that equal column counts
  cannot be mistaken for compatible schemas.
- Legacy migration requires an explicit audited, human-reviewed mapping and is
  not a normal-processing fallback.
- The prohibition applies to mixing same-named Class candidates in one HMD;
  it does not prohibit combining differently named Classes from multiple
  modules.
- This amendment clarifies QName rejection, whitespace classes, module
  lowercase normalization and R／REF handling without changing the three
  identity tuples.

## Relationship to ADR-0005

This ADR supersedes ADR-0005 only for Class identity, Association identity,
column counts and the treatment of logical modules. ADR-0005 remains in force
for element generation, DNM removal, PoC continuation, diagnostics,
sidecars and manifest-based processing state where those provisions do not
conflict with this ADR.
