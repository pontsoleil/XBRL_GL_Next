**English** | [日本語](architecture_ja.md)

# Architecture baseline

## 1. Semantic pipeline

The project uses one semantic source and two syntax bindings.

```text
UN/CEFACT CCL and existing XBRL GL
                 |
                 v
       Foundational Semantic Model (FSM)
          Shared / Aligned / Distinct
                 |
          specialization by profile
                 v
        Business Semantic Model (BSM)
                 |
              graph walk
                 v
 Logical Hierarchical Model / HMD (LHM)
           /                     \
          v                       v
 XBRL 2.1 Tuple binding     OIM dimensional binding
                                  |
                                  v
                              xBRL-CSV
```

FSM, BSM and LHM are semantic artifacts. XSD, linkbases, JSON metadata and CSV
tables are syntax artifacts. A concept must not acquire a different meaning
merely because the serialization changes.

### FSM superclass specialization

A superclass defined in the FSM is specialized and extended by defining its
child class in the FSM. The child class uses the superclass properties as its
base and may remove, modify or add properties.

Class identity is `(module, class_term)`. A referenced Class is identified by
`(associated_module, associated_class)`. Association property identity is
`(property_term, associated_module, associated_class)`. Association kind and
multiplicity are not part of the identity key and may be changed by the child
class. For example, a matching association may be changed
from reference to aggregation and its multiplicity may be changed.

Managed strings use XML Schema `token`-equivalent `whiteSpace="collapse"`;
free-text definitions preserve line breaks and internal whitespace. ASCII
uppercase in `module` and `associated_module` is lowercased after collapse;
other identifiers remain case-sensitive. `module` and `associated_module` are
logical module identifiers. QName-form semantic names and Class references are
input errors; QName, prefix and namespace URI belong only to syntax binding.
An empty role
remains empty and is not inferred. Within one class, each
`(association role, associated module, associated class)` key may occur only once,
regardless of association kind, property ID or sequence. A duplicate is an
input error detected before specialization; no candidate is selected by ID or
input order. During the PoC, such a model error does not abort the whole run.
Unambiguous classes and properties continue into the BSM, while ambiguous
properties are omitted and reported as unresolved or requiring review. The BSM
and its diagnostic report form one PoC result.

Association and Specialization rows require both `associated_module` and
`associated_class`, even for a reference within the same module. Missing or
unknown references are model errors. PoC processing may continue elsewhere,
but the invalid Association is not reflected in the BSM.

A child-class FSM row with multiplicity `0` is a removal directive for the
matching inherited property. The removed property is not defined in the
effective child-class BSM and is not emitted to the LHM/HMD or taxonomy. The
FSM row carrying multiplicity `0` is not itself an effective property
definition.

If a new child Association has no matching superclass property and carries
multiplicity `0` or `0..0`, it is also not emitted as an effective property.
Unreadable input, unparseable syntax, missing columns needed to identify
classes or properties, unwritable output, and risks of corrupting an existing
file are fatal input-level failures. Other module, logical-class-reference and
Association ambiguities are model errors: they are reported and isolated while
processing continues for unaffected classes.

### Canonical semantic tables

The BSM semantic core has 15 columns: the 14 FSM columns followed only by
`id`. It has no `element` column. WORK-specific provenance, external-reference,
context and presentation fields are held in responsibility-specific extensions
or sidecars.

A PoC BSM with model errors is not presented as a clean result. Its manifest
records `processing_status`, `error_count`, `warning_count` and `report_file`.
The diagnostic report carries property-level details; an optional status
sidecar may carry machine-readable row-level disposition. These fields are not
added to the 15-column semantic core.

LHM is the complete logical hierarchy table; HMD is the portion identified or
extracted for one root Class. Both use the same 17-column contract and
terminology. The contract excludes `path`, `abbreviation_path`, `xpath` and
`associated_class`, retains `semantic_path`, `associated_module` and
`class_term`, and identifies an HMD by `(module, class_term)`.
Reference traversal emits an R row and target-PK-derived
`type=A, identifier=REF` rows, copies the target module from R to REF, and then
stops. REF names are never parsed to infer a target. XML placement belongs to a
syntax binding, not to the semantic model.
Graph Walk generates `element` after the semantic path is fixed. It starts with
the LC3 form of the terminal name and, when necessary, prepends non-repeating
words from parent to ancestor until the result is model-wide unique. Matching
is case-insensitive and recognizes whitespace and CamelCase word boundaries.
If all ancestor words are insufficient, generation fails rather than appending
an automatic number.

DNM output and the Graph Walk `-o` option are not part of the target
architecture.

The 14-column FSM, 15-column BSM and 17-column LHM/HMD contracts apply from
taxonomy version `2026-12-31` and are identified by manifest contract name and
version.

## 2. Governance layers

### Shared

World-common standard concepts and structures that are used across countries,
legal and institutional systems, industries, and implementations. A concept is
not Shared merely because it originates in an international standard or
UN/CEFACT CCL. Broad cross-domain use is required. Invoice, Shipment, and
Customs may be Shared root Classes, while only their genuinely cross-domain
ASBIEs and BBIEs belong in Shared. Shared entries should have syntax-neutral
identifiers, definitions, datatype/representation terms and semantic paths.
Changes require central review and strong compatibility rules.

### Aligned

Standard definitions aligned with regional standards, national standards,
laws, regulations, or published industry standards. International-standard or
CCL components whose use is limited to a particular domain also belong here.
Aligned entries retain explicit provenance and mappings to upstream identifiers
and releases. They are selected by profiles and do not automatically become
part of every instance.

### Distinct

Definitions specific to an enterprise, enterprise group, product, individual
trading relationship, or other closed community. Distinct is not the location
for public legal, regulatory, national, regional, or published industry
standards; those belong in Aligned.

## 3. Module responsibilities

The initial baseline uses the following responsibility split. Names are
provisional until the module decision record is accepted.

| Module | Responsibility |
| --- | --- |
| `cor` | Ledger/document envelope and stable accounting core |
| `bus` | Reusable business party, address, contact and measurable structures |
| `muc` | Multicurrency structures |
| `taf` | Tax structures |
| `ehm` | Enhanced measurement structures |
| `usk` | US GAAP/accounting-specific structures retained for compatibility |
| `btx` | Source business transactions and transaction documents |
| `sta` | Statistical observations, measures and classifications |
| `lnk` | Links among transactions, ledger entries, evidence and reports |
| `gen` | Generic datatypes and representation terms |
| `plt` | Profile/palette entry points and syntax assembly |

`btx`, `sta` and `lnk` must not be treated as dumping grounds. Shared reusable
components belong in a shared semantic library; the modules own domain roots,
constraints and profile assembly.

## 4. OIM realization

Tuple containment is represented in OIM by explicit dimensions and definition
linkbase relationships. Each repeated class level receives an explicit typed or
explicit dimension as appropriate. Parent-child navigation, primary item to
hypercube attachment, closed/open behavior and defaults must be specified rather
than inferred from CSV row order.

Every supported profile provides:

- a taxonomy entry point;
- module and root selection;
- definition linkbase(s) defining cubes and hierarchy;
- xBRL-CSV JSON metadata and table templates;
- a mapping from semantic path to concept and dimensions;
- positive and negative conformance examples.

## 5. Compatibility

Migration from the 2015/2017 Tuple taxonomy is managed by a machine-readable
mapping table. Each old concept or tuple path is classified as unchanged,
renamed, moved, split, merged, deprecated or unsupported. Compatibility claims
are made per profile, not for the repository as a whole.
