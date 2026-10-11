# Full HMD Tavi Taxonomy v3 — datatype model redefinition

## Result

`RESULT = CANDIDATE_V3`

v3 redefines the datatype layer while preserving the Full HMD taxonomy structure.

### Changes from the original Full HMD taxonomy

1. `xbrli` namespace is changed from the XML XBRL 2.1 instance namespace to the Tavi/OIM Taxonomy built-in namespace:

```text
https://xbrl.org/2025/instance
```

2. All 353 HMD-derived custom datatype objects are retained.

3. Their XML XBRL 2.1 `*ItemType` base references are replaced as follows:

| XML XBRL 2.1 base | Tavi/OIM Taxonomy base |
|---|---|
| `xbrli:stringItemType` | `xs:string` |
| `xbrli:tokenItemType` | `xs:token` |
| `xbrli:dateTimeItemType` | `xs:dateTime` |
| `xbrli:booleanItemType` | `xs:boolean` |
| `xbrli:monetaryItemType` | `xbrli:monetary` |
| `xbrli:decimalItemType` | `xs:decimal` |
| `xbrli:QNameItemType` | `xs:QName` |
| `xbrli:pureItemType` | `xbrli:pureType` |
| `xbrli:dateItemType` | `xs:date` |
| `xbrli:integerItemType` | `xs:integer` |
| `xbrli:anyURIItemType` | `xs:anyURI` |

4. The 46 `p_*` class-anchor concepts use `xs:string`.

5. The 353 HMD attribute concepts continue to reference their own module-local custom datatype objects. This preserves the HMD/XBRL GL datatype identity instead of flattening every concept directly to an XSD primitive.

## Counts

```text
concepts       = 399
dataTypes      = 353
dimensions     = 44
domains        = 45
cubes          = 46
networks       = 1
tableTemplates = 0
```

## Static validation

- JSON parse: PASS
- OimTaxonomy JSON Schema: PASS
- unresolved concept datatype references (static): 0
- unresolved custom datatype base references (static): 0

Arelle native/full-DTS validation has not been run in the Web environment. Codex must perform one formal local validation against accepted Arelle authority `f8f50ee1d06a12f2e9798437c66e2d360514d6be`.

The previous `ValidateDTS.py:328` `dt.name` NameError occurred on the invalid-baseType diagnostic path. Arelle source should not be modified unless the error remains after v3's datatype references are confirmed valid.
