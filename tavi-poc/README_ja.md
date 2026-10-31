[English](README.md) | **日本語**

# XBRL GL Next — Tavi概念実証

Tavi PWD 2026-09-01を参照した議論用試作。正式適合性は未確認。

## 公開対象

- [Journal Entry JSON](taxonomy/Tavi_JournalEntries_SingleAccount_Date_r2_candidate.json)：唯一のTaviタクソノミ。`xbrlModel.tableTemplates`にTable Templateを内包します。
- [Journal Entry Viewer](https://pontsoleil.github.io/XBRL_GL_Next/tavi-inst-hmd-view.html)：既存UI・タブ・9列CSV転置表示を保った静的表示例です。ソースタブは議論用PWD候補を表示します。

旧Simple、Full v3、4モデル、Arelleパッチおよび旧仕様参照インスタンスは公開から撤回しました。原本と過去の検証証跡はWORKに保全します。共有CSVは保全しますが、CSV単独を完全なxBRL-CSVレポートや検証済みPWDインスタンスとは扱いません。

## 検証の範囲

Viewerは正式なTavi検証器ではありません。JSON構文・静的表示・旧Arelle結果はPWD正式適合性の証拠ではありません。Part 5、HMDと元の意味モデルは変更していません。
