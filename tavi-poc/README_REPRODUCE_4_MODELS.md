# Reproducing the four Tavi taxonomy models

This guide describes the published four-model `taxonomy/tavi/` output collection. For each model, the Tuple, OIM and Tavi taxonomy representations are based on the corresponding formal HMD in `semantic-model/HMD/`. The independent `tavi-poc/` experimental taxonomies and instance examples do not share this generation process.

The published HMD-to-Tavi generator produces one JSON taxonomy from one formal 18-column HMD. This guide covers four independent models: COR, COR-JPN, BTX and BTX-PINT. It does not reproduce upstream Specialisation or Graph Walk steps, create View-derived instances, or claim a clean-clone test has been completed.

## Published inputs and reference outputs

| Model | Formal HMD input | Reference taxonomy JSON |
| --- | --- | --- |
| COR | `semantic-model/HMD/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv` | `taxonomy/tavi/accounting-entries/taxonomy.json` |
| COR-JPN | `semantic-model/HMD/accounting-entries-jpn/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv` | `taxonomy/tavi/accounting-entries-jpn/taxonomy.json` |
| BTX | `semantic-model/HMD/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv` | `taxonomy/tavi/business-transactions/taxonomy.json` |
| BTX-PINT | `semantic-model/HMD/business-transactions-pint/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv` | `taxonomy/tavi/business-transactions-pint/taxonomy.json` |

Generator: [`tavi-poc/tools/hmd_to_tavi.py`](tools/hmd_to_tavi.py). Use Python 3.10 or later. Generation requires the Python standard library only. The generator reads the formal 18-column HMD (`value_domain` contract) and creates a new JSON file; it does not read external datatype-mapping CSV files.

## Source-edition relationship for reference comparison

The published **COR** and **BTX** HMD files belong to the current main Canonical HMD set. The four Tavi reference JSON files were accepted against **specific HMD input editions**. Those editions are not necessarily identical to the HMD files currently published at the same paths. The following raw SHA-256 identities distinguish them; they are file identifiers, not requirements to make distinct HMDs equal.

| Model | Current published HMD raw SHA-256 | HMD raw SHA-256 used for accepted reference JSON | Relationship |
| --- | --- | --- | --- |
| COR | `d0fa07a8165a0dac782ad38af78e5593527a09b2dd541d7807bf07c846488f6e` | `1282f2e705c68aac8a232ad5d61b61120edaefa244245a3b5d07391fd3f32c78` | Different editions; reference reproduction is not established from the published HMD alone. |
| COR-JPN | `ada4b1f7cafbe0b3e542f554646f424f5b8a08209777582164ef467e5d9fcce9` | `ada4b1f7cafbe0b3e542f554646f424f5b8a08209777582164ef467e5d9fcce9` | Same recorded input identity. |
| BTX | `14ec10d441fc98f17f17866394504281006a6d441d554389b16d3adca74a6974` | `4e72394c378b46d2c22438f80856f65245ee2f408185ca36df288733ca203c8a` | Different editions; reference reproduction is not established from the published HMD alone. |
| BTX-PINT | `d7a52fa07666d216fd023f59197e76e1ff7734eafb3ae1489da491de6f150c55` | `d7a52fa07666d216fd023f59197e76e1ff7734eafb3ae1489da491de6f150c55` | Same recorded input identity. |

The accepted Tavi reference JSON was generated and validated for the recorded input edition of each model. **Generating from the current public COR or BTX HMD is a separate operation**, not a demonstrated byte-for-byte reproduction of the corresponding reference JSON. A difference against the reference in those two cases must be reported as an edition-dependent result, not automatically as a failed generator. To reproduce an accepted reference exactly, use its accepted HMD input edition, recorded generator and options; first establish that those exact inputs are available. Do not silently substitute the current public HMD, alter a source HMD, or require the main and Tavi input editions to share a SHA. The generator's output and validation have different evidence boundaries from Tuple/OIM generation.

## Generate taxonomies

Run from the repository root. Substitute a fresh writable directory for `<NEW_OUTPUT>`; do not overwrite the published reference outputs. These commands use the **currently published** model HMD paths. They are runnable command examples, not assertions of a newly executed clean-clone test or reproduction of the accepted COR/BTX reference JSON editions. Verify the actual input SHA and record the output edition before comparison.

```sh
python -B tavi-poc/tools/hmd_to_tavi.py --hmd semantic-model/HMD/accounting-entries/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv --output "<NEW_OUTPUT>/accounting-entries/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd semantic-model/HMD/accounting-entries-jpn/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv --output "<NEW_OUTPUT>/accounting-entries-jpn/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd semantic-model/HMD/business-transactions/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv --output "<NEW_OUTPUT>/business-transactions/taxonomy.json" --version 2026-10-26-candidate --include-documentation
python -B tavi-poc/tools/hmd_to_tavi.py --hmd semantic-model/HMD/business-transactions-pint/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv --output "<NEW_OUTPUT>/business-transactions-pint/taxonomy.json" --version 2026-10-26-candidate --include-documentation
```

The version argument is the identifier used by the reference JSON set; the word `candidate` in that identifier is not a statement that the files remain unpublished. The generator rejects an existing output path. It supports 15 source representation terms, including `Identifier`, `Code`, `Text` and `Amount`, with the mappings documented in [the generator guide](../tools/tavi/README_Tavi_4models_datatypes_candidate.md).

## Compare and inspect

For a **reference reproduction comparison**, first verify that the HMD input edition is the same one used to generate the accepted reference JSON in the table above. Only then compare the generated JSON with the corresponding published reference using the project's approved text-content comparison, normalising only CRLF/LF for comparison. For a **current-published-HMD generation** using a different edition (COR or BTX), retain the output as a separate result and do not claim reference identity; differences alone do not demonstrate a generator defect. Preserve original files and raw SHA values. The four models need not share fact identities or structures.

For Tavi DTS validation, use the [Arelle OimTaxonomy patch setup](arelle/APPLY_PATCH.md) and [environment](arelle/ENVIRONMENT.md). Select **one generated JSON per run**, independently of the other model files. From the patched Arelle source checkout, use the existing command-line validation contract:

```sh
"<ARELLE_PYTHON>" -B "<ARELLE_CHECKOUT>/arelleCmdLine.py" --file "<NEW_OUTPUT>/<MODEL_SCOPE>/taxonomy.json" --plugins OimTaxonomy --validate --keepOpen --internetConnectivity offline --disablePersistentConfig --cacheDirectory "<NEW_CACHE>" --logFile "<NEW_LOG>.xml"
```

Replace every angle-bracket placeholder with actual paths. `<MODEL_SCOPE>` is one of `accounting-entries`, `accounting-entries-jpn`, `business-transactions` or `business-transactions-pint`; `<ARELLE_PYTHON>` is the executable in the configured Arelle environment. Use a separate log and suitable cache path for each run, and record the input JSON identity, command, exit status, errors and warnings. Run with the exact Arelle base and three patches described in the patch guide; GUI loading does **not** replace this `--validate` command. The four taxonomy models have **previously recorded** OimTaxonomy DTS validation with zero errors and warnings for their accepted editions. That is historical evidence, not a new run or a guarantee that outputs from different current HMD editions will validate identically. This guide does not introduce a new validation gate beyond the existing procedure.

The PoC does not establish general automated View-to-Tavi instance generation or four-model instance validation. The [Simple and HMD-view report examples](README.md) are separate demonstrations, not substitutes for the four-model taxonomies.
