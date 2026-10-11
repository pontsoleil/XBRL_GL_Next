# Expected Structured Tidy Data

24 native facts reconstruct as two Header rows and four Detail rows: six Structured Tidy rows in total, with nine columns ordered by the Table Template.

```csv
dHeader,dDetail,entryNumber,entryDate,drCrIndicator,accountCode,accountName,amount,description
1,,JE001,2026-10-10,,,,,
1,1,,,Dr,100,Cash,1000,Receipt
1,2,,,Cr,400,Sales,1000,Sale
2,,JE002,2026-10-10,,,,,
2,1,,,Dr,120,AccountsReceivable,2000,Invoice
2,2,,,Cr,400,Sales,2000,Sale
```

Header row identity is cube name + dHeader, using cor:entryHeaderCube. Detail row identity is cube name + dHeader + dDetail, using cor:entryDetailCube. Header and Detail share the same dHeader value.

The view uses loaded native facts and their dimensions and concepts. It does not reread the source CSV, use fact IDs as row identity, or use tableId as semantic identity. It does not introduce headerRef, targetRef or concept-refDimension.

An amount cell maps to its native XbrlFact. The amount facts retain JPY units and decimals=0; selecting the cell links the native fact to the Properties pane.
