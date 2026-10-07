# Journal Entries reviewed LHM materialisation

Journal Entries is a purpose-specific COR specialisation with an independent
Tuple/OIM DTS. It does not replace the general Accounting Entries model.

The semantic source authority is the `LHM reviewed` sheet in:

`docs/ChatGPT/2026/202610/20261007/20261007_1616/JournalEntries_FSM_BSM_LHM_with_reviewed.xlsx`

Accepted workbook SHA-256:
`1C18AEE97DA64E3DA55D3603B900CA4F1AB882483D0C9713496F31515277DAC5`

`XBRL_GL_Next_LHM_reviewed.csv` is the canonical CSV materialisation of that
reviewed sheet for the registered CSV-based processing tools. It carries the
same 44 rows and 18 columns, including `value_domain` in column 9. It is not
an independently editable semantic authority. Future changes require controlled
review of the source authority and regeneration of the dependent artefacts.

The reviewed `local_name`, `semantic_path`, multiplicity and XPath are retained.
On 7 October 2026, the user approved removal of line-end spaces/tabs only
inside quoted CSV fields for publication. The canonical materialisation and
HMD apply this explicit exception to the original workbook bytes; all other
cell values and ordering are retained. The workbook remains unchanged.
The generated HMD and its execution manifest are under
`semantic-model/HMD/journal-entries/`. The independent DTS is under
`taxonomy/journal-entries/`, with entry points:

- `tuple/jnl_journalEntries/jnl-all-2026-12-31.xsd`
- `oim/jnl_journalEntries/jnl-all-oim-2026-12-31.xsd`

The stable module namespace is
`https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/jnl`.
Generation provenance and the taxonomy manifest are maintained separately under
`taxonomy/provenance/journal-entries/`.

This standalone HMD is not added to the existing Accounting Entries / Business
Transactions two-HMD input set in `semantic-model/LHM_for_taxonomy/`.
WORK canonical placement does not authorise Official GIT publication.
