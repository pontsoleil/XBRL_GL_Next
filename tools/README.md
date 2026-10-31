# Tools: implementation map

The Framework defines requirements, while these scripts implement particular steps. A Part association is **a scope map, not a claim of complete compliance with every clause**.

| Tool | Relevant Framework | Input → output / purpose |
|---|---|---|
| `semantic/specialisation.py` | Parts 1, 4 | class Specialisation: FSM/semantic source → BSM; aligned extensions specialise Shared model classes |
| `semantic/graphwalk.py` | Part 1 | BSM graph → Candidate LHM |
| `semantic/post_graphwalk.py` | Part 1 | Reviewed LHM → formal 18-column HMD |
| `semantic/validate_lhm.py` | Part 1 | LHM structural checks |
| `taxonomy/xBRLGL_TaxonomyGenerator.py` | Parts 1, 2, 3 | Formal HMD → root-specific Tuple/OIM taxonomy DTS |
| `taxonomy/datatype_binding.py` | Part 1 plus binding | Semantic to physical datatype binding for relevant Tuple/OIM generator |
| `instance/instance_core.py` | Part 1 view concepts; Parts 2, 3 | Approved View CSV/workbook → scoped Tuple/OIM instances |
| `instance/structured_oim.py` | Part 3 | Structured xBRL-CSV report serialization |
| `instance/tuple_binding.py` | Parts 1, 2 | Structured CSV/HMD/overlay-based Tuple conversion, distinct from instance_core View path |

Run tools from an explicitly chosen project root and with accepted source version; use a new WORK output path. Details: [semantic model](../semantic-model/README.md), [Tavi discussion draft](../tavi-poc/README.md), [COR View1](instance/README_COR_VIEW1.md). Experimental discussion draft based on Tavi PWD 2026-09-01; formal conformance has not been established.
