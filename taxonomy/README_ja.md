# XBRL GL Next Canonical WORK タクソノミ

有効なタクソノミは、独立生成した次の2つのDTSです。

- `accounting-entries/`（58ファイル）
- `business-transactions/`（67ファイル）

各プロジェクトmoduleのnamespaceは `https://www.xbrl.or.jp/taxonomy/xbrl-gl-next/{module}` に完全一致します。`2026-12-31` は予定版を示すファイル名に残し、namespace URIには含めません。現在のプロジェクト公開・namespace判断は `PROJECT_PUBLICATION_AND_NAMESPACE_DECISION.md` に記録しています。同記録は、判断者のプロジェクト上の役割を明示しますが、別途の理事会決議、ドメイン管理者による技術的委任、公式タクソノミ指定又は外部機関のendorsementを主張しません。

Accounting EntriesとBusiness Transactionsは、異なるルートHMDから階層展開されるためsplit構成を維持します。共有global declarationのうち14件には、ルートHMD別の型・構造・多重度の差異があります。これは各DTS固有の受入済み特性であり、競合又は不具合とは判定しません。利用側はAE又はBTに対応するTuple／OIM entry pointを選択し、同名ファイルの相互上書きや設計なしのDTS混載を行わないでください。単一DTSとしての統合利用は受入範囲外です。

旧root単一ツリーは `../archive/taxonomy/legacy-single-tree-20260915_1406/` に退避し、有効な `taxonomy/**` の外に保持しています。

生成証跡とSHA-256 manifestは `provenance/`、検証証跡は `C:\Users\nobuy\GitHub\WORK\XBRL-GL-Next\docs\Codex\2026\202609\20260915\20260915_1406\stable-namespace-work-unification\outputs` にあります。

XBRL GLの出典、著作権、ライセンス条件、帰属表示及び非endorsement表示は `NOTICE_XBRL_GL.md` に記録しています。その他の第三者由来資料には、それぞれの条件が引き続き適用されます。
