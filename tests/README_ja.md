[English](README.md) | **日本語**
# 第三者向け既存テスト案内

現行の検査入口は`check_generated_package.py`です。実際のCLI・入力契約・依存関係は同スクリプトおよび[英語版案内](README.md)を確認してください。過去の`test_*.py`群はWORKの履歴証跡であり、現行Canonicalには含まれません。新たな共通テスト条件を作らず、必要な入力・依存環境を確認してください。

Taviの4モデル再現は[Tavi再現README](../tavi-poc/README_REPRODUCE_4_MODELS.md)に別途記載します。過去のWORK受入PASSとGitHub cloneでの再現PASSは別です。旧401行HMD用検証器は4モデル共通検証器ではありません。
