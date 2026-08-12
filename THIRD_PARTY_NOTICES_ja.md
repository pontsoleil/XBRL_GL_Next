[English](THIRD_PARTY_NOTICES.md) | **日本語**

# 第三者資料及びライセンスreview

このprojectは、project-authored成果物と来歴の異なる過去資料・外部資料を扱います。技術的妥当性は、著作権、再配布許可、endorsement又は公開権限を示しません。このnoticeは来歴・公開管理記録であり、法律意見ではありません。

## Project licenseの境界

- MITは、MIT表示を持つ、又は著作者とMIT適用が明示的に確認されたproject-authored scriptだけに適用します。
- CC BY 4.0は、識別済みのproject-authored documentation及びartifactだけに適用します。
- いずれのlicenseも、外部原本、標準、taxonomy、code list、consumer data又はderivative workの条件を変更しません。
- repositoryへの配置、技術的変更又は生成artifactへの包含により、第三者資料がproject-authored成果物へ変わることはありません。

保持するPython toolはproject-authored formal toolです。そのnotice及び正確なSHA-256は`TaxonomyFramework/INVENTORY.md`に記録します。

## XBRL Global Ledger 2015及び2017

XBRL GL 2015 Recommendation及びXBRL GL 2017 Public Working DraftはXBRL Internationalの外部資料です。公式packageは本repositoryへcopyしていません。

- 2015 official package: <https://www.xbrl.org/int/gl/2015-03-25/XBRL-GL-REC-2015-03-25.zip>
- 2015 licence statement: <https://www.xbrl.org/int/gl/2015-03-25/gl-framework-REC-2015-03-25.html#copyright>
- 2017 official package: <https://www.xbrl.org/int/gl/2016-12-01/XBRL-GL-PWD-2016-12-01.zip>
- 2017 licence statement: <https://www.xbrl.org/int/gl/2016-12-01/gl-framework-2017-PWD-2016-12-01.html#copyright>

用途ごとにリンク先条件をreviewする必要があります。必要に応じて公式entry pointをimportするか、独立管理conceptにはproject-owned namespaceを使用します。

## UN/CEFACT資料

UN/CEFACT標準及びsource分析は過去のproject作業で参照しましたが、UN/CEFACT原資料は今回のPhase 1 sample packageに含めません。一般利用可能であることを、原本又は派生物の無制限な再配布許可とは扱いません。

- UN/CEFACT standards: <https://unece.org/trade/uncefact/standards>
- United Nations terms of use: <https://www.un.org/en/about-us/terms-of-use>

将来の再利用ではsource/releaseの来歴を保持し、適用条件又は許可を確認します。

## Project文書及び台帳

Framework DOCX 5件は、現在のcollaborative-review文書として`TaxonomyFramework/`へ登録済みです。登録又は保有だけでpublic-release承認を意味しません。

Phase 0 inventory/manifest、historical script及びworking materialはcurated packageから削除済みです。現在のPhase 1成果物台帳は`TaxonomyFramework/INVENTORY.md`です。

## Release規則

公開又は再配布前に各artifactをproject-authored、external original、derivative、generated output、consumer data又はreview evidenceへ分類し、source、version、SHA-256、適用条件、data sensitivity及び承認済みsharing scopeを記録します。
