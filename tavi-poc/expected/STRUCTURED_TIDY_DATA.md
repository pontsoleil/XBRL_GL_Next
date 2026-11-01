# Structured Tidy Data — example and display scope

The historical Simple Tavi example used `JSON report metadata` (withdrawn; historical reference), a [historical nine-column CSV report](../profiles/single-account-date-r2/instance/tavi-inst.csv) and the `minimal taxonomy` (withdrawn; historical reference). Its withdrawn metadata and patched Arelle environment are historical context.

The historical OimTaxonomy Structured Tidy Data presentation is a **transposed view reconstructed from loaded native facts**, with nine Item rows and six occurrence columns for the Simple example. Fact selection is linked to the native fact and its Properties, including dimensions, unit and decimals where applicable. This view is not a literal reformatting of the CSV and must not be interpreted as an independent source of facts.

The [static HTML demonstrations](../README.md#published-scope) display Table Template and taxonomy JSON with a transposed CSV. Static HTML viewing is separate from native Arelle fact selection and from formal Tavi validation.

## Current Journal Entry PoC

The [current CSV](../instance/tavi-ins.csv) has 18 columns and seven records. The [current taxonomy](../taxonomy/tavi-tax.json) defines three cubes and embeds the Table Template. The [static viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html) displays that CSV transpose and the exact embedded source text. Scoped static checks do not establish parent-occurrence existence or full Tavi PWD conformance.
