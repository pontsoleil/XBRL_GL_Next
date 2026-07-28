# XBRL_GL_Next全面改定移行計画

## 1. 目的

旧正式リポジトリを、FSM → Specialization → BSM → Graph Walk → LHM →
OIMタクソノミの再現可能なパイプラインへ全面改定する。旧ファイルの配置又は行数を維持する
ことではなく、意味、来歴、検証可能性及び他プロジェクトからの利用契約を確立する。

## 2. 変更しない基準

```text
正式リポジトリ:
C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next

旧版復元tag:
pre-2026-rearchitecture-20260725

旧版commit:
4172d5f77c61ec7bc3ec7e68d77afb52b752bdbd

復元bundle:
C:\Users\nobuy\GitHub\GIT\XBRL_GL_Next_BACKUP\20260725_4172d5f
```

Phase 1開始までは正式リポジトリのファイル、branch及びremoteを変更しない。

## 3. 提案する改定branch

```text
rearchitecture/oim-taxonomy-2026
```

目的:

- 旧`main`から新アーキテクチャへの変更を隔離する。
- 旧資産の保存、移植及び廃止をcommit単位で追跡する。
- FSMからOIMタクソノミまでの検証が完了するまで`main`を安定状態に保つ。

今回はbranchを作成しない。

## 4. 提案する新構成

```text
XBRL_GL_Next/
├─ AGENTS.md
├─ README.md
├─ LICENSE.md
├─ NOTICE.md
├─ docs/
│  ├─ architecture/
│  ├─ decisions/
│  ├─ migration/
│  └─ legacy/
├─ source/
│  ├─ models/
│  │  ├─ shared/
│  │  ├─ aligned/
│  │  └─ legacy/
│  └─ taxonomies/
│     └─ legacy/
├─ tools/
│  ├─ semantic/
│  ├─ taxonomy/
│  ├─ instance/
│  └─ conversion/
├─ taxonomy/
│  └─ oim/
├─ tests/
│  ├─ unit/
│  ├─ integration/
│  ├─ fixtures/
│  └─ expected/
└─ outputs/
```

`source/`は入力及び来歴資料、`taxonomy/`は正式生成物、`outputs/`は再生成可能な検証出力、
`tests/fixtures/`は固定試験データとして区別する。

## 5. 段階的移行

### Stage 1: ガバナンスと契約

- `AGENTS.md`、README、LICENSE/NOTICE及びディレクトリ責務を確定する。
- Shared、Aligned及びDistinctの定義を正式文書化する。
- ADR-0006承認後、FSM 14列、BSM 15列及びLHM 17列をcanonical semantic
  coreとして版管理する。
- WORK追加項目をprovenance、inheritance、external reference、semantic context及び
  label／presentationのextension又はsidecarへ分離する。
- namespace、URI、2026-12-31の日付及びentry point命名規則を決定する。

合格条件:

- 旧新パス対応、ライセンス例外及び生成物の配置が文書と一致する。
- DNM及び`graphwalk.py -o`を正式設計から除外する。

### Stage 2: 機能単位の統合候補作成

- WORK版、単独4件版及び28件版のprogram、試験、fixture及びSHA-256を版別に固定する。
- いずれか一版を上書き採用せず、header、Specialization、Abstract、module参照、
  Reference、datatype、複数root、element及びsidecarを機能単位で統合する。
- 状況報告上の31件版は一式未回収の過去記録として扱い、探索又は件数再現を行わない。
- `common.utils`に依存しない自己完結した実行環境を定義する。
- CLI contract test、エラー出力及び終了コードを固定する。

合格条件:

- 3版から採用した全機能の試験が成功する。
- 未定義module、未定義associated module、未定義associated class及び異module同名Classを個別に確認できる。
- Association重複の報告とPoC継続、14列／15列／17列、LHM element生成、HMD選択、WORK追加項目sidecar及び
  DNM非サポート方針が試験化される。
- 正式入力を2回処理したBSM/LHMのSHA-256が一致する。

### Stage 3: FSM移行

- Shared FSM 849行及びFSM_btx 180行を正式入力集合として登録する。
- 旧FSM 418行及びJPN 84行との概念対応表を作成する。
- JPN及び公開された地域・国家・業界標準をAligned poolへ分類する。
- 未定義module／associated module／associated class、Abstract Class及びmultiplicity削除指示を検査する。
- 各Classを`(module, class_term)`、Associationを
  `(property_term, associated_module, associated_class)`で事前検証し、
  重複を入力エラーとして報告する。PoCでは重複のないClass及び一意なpropertyを
  継続処理し、曖昧なpropertyを未反映／要確認としてBSMと対になる診断reportへ記録する。

合格条件:

