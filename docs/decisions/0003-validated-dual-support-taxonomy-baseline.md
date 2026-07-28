# ADR-0003: Validated OIM/Palette dual-support taxonomy as the conformance baseline

- Status: Accepted
- Date: 2026-07-25

## Context

The review material under `docs/ChatGPT/` proposes changes to the taxonomy
architecture and generator. Some proposals describe a theoretically preferred
layout, but the project already has an OIM/Palette dual-support taxonomy that
has been validated by XMLSpy 2026 and Arelle.

The validated entry point imported into this repository is:

`xBRL-GL2.0_btx/plt/plt-oim-2026-12-31.xsd`

Its SHA-256 is:

`D38FEF5202594041F6F4985B2355A63667E420F7A9E5D44E93359F8CDB35B72A`

The entry point has eleven schema references, no missing local schema
references, is valid in XMLSpy 2026, and produces no XBRL validation errors in
Arelle.

## Decision

Use the validated 2026-12-31 OIM/Palette dual-support taxonomy as the normative
technical baseline for generator and architecture decisions.

The accepted assembly pattern is:

1. A module schema such as `btx/btx-2026-12-31.xsd` declares stable concepts and
   references its presentation linkbase.
2. A content schema such as `plt/btx-content-2026-12-31.xsd` includes the
   same-namespace module schema and imports the content schemas on which it
   depends.
3. The OIM palette imports the module declaration schemas and imports the root
   content schema that closes the selected content dependency graph.
4. The OIM palette references the label and definition linkbases needed by the
   profile.
5. Presentation relationships may be reached through imported module schemas.
   They do not need to be referenced directly by the palette when DTS
   reachability is already complete.

The generator must reproduce this dependency graph or another graph that is
demonstrably equivalent. It is not a requirement that the palette directly
import every content schema. It is a requirement that every selected concept,
type and linkbase be reachable from the entry point without relying on an
undeclared working-directory convention.

XML Schema and XBRL validity are necessary release conditions. They do not by
themselves prove that the selected dimensions, periods, units or business
semantics are correct. Semantic changes therefore require profile-level
expected-result tests in addition to XMLSpy and Arelle validation.

## Consequences

- Generator changes are evaluated against a working, validated taxonomy rather
  than against an untested target architecture.
- `taxonomy/oim/prototype` can be updated from the validated 2026-12-31 file
  set while keeping `taxonomy/tuple` and `taxonomy/experiments` independent.
- Direct palette imports and direct palette linkbase references are not added
  merely for stylistic uniformity.
- A generated release must pass XML parsing, local-reference checks, XMLSpy
  schema validation and Arelle XBRL validation.
- The validated file set remains a baseline snapshot; future semantic model
  changes must be regenerated rather than manually patched into the snapshot.
