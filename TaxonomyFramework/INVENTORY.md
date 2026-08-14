# Phase 1 Sample Inventory

## Status

- Inventory date: 2026-08-14
- Status: Phase 1 sample / collaborative review
- Public release approved: No
- Taxonomy version: 2026-12-31

The inventory and validation date does not alter the taxonomy namespace/version `2026-12-31`.

## Framework documents

| File | SHA-256 |
| --- | --- |
| `XBRL_GL_Next_Requirements_Specification.docx` | `3D2F29ADBA3B715A9BF04C6E180458363D2F1E85DDDF8CFF25E6A0326486FC48` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules.docx` | `76770CC8E01E84A630C7A64B679C620249D5204AF471AF1E16A86840D6D2C65D` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_2_Tuple_palette_taxonomy.docx` | `24CE142D7992DFD99E1F34A6F1E5560B17D4A364051ED36C9CED0D8BD0A18A3F` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_3_OIM_palette_taxonomy.docx` | `E11C9C6F8355FD2CFA3CA48EC65E29C5374BA05EF32014B74669E2A928136094` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_4_Aligned_pool_for_extension.docx` | `E7ED58A41F636E83C78475D09A4D470179828E367F126A79D61625F040A37C72` |

## Semantic source and pipeline artifacts

```text
semantic-model/FSM.xlsx
  ↓ export formal FSM sheets
semantic-model/FSM/FSM.csv
semantic-model/FSM/FSM_btx.csv
  ↓ Specialisation
semantic-model/BSM/BSM.csv
  ↓ Graph Walk
semantic-model/LHM/LHM_candidate.csv
  ↓ human semantic review
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.xlsx
  ↓ Post-Graph Walk
semantic-model/LHM_for_taxonomy/
  XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv
  XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv
  manifest.csv
```

| File | Rows / used range | Columns | SHA-256 |
| --- | ---: | ---: | --- |
| `semantic-model/FSM.xlsx` | `FSM` A1:O504; `FSM_btx` A1:O506 | 15 per sheet | `A22F37E69168341F38F77987FD4B0D38BF732527C418A700CE766D45D991F3E2` |
| `semantic-model/FSM/FSM.csv` | 500 | 15 | `836508A329B7FD8D05C267EF9E63329E30947B7AD1DE5BAA885B02202934BCF7` |
| `semantic-model/FSM/FSM_btx.csv` | 77 | 15 | `DAC94254F8C4F5302E5BA7DA89CA7E738BC8642AC0EDBA5E441147B7443DEF82` |
| `semantic-model/BSM/BSM.csv` | 713 | 16 | `6002FE391E96A2323C28635C205C9A7D63B05FD1430A12761D22D30897D169BF` |
| `semantic-model/LHM/LHM_candidate.csv` | 498 | 18 | `7679BAA3BEC60B187ACD033239FF6D3B1A2CC3092171A7F3FFEA07F7B2694721` |
| `semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv` | 496 | 18 | `ECDBE773CCB6408BFE702AAAF495F56049FEFB4D0A1A14D72FAB142BB8A87FB9` |
| `semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.xlsx` | four sheets: A1:T497, A1:R497, A1:R221, A1:R279 | 20/18/18/18 | `1CF1F4DFA8C3D3F6302C2DB9B925EA33761A283E3E7F7C1BFBC58B9B964FD700` |
| `semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv` | 220 | 18 | `E9481DAF7A3403771FCD9F67FC078229354CEE697A7199F0943AA883648D4B29` |
| `semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv` | 276 | 18 | `A1FE079A36EB38D15911BFDE28A37FBF6470767E349FC4241AC8D632EF1D70CA` |
| `semantic-model/LHM_for_taxonomy/manifest.csv` | 2 | 12 | `7E96458955EB8123031D47E3039D9ECD6B06F687BB2D6AD111E5C16C52807BBA` |

