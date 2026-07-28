# ADR-0005: Semantic core, element generation and Association identity

## Status

Accepted for design documentation on 2026-07-26. Program implementation is
deferred to a separately approved task.

Partially superseded by ADR-0006 for Class identity, Association identity,
logical module references, FSM／BSM／LHM column counts and binding-stage HMD
selection. The remaining
decisions below continue to apply where they do not conflict with ADR-0006.

## Decision

1. BSM uses the semantic core defined by ADR-0006. It consists of the fourteen
   FSM columns followed by `id` and does not contain `element`.
2. Graph Walk produces the 17-column LHM defined by ADR-0006. HMD is the
   message-level subset selected from that LHM during binding, not a separate
   Graph Walk product. A single-root LHM is content-identical to that root's HMD.
   `path`, `abbreviation_path`, `xpath` and `associated_class` are removed.
   XML placement is a syntax-binding concern.
3. `semantic_path` is the human-readable identity used to allocate
   `element`, and every `semantic_path` in one LHM or selected HMD must be unique. Graph
   Walk generates a prefix-free lowerCamelCase XML Schema NCName after the
   path is fixed. It starts with the terminal path segment and prepends the
   nearest ancestor segments until the name is unique within the logical
   `module`. Adjacent duplicate words are emitted once. Input order,
   `sequence`, automatic numbers and hashes are never used to resolve a
   collision. A collision that remains after all segments are used requires
   an explicitly approved element mapping.
4. DNM and Graph Walk `-o` are not supported by the target architecture.
5. Association and Class identity are defined by ADR-0006. Association property
   identity is `(property_term, associated_module, associated_class)`.
   `property_term` may be empty and is compared as empty; it is never inferred
   or generated from `associated_class` or other fields. `property_type`,
   multiplicity, property ID and sequence remain outside the identity key.
   QName, prefix and namespace URI are assigned and validated only by a
   syntax binding.
6. An empty association role is valid and remains empty. A role is never
   inferred or generated.
7. Within one class, duplicate Association identity keys are input errors
   detected before Specialization or extension. No duplicate is selected or
   merged by ID, FSM ID, sequence or input order. During the PoC, this does not
   abort the whole model: unaffected classes and unambiguous properties are
   processed, while ambiguous properties are omitted and reported as
   unresolved or requiring review.
8. WORK-specific provenance, inheritance, external-reference, context and
   presentation fields are held in responsibility-specific extensions or
   sidecars joined by stable canonical `id`.
9. A PoC BSM and its diagnostic report are one result. Processing state,
   error/warning counts and the report reference belong in the manifest, not
   in the semantic core.
10. Only infrastructure failures such as unreadable or unparseable input,
    missing identification columns, unwritable output or risk of overwriting
    existing files are fatal for the target input.
11. `element` is required for C, A and REF rows. An R row represents a
    Reference Association and normally has no taxonomy concept: when its
    multiplicity upper bound is one, `element` is empty. When the upper bound
    exceeds one or is unbounded, the R row defines a dimension and `element`
    is required.

## Consequences

- Existing producers and consumers require migration to the ADR-0006
  contracts or an explicit versioned adapter.
- Existing DNM-only invocations and tests are removal candidates.
- Source models with duplicate Association identity keys remain invalid, but
  PoC processing may produce a clearly marked partial BSM for unaffected
  content. Ambiguous properties are never silently chosen or merged.
- A clean release requires correction of all reported model errors even when a
  PoC partial BSM was generated.
- The same semantic concept appearing in more than one HMD uses the same
  `element` when its `module` and `semantic_path` are the same.
- Element uniqueness is checked per logical module, not per HMD and not across
  all modules.
- The extension manifests and stable ID rules must be implemented and tested
  before WORK-specific columns can be removed from the processing CSV.
