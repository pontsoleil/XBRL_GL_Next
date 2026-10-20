# COR View1: Excel → defined View CSV → instances

## Adopted source contract

The actual generation input is semantic-model/views/accounting-entries/LHM_view1_cor.csv. It is the complete existing LHM_view1_cor View exported from the accepted workbook, not the 18-column structural HMD CSV and not the old diagnostic38-cell list.

The CSV has40 records including the header and15 columns: the existing11 structure fields, the existing occurrence-definition rows and four value columns corresponding to L–O. It retains35 selected model rows and38 values. It is UTF-8 without BOM; ordinary record separators are LF. Excel Date cells are exported through the existing lexical conversion as ISO dates. Other values, quoting and embedded field content are preserved by standard CSV writing. No sample value is invented.

The View selects items from the adopted HMD and is defined in accordance with that structure. HMD sequence/module/level/type/datatype/local_name/semantic_path and permitted multiplicity are checked against the defined CSV. CSV physical row numbers are source locations, never a substitute for semantic_path or model hierarchy. The View itself defines that upper-bound-one classes do not add an occurrence level or dimension. The generator does not infer, flatten, repair or recalculate the View definition. The previously attempted diagnostic occurrence-depth inference was removed before adoption.

Candidate and Reviewed LHM may change local_name/multiplicity under the user's current decision; the adopted issued HMD remains the authority for this View execution. No Candidate/Reviewed/HMD value is changed by this tool registration.

## Commands

Run in authorised WORK staging, with a new output directory and the approved HMD/taxonomy inputs. Do not generate directly inside Canonical or Official.

python -B instance_core.py export-csv --workbook <approvedExcel> --sheet LHM_view1_cor --output <newCSV>
python -B instance_core.py generate --csv <approvedViewCSV> --sheet LHM_view1_cor --config <approvedConfig> --output <newWORKids> --output-profiles tuple oim --validate-profiles tuple oim --arelle <Arelle>

For the accepted aggregate View use its aggregate config and --output-profiles oim --validate-profiles oim. Templates are documentation; exact executed commands are in the1133 task record. The old --workbook input remains for historical compatibility, but the adopted normal route here is Excel export then --csv generation.

CSV content SHA uses comparison-only CRLF→LF for record separators, preserving quoted values. raw SHA, content SHA and workbook provenance SHA are distinct. Input comparison does not rewrite files. The config pins csv_comparison_sha256; workbook_sha256 is retained as original export provenance in CSV mode, not used to open the workbook. generate --csv never calls the Excel reader.

The registered CSV configs resolve hmd/taxonomy_root/tuple_entry/oim_entry/view_definition relative to the config file; no historical task runtime is auto-imported. structured_oim.py must be beside instance_core.py. All other imports are standard library. Existing tuple_binding.py has a different Structured CSV contract and is not replaced.

## Acceptance and boundaries

The new CSV-input runs emitted38 facts per representation; full OIM aspects/values and Tuple tree equal accepted1812. Three of five output files are raw-identical; Tuple and separateJSON differ only innamespace ordering and are not called file-identical. Those two were newly Arelle-validated; aggregate CSV+JSON validation is reused from1812 after raw identity and unchangedDTS confirmation. New outputs are task candidates only: existingCOR70 instances and manifests are not replaced.

Original0456 code, the old Excel-direct1812 commands and extraction evidence remain historical. The newCSV did not exist as the historical1812 input. The source workbook is WORK semantic-model/LHM_reviewed_COR_BTX_view.xlsx, rawSHA6E0F5CFAEC876A144BF5C3C343928ACC0E1BED24ECB1310525186ADF12674BC6. The structural HMD rawSHA isD0FA07A8165A0DAC782AD38AF78E5593527A09B2DD541D7807BF07C846488F6E, already registered in the two existing HMD locations.

Canonical adoption does not lift Official publication holds. Rights/licences/attribution/namespace, View1 data and evidence sharing approvals still apply. The previous70-member Canonical set is preserved; any future Official comparison uses the whole approved79-member union, not an independently chosen subset.

## Header-total correction successor (2026-10-20)

Run 20261020_1215/cor-view1-header-total-correction changes only totalDebits and totalCredits from 1100 to 5500. The workbook SHA quoted above identifies the historical 1133 source, not the corrected current workbook. Current workbook SHA is 599104C9EF7D70E6232E5C9863B315BEFA33AE763E7942070318780E545E4D67; current View CSV SHA is 3B2296ABA9B18CF47DF276373EB920BDD5B286ED041CEA4A002ED880C837078B. The same generator and HMD produce 38 facts, with only these two values changed and all aspects retained. Tuple, separate OIM and aggregate OIM each passed current Arelle validation. The accepted successor replaces the five registered instances and the related input/configuration/evidence records within the fixed 79-path set. Historical 1133 records remain unchanged. Publication holds remain in force.