The candidate-to-reviewed LHM transition is a human review boundary. Candidate and reviewed artifacts are not expected to have identical SHA-256 values, and the reviewed LHM must not be overwritten by automated regeneration. Generation from the reviewed LHM through the root-specific HMDs to the taxonomy is deterministic. `manifest.csv` is an execution/verification artifact, not a Taxonomy Generator model input.

## Canonical execution tools

| File | SHA-256 |
| --- | --- |
| `tools/semantic/specialization.py` | `9B5E78993A724744386904329D0FA00CC2ADD0B0BCAB46BECFADB775A5E48366` |
| `tools/semantic/graphwalk.py` | `2CFC9F6868D04E173B6752E2AB4A1A4B18038AAE010A1AEB0E136ECE5068CD0E` |
| `tools/semantic/post_graphwalk.py` | `985D217CB150C7A00181BC3D0AC9DF8350DC458A2E09C3310FC110024E944DA7` |
| `tools/semantic/validate_lhm.py` | `22EF2D1C7CE5A3643A23AF11D7D07A01759F14781A8D10BC80E9DD22D892127D` |
| `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` | `205FD43B730993C573ED55228FA4E01BE490A17CC1177EACDD9A995E2AA05447` |

## Canonical tests

| File | SHA-256 |
| --- | --- |
| `tests/test_specialization.py` | `5C063A889FB4134CDDBE1FDB48D0018139BCB029BB92E0BCA95D0E4257204B0C` |
| `tests/test_graphwalk.py` | `CED82615697CEDD47113AD9A9307B6F3AF26ED8B00E73ECEE90EADA073DDAF0A` |
| `tests/test_post_graphwalk.py` | `19499A11C4E3A767BCBED1EFDAA07F612482911B21BA37B16CB4E0016CD998E1` |
| `tests/test_semantic_pipeline.py` | `9ECDF0249BCA942BF9ABD506FF9512F0DD62C78367D4E98DB935BE7780487EF6` |
| `tests/test_v5_taxonomy_generator.py` | `89D4CA7F06CBDC5F102CF92361E88C96E534F028DEEC677F44E461FA900C52E8` |
| `tests/check_generated_package.py` | `B44C593D374AC534C9B4AB40BE2DE33E366134687195DF07CDDCD4F1B04E24C1` |

## Generated sample taxonomy

`taxonomy/` is a 56-file sample taxonomy package generated from the formal HMDs. It contains two Tuple and two OIM entry points:

- `taxonomy/tuple/cor_accountingEntries/cor-all-2026-12-31.xsd`
- `taxonomy/tuple/btx_businessTransactions/btx-all-2026-12-31.xsd`
- `taxonomy/oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd`
- `taxonomy/oim/btx_businessTransactions/btx-all-oim-2026-12-31.xsd`

## Sample instances

`ids/` contains the sample instances:

- `ids/tuple/accountingEntries-journalEntry.xml`
- `ids/tuple/businessTransactions-vendorInvoice.xml`
- `ids/oim/accountingEntries-journalEntry.json`
- `ids/oim/accountingEntries-journalEntry.csv`
- `ids/oim/businessTransactions-vendorInvoice.json`
- `ids/oim/businessTransactions-vendorInvoice.csv`

The OIM JSON metadata files are the xBRL-CSV entry points.

## Validation baseline

- Python unittest discovery, WORK and GIT: 70 tests passed, failures 0, errors 0.
- Package checker: taxonomy files 56; local references 3,821; unresolved local files 0; unresolved local fragments 0; dimensional locators 850; failures 0.
- Arelle 2.44.1 taxonomy entry points: 4/4, errors 0, warnings 0.
- Arelle 2.44.1 sample instance entry points: 4/4, errors 0, warnings 0.
- XMLSpy GUI: Tuple/OIM DTS manually confirmed on 2026-08-12. No repeat GUI validation is required because the taxonomy content is unchanged.
