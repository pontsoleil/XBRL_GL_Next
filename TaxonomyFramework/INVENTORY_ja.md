[English](INVENTORY.md) | **日本語**

# Phase 1 サンプル・インベントリ

## 状態

- インベントリ確認日: 2026-08-13
- 状態: Phase 1 sample / collaborative review
- Public release 承認: No
- Taxonomy version: 2026-12-31

インベントリ確認日および検証日は、taxonomy の namespace/version `2026-12-31` を変更するものではありません。


## Framework 文書

正式な Framework 文書は英語のみで管理します。このディレクトリにある文書の概要は [README_ja.md](README_ja.md) で日本語案内しています。

| ファイル | SHA-256 |
| --- | --- |
| `XBRL_GL_Next_Requirements_Specification.docx` | `3D2F29ADBA3B715A9BF04C6E180458363D2F1E85DDDF8CFF25E6A0326486FC48` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_1_General_rules.docx` | `B766038A4BAEBD089E38A615AEA133F09B7355A761939FB5AAD81E3D29A04B39` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_2_Tuple_palette_taxonomy.docx` | `24CE142D7992DFD99E1F34A6F1E5560B17D4A364051ED36C9CED0D8BD0A18A3F` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_3_OIM_palette_taxonomy.docx` | `E11C9C6F8355FD2CFA3CA48EC65E29C5374BA05EF32014B74669E2A928136094` |
| `XBRL_GL_Next_Taxonomy_Framework_Part_4_Aligned_pool_for_extension.docx` | `E7ED58A41F636E83C78475D09A4D470179828E367F126A79D61625F040A37C72` |

## セマンティックモデルの入力とパイプライン生成物

```text
semantic-model/FSM.xlsx
  ↓ formal FSM sheets をexport
semantic-model/FSM/FSM.csv
semantic-model/FSM/FSM_btx.csv
  ↓ Specialisation
semantic-model/BSM/BSM.csv
  ↓ Graph Walk
semantic-model/LHM/LHM_candidate.csv
  ↓ 人によるセマンティックレビュー
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv
semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.xlsx
  ↓ Post-Graph Walk
semantic-model/LHM_for_taxonomy/
  XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv
  XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv
  manifest.csv
