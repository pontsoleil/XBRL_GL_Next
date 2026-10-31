[English](README.md) | **日本語**
# ツールとFrameworkとの対応

実装は仕様の一部の工程を実現するもので、Part全条項の適合を保証するものではありません。

- Part 1／4：`semantic/specialisation.py` はSharedクラスのAligned extensionへのSpecialisation、Part 1の`graphwalk.py`はBSM→Candidate LHM、`post_graphwalk.py`はReviewed LHM→Formal HMD。
- Part 1／2／3：`taxonomy/xBRLGL_TaxonomyGenerator.py` はHMDからTuple／OIM DTSを生成。`datatype_binding.py`等は対応するBindingを実装。
- Part 2／3：`instance/instance_core.py`と`structured_oim.py`は受入済みView等に基づくインスタンス処理（対応範囲は各仕様で確認）。

[英語版の一覧表](README.md)と[Journal Entry議論用候補](../tavi-poc/README_ja.md)を参照してください。旧4モデル生成器は公開から撤回しました。
