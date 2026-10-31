[English](README.md) | **日本語**
# XBRL GL Next

XBRL GL Nextは、共通意味モデル（COR／BTX／AAAという絵具箱）から目的別HMDパレットを構成し、Tuple／OIM／Taviなどで表現する取組です。共同レビュー用資料であり、規格としての正式な承認を示すものではありません。

## プロジェクトの段階と公開状態

本リポジトリは共同レビュー用であり、標準団体の公式公開版・承認済み標準を主張しません。プロジェクトのPhaseとTavi PoCのPhaseは別の区分です。

- **Phase 1 — 再現可能なサンプルパッケージ：** Requirements、Part 1–4、意味モデル、Tuple/OIMサンプル、当時のツール・テストを対象とする共同レビュー用パッケージ。後のPart 5やTavi PoCを当時の受入範囲へ遡及的に追加しません。
- **Phase 2 — 外部共同レビュー：** 意味モデル、Specialisation、Graph Walk、拡張とTuple/OIM bindingなどを議論します。
- **Phase 3 — 公開候補：** レビューを反映してバージョン、名前空間、ライセンスと公開構成を整備します。
- **Phase 4 — 正式公開と維持管理：** 正式な公開と、以後の更新・拡張・保守を対象とします。

第三者ライセンス等は[日本語の注意事項](THIRD_PARTY_NOTICES_ja.md)、Framework概要は[日本語の案内](TaxonomyFramework/README_ja.md)を参照してください（参照先のWORK／公開登録状況は別途確認）。

## 仕様と処理工程

[Taxonomy Framework](TaxonomyFramework/README.md)（現状維持）を参照してください。Part 1は共通意味モデルとHMD、Part 2はTuple、Part 3はOIM、Part 4はAligned extensionを扱います。CORとBTXはShared、COR-JPNはCORクラスのSpecialisation、BTX-PINTはBTXクラスのSpecialisationによるAligned extensionです。

**FSM → Specialisation／BSM → Graph Walk → Candidate LHM → Reviewed LHM → Post-Graph Walk → Formal HMD → Taxonomy**。Journal Entry Tavi議論用候補は独立したHMD Viewを対象とします。

## ディレクトリ案内

- [semantic-model/](semantic-model/README.md)：FSM、BSM、Reviewed LHM、HMDと意味モデルのauthority
- [taxonomy/](taxonomy/README.md)：Tuple／OIMの独立DTSとTavi候補
- [ids/](ids/README.md)：**Instance Documents（インスタンス文書）**の略。識別子のディレクトリではありません。`ids/tuple/`はXML、`ids/oim/`はCSVとJSONメタデータの組で、JSONがレポートの入口です。
- [tavi-poc/](tavi-poc/README.md)：Journal Entry PWD議論用JSONと静的Viewer
- [tools/](tools/README.md)：各スクリプトとFramework Partとの関係
- [tests/](tests/README.md)：第三者による既存テストの再現ガイド
- [definitions/](definitions/README.md)：datatype等の参照定義

## 再現性と公開状態

Tavi PWD 2026-09-01を参照した議論用試作。正式適合性は未確認。 公開するTaviタクソノミは[Journal Entry JSON](tavi-poc/taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json)1件で、Table Templateを内包します。[Journal Entry Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)は静的表示例です。旧モデル・旧メタデータ・パッチの原本と証跡はWORKで保全します。

## Tuple／OIM生成CLI（既存実装）

``text
python tools/taxonomy/xBRLGL_TaxonomyGenerator.py \
  --hmd-dir <HMD_DIRECTORY> \
  --output-dir <TAXONOMY_OUTPUT_DIRECTORY> \
  --namespace <NAMESPACE>
``

`--namespace` は名前空間anchor（例 `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/plt`）です。既存の位置引数および `-b`／`--base-dir` は後方互換の範囲で説明されています。

## 検証baselineの注意

Phase 1のArelle受入baselineは対象入力・エントリーポイント・検証記録の対応を引き続き確認する必要があり、全版共通の単一数値PASSをここでは主張しません。
