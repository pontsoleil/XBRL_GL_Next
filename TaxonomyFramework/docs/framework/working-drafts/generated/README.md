# Generated semantic-model CSV artifacts

These CSV files are derived artifacts for private collaborative review,
machine-readable comparison, and reproducibility checks. They are not the
authoritative semantic input. The authoritative source is
[`../FSM.xlsx`](../FSM.xlsx).

All artifacts have status `for-review` and sharing and redistribution status
`license-hold`. They are not an approved specification. Do not edit these CSV
files manually. Whenever `FSM.xlsx` changes, regenerate and verify all four
files together.

## Artifact register

| Artifact | Purpose | Columns | Data rows | Bytes | SHA-256 |
|---|---|---:|---:|---:|---|
| [FSM.csv](FSM.csv) | `FSM` sheet in the formal FSM contract | 15 | 500 | 156,672 | `836508A329B7FD8D05C267EF9E63329E30947B7AD1DE5BAA885B02202934BCF7` |
| [FSM_btx.csv](FSM_btx.csv) | `FSM_btx` sheet in the formal FSM contract | 15 | 77 | 23,511 | `DAC94254F8C4F5302E5BA7DA89CA7E738BC8642AC0EDBA5E441147B7443DEF82` |
| [BSM.csv](BSM.csv) | Specialization output from both FSM CSV files | 16 | 713 | 217,308 | `6002FE391E96A2323C28635C205C9A7D63B05FD1430A12761D22D30897D169BF` |
| [LHM.csv](LHM.csv) | Full combined LHM/HMD for Accounting Entries and Business Transactions | 17 | 498 | 211,806 | `D2BD7473639A686EB3BB60B9476F2D9546BD3EDC505C318916B9612C37C00FB8` |

## Provenance

- Source Git commit: `1ed6668486dfadcc6ed7a6ca1598c11bb4b77dfd`
- Input `FSM.xlsx` SHA-256:
  `A22F37E69168341F38F77987FD4B0D38BF732527C418A700CE766D45D991F3E2`
- Generation time: 2026-07-30 06:03 JST
- Sheet extraction:
  `extract_fsm_sheet` in `tests/test_semantic_pipeline.py`
- Specialization: `tools/semantic/specialization.py`
- Graph Walk: `tools/semantic/graphwalk.py`

The commands below are run from the repository root. `$run` is a directory
outside the repository.

```powershell
python.exe -B -c "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); from test_semantic_pipeline import extract_fsm_sheet; extract_fsm_sheet(Path(sys.argv[2]), sys.argv[4], Path(sys.argv[3]))" tests TaxonomyFramework/docs/framework/working-drafts/FSM.xlsx "$run/FSM.csv" FSM
python.exe -B -c "import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); from test_semantic_pipeline import extract_fsm_sheet; extract_fsm_sheet(Path(sys.argv[2]), sys.argv[4], Path(sys.argv[3]))" tests TaxonomyFramework/docs/framework/working-drafts/FSM.xlsx "$run/FSM_btx.csv" FSM_btx
python.exe -B tools/semantic/specialization.py --in "$run/FSM.csv" --in "$run/FSM_btx.csv" --out "$run/BSM.csv" --diagnostics "$run/specialization.diagnostics.json"
python.exe -B tools/semantic/graphwalk.py "$run/BSM.csv" "$run/LHM.csv" --root "cor:Accounting Entries" --root "btx:Business Transactions" --diagnostics "$run/graphwalk.diagnostics.json"
```

Diagnostics are verification-only outputs and are not registered.

## Contracts and CSV format

- FSM: 15 columns
- BSM: 16 columns
- LHM/HMD: 17 columns
- Encoding: UTF-8 with BOM
- Record line ending: LF
- Delimiter: comma
- Header: present
- Quoting: Python `csv` minimal quoting; fields containing a comma, quote, or
  line break are double-quoted, and an embedded quote is escaped as `""`.
- Git handling: `-text` preserves the generated LF byte stream without
  checkout-time line-ending conversion. Definition fields retain source
  whitespace, including intentional spaces before embedded line breaks.

The LF record ending is the actual format emitted by the current extraction
helper and semantic tools. It differs from the CRLF record ending commonly
produced by Excel CSV export but remains RFC 4180-compatible in field quoting.

## Reproducibility

The complete pipeline was run independently in two external temporary
directories from the same Git commit and input workbook. For every artifact,
the two byte streams and SHA-256 values matched. The registered files are the
first run's byte-identical outputs and can be regenerated using the commands
above.