- 旧FSMの全概念に採用、統合、分割、廃止又は保留の判断がある。
- FSM＋FSM_btx → BSMが、clean又は`poc-with-errors`の状態をmanifestへ記録して完了する。
- `poc-with-errors`では、Abstract Class参照、未定義associated module／class及び重複Associationが
  BSMへ暗黙反映されず、診断reportから入力行と処置を追跡できる。

### Stage 4: LHM及び採用判断

- BSMからGraph Walkで候補LHMを生成する。
- root、循環、再帰、Reference、semantic path及びLC3 element命名を検証する。
- `abbreviation_path`及び`xpath`をLHMへ出力しない。
- 自動生成LHMと採用FSM/LHMを区別する。
- 旧BSM/LHMとの差分を正解値照合ではなく設計評価として分類する。

合格条件:

- datatype空欄、semantic path重複及びelement重複が基準内。
- Reference test profileでR/REF出力後の非REF子孫が0。
- 二回生成のSHA-256が一致する。

### Stage 5: OIMタクソノミ生成器

- 旧generatorをschema、concept/type、dimension、hypercube、linkbase、metadata、
  namespace及びentry point単位へ分割する。
- 2025-12-01固定値及び旧module推測を廃止する。
- XBRL International由来資産のライセンス判断を反映する。

合格条件:

- XML Schema validationが成功する。
- XBRL/DTS validationが成功する。
- OIM/xBRL-CSV metadata及び代表instanceが検証に合格する。
- Palette/OIM dual supportのentry pointが明示される。

### Stage 6: instance及び他プロジェクト移行

- 旧23サンプルを権利・個人情報確認後に試験fixture化する。
- fact、aspect、dimension、semantic path及び値を旧新で比較する。
- WORK配下のLHM利用プロジェクトについて対応表を作成する。
- 年次報告書から根拠データへのdrill-down、drill-up及びdrill-throughを試験する。

合格条件:

- 代表業務分野のend-to-end試験が成功する。
- 旧LHM依存箇所の移行又は互換層が明示される。

### Stage 7: 正式化

- README、architecture、decision、manifest、台帳及びSHA-256を同期する。
- 生成物と検証ログを分離する。
- release前チェックを実行し、利用者レビューを受ける。

## 6. 最初のcommit案

最初のcommitには次だけを含める。

- 新しいディレクトリの責務を説明するREADME
- FSM/BSM/LHMの列契約
- Shared/Aligned/Distinct及び生成工程のarchitecture文書
- 370ファイル評価台帳と旧新対応表
- LICENSEを維持し、第三者資産を扱うNOTICEの雛形
- WORK版・4件版・28件版のSHA-256、機能差及び統合条件

最初のcommitには次を含めない。

- 旧taxonomy及びinstanceの実ファイル
- 正式FSM、BSM、LHMの置換
- 候補プログラムの実装
- 自動生成taxonomy
- ライセンス未確認のXBRL International由来ファイル
- 旧出力に一致させる例外処理

## 7. commit分割案

1. `docs: define rearchitecture contracts and migration inventory`
2. `test: establish semantic functional regression baseline`
3. `feat: add normalized FSM to BSM specialization pipeline`
4. `feat: add module-aware BSM to LHM graph walk`
5. `data: add reviewed Shared and Aligned FSM sources`
6. `feat: generate OIM taxonomy from approved LHM`
7. `test: add XML Schema, XBRL, OIM and instance validation`
8. `docs: finalize user guide, provenance and notices`

各commitは独立して試験可能にし、プログラム、入力、生成物及び文書を無関係に混在させない。

## 8. 旧構成の残し方

- Git tag及びbundleを完全な復元手段とする。
- 新branch内では、必要な旧文書及びモデルだけを`docs/legacy`又は`source/.../legacy`へ
  来歴付きで配置する。
- 旧BSM/LHMは`tests/fixtures/legacy`に置き、期待値とは明記しない。
- 大量の旧taxonomyはライセンス判断後に同梱、外部参照又は除外を決定する。
- 同じファイルを旧パスと新パスへ無期限に二重管理しない。

## 9. rollback

branch作業中:

```text
mainへ戻る。改定branchをmergeしない。
```

merge後に問題が判明した場合:

```text
改定mergeをrevertし、pre-2026-rearchitecture-20260725と差分確認する。
```

ローカルリポジトリを失った場合:

```text
XBRL_GL_Next_4172d5f.bundleからcloneし、
pre-2026-rearchitecture-20260725をcheckoutする。
```

ソースZIPはファイル比較用であり、完全復元にはbundleを使用する。

## 10. Phase 1開始前の承認事項

1. branch名`rearchitecture/oim-taxonomy-2026`
2. 新ディレクトリ構成
3. FSM/BSM/LHM列契約
4. 14列FSM／15列BSM／17列LHM契約、HMD選択及びWORK追加項目sidecar schemaの実装順序
5. extension及び複数rootの正式CLI範囲
6. XBRL International由来資産のライセンス方針
7. 旧instanceの公開可否
8. 最初のcommit対象及び除外対象
