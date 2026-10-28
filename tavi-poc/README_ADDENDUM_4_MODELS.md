# Four-model Tavi taxonomy scope

The current Tavi PoC publishes four independent HMD-derived taxonomy JSON files: [COR](../taxonomy/tavi/accounting-entries/taxonomy.json), [COR-JPN](../taxonomy/tavi/accounting-entries-jpn/taxonomy.json), [BTX](../taxonomy/tavi/business-transactions/taxonomy.json) and [BTX-PINT](../taxonomy/tavi/business-transactions-pint/taxonomy.json).

COR and BTX are Shared models; COR-JPN and BTX-PINT are Aligned extensions in the semantic framework. The taxonomy generator consumes an existing formal HMD for one root at a time. It does not perform the upstream semantic-model transformations or generate instance reports.

For inputs, commands and validation scope, use the [four-model reproduction guide](README_REPRODUCE_4_MODELS.md). For the distinct Simple, Full v3 and Single Account HMD-view examples, see the [main Tavi PoC README](README.md).


The four published Tavi model taxonomies belong to the three-representation `taxonomy/` output collection and use formal model-specific HMDs. The independent `tavi-poc/` Simple, Full v3 and HMD-view demonstrations use their own prototype inputs and are not outputs of the same taxonomy generation pipeline. The planned common View-to-Tuple/OIM/Tavi instance workflow is not implemented as a completed three-format process.