```

| ファイル | 行数 / 使用範囲 | 列数 | SHA-256 |
| --- | ---: | ---: | --- |
| `semantic-model/FSM.xlsx` | `FSM` A1:O504; `FSM_btx` A1:O506 | 各sheet 15 | `A22F37E69168341F38F77987FD4B0D38BF732527C418A700CE766D45D991F3E2` |
| `semantic-model/FSM/FSM.csv` | 500 | 15 | `836508A329B7FD8D05C267EF9E63329E30947B7AD1DE5BAA885B02202934BCF7` |
| `semantic-model/FSM/FSM_btx.csv` | 77 | 15 | `DAC94254F8C4F5302E5BA7DA89CA7E738BC8642AC0EDBA5E441147B7443DEF82` |
| `semantic-model/BSM/BSM.csv` | 713 | 16 | `6002FE391E96A2323C28635C205C9A7D63B05FD1430A12761D22D30897D169BF` |
| `semantic-model/LHM/LHM_candidate.csv` | 498 | 18 | `8D7BC4F19E3F542055CE52DEFC7735FDEA816F7C033EC125EE0FF0FB7C070006` |
| `semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.csv` | 496 | 18 | `FED2EA0CAF51D6BEC880234A3B1E3B068893A8E5F8957254FAD707950718259F` |
| `semantic-model/LHM/XBRL_GL_Next_LHM_reviewed.xlsx` | 4 sheets: A1:U497, A1:R497, A1:R499, A1:R279 | 21/18/18/18 | `12A17F192D034E6DCBB7D09885880832077ADC5DED78872A87EAA54047A478D3` |
| `semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_AccountingEntries_for_taxonomy.csv` | 220 | 18 | `4E388F7107C6B2CE0C9E911BC672114ABD1E638A2DCA4A264332E281C0440810` |
| `semantic-model/LHM_for_taxonomy/XBRL_GL_Next_HMD_BusinessTransactions_for_taxonomy.csv` | 276 | 18 | `EB3479D5A96175FA9D72265700D8947A05F011292D4C6873A5D06577C971A984` |
| `semantic-model/LHM_for_taxonomy/manifest.csv` | 2 | 12 | `36B4261ED8BABF34E12B6244AE5F3C5C73D719077ABC175172B7821208589661` |

candidate LHM から reviewed LHM への移行は、人によるレビュー工程です。candidate と reviewed の SHA-256 が一致することは想定しておらず、reviewed LHM を自動再生成で上書きしてはいけません。reviewed LHM から root 別 HMD を経て taxonomy を生成する処理は決定論的です。`manifest.csv` は実行・確認用の生成物であり、Taxonomy Generator がモデル内容を決定する入力ではありません。

## 正式な実行ツール

| ファイル | SHA-256 |
| --- | --- |
| `tools/semantic/specialisation.py` | `FAC3F6F526DC752C7A704A26A8EB3C02C7C597C967827044856A4388DC08E5D5` |
| `tools/semantic/graphwalk.py` | `FBF34BDD9B0DFA020B64C712BEECD40417F50CF8F045C7A6D48158C50E970338` |
| `tools/semantic/post_graphwalk.py` | `FF7446A82A2527860245EC738672CFC989409850952C870676F4F1DB56DF7E9E` |
| `tools/semantic/validate_lhm.py` | `22EF2D1C7CE5A3643A23AF11D7D07A01759F14781A8D10BC80E9DD22D892127D` |
| `tools/taxonomy/xBRLGL_TaxonomyGenerator.py` | `205FD43B730993C573ED55228FA4E01BE490A17CC1177EACDD9A995E2AA05447` |

## 正式なテスト

| ファイル | SHA-256 |
| --- | --- |
| `tests/test_specialisation.py` | `BF28FDD2FBB944B78B2F9B72C1B966AC5F00D65627BB6F0F093B57787F77E4CA` |
| `tests/test_graphwalk.py` | `64F3D9469A6CD3CCF668BE27396DB922619CB6CE86FFC5E79E71F0BE92789D91` |
| `tests/test_semantic_pipeline.py` | `1197DDFCBDBE724CD20704337C2281509887B1D535E0C86AE6F2ED7C5B097C9C` |
| `tests/test_v5_taxonomy_generator.py` | `89D4CA7F06CBDC5F102CF92361E88C96E534F028DEEC677F44E461FA900C52E8` |
| `tests/check_generated_package.py` | `8E6E8E6D762339AFCA2BF3C9168761A3B19C163A15C62024EFEB90A4D960ADBA` |

## 生成済みサンプル taxonomy

`taxonomy/` は、正式 HMD から生成した 56 ファイルのサンプル taxonomy package です。Tuple 2件、OIM 2件の entry point を含みます。

- `taxonomy/tuple/cor_accountingEntries/cor-all-2026-12-31.xsd`
- `taxonomy/tuple/btx_businessTransactions/btx-all-2026-12-31.xsd`
- `taxonomy/oim/cor_accountingEntries/cor-all-oim-2026-12-31.xsd`
- `taxonomy/oim/btx_businessTransactions/btx-all-oim-2026-12-31.xsd`

`taxonomy/README.md` や `taxonomy/README_ja.md` のような repository の説明文書は生成された taxonomy の構成ファイルではなく、formal taxonomy の 56 ファイルには含めません。

## サンプル instance

`ids/` には次のサンプル instance が格納されています。

- `ids/tuple/accountingEntries-journalEntry.xml`
- `ids/tuple/businessTransactions-vendorInvoice.xml`
- `ids/oim/accountingEntries-journalEntry.json`
- `ids/oim/accountingEntries-journalEntry.csv`
- `ids/oim/businessTransactions-vendorInvoice.json`
- `ids/oim/businessTransactions-vendorInvoice.csv`

OIM の JSON metadata file が xBRL-CSV の entry point です。

## 検証基準

- Pytest, WORK: 142 passed, 61 subtests passed, failures 0, errors 0。
- Pytest, curated GIT suite: 63 passed, 48 subtests passed, failures 0, errors 0。WORK には curated GIT 登録対象外の追加テストがあるため、件数差はfailureではありません。
- Package checker: formal taxonomy files 56; local references 3,821; unresolved local files 0; unresolved local fragments 0; dimensional locators 850; failures 0。
- Arelle 2.44.1 taxonomy entry points: 4/4, errors 0, warnings 0。
- Arelle 2.44.1 sample instance entry points: 4/4, errors 0, warnings 0。
- XMLSpy GUI: Tuple/OIM DTS は 2026-08-12 に手動確認済み。taxonomy content は変更していないため、GUI での再検証は不要です。
