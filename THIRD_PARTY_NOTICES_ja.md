[English](THIRD_PARTY_NOTICES.md) | **日本語**

# 第三者資料及びライセンスreview

このプロジェクトは、project-authored成果物と、来歴の異なる過去資料及び外部資料を
組み合わせます。技術的妥当性は、著作権、再配布許可、endorsement又は公開権限を
示すものではありません。

## Project licenseの境界

repository licenseは次のように解釈します。

- MITは、MIT表示を持つ、又は著作者とMIT適用が明示的に確認されたproject-authored
  scriptだけに適用します。
- CC BY 4.0は、識別済みのproject-authored documentation及びartifactだけに適用します。
- いずれのlicenseも、外部原本、標準、taxonomy、code list、consumer data又は
  derivative workへ適用される条件を変更しません。
- ownership、license、confidentiality、privacy又は再配布条件が未解決のfileは、
  Private repositoryにも登録しません。

repositoryへの配置、技術的変更又は生成artifactへの包含により、第三者資料が
project-authored成果物へ変わることはありません。

## XBRL Global Ledger 2015

- Owner: XBRL International
- Status: Recommendation
- Release date: 2015-03-25
- Official package:
  <https://www.xbrl.org/int/gl/2015-03-25/XBRL-GL-REC-2015-03-25.zip>
- SHA-256:
  `AFCAEE16683E1D1348E0BBE91D1928EC5EF2265BEA8590238F86D52E9F12B931`
- Licence statement:
  <https://www.xbrl.org/int/gl/2015-03-25/gl-framework-REC-2015-03-25.html#copyright>

## XBRL Global Ledger 2017

- Owner: XBRL International
- Status: Public Working Draft
- Work product name: XBRL Global Ledger 2017
- Release and namespace date: 2016-12-01
- Official package:
  <https://www.xbrl.org/int/gl/2016-12-01/XBRL-GL-PWD-2016-12-01.zip>
- SHA-256:
  `0C48AA0EA8F6963CA5A3625AD32ADA6AEE5B3A164438A155A0C9937CCFFECE67`
- Licence statement:
  <https://www.xbrl.org/int/gl/2016-12-01/gl-framework-2017-PWD-2016-12-01.html#copyright>

各用途について、リンク先の条件をreviewする必要があります。過去及びWORKのprototype
には、改変したXBRL-GL由来内容と`xbrl.org` namespaceを使用するものがあります。
これらは本登録候補に含まれず、project licenseによるPrivate又はpublic登録許可も
確認されていません。

公式ZIPはcommitしません。再利用するrelease packageは公式entry pointをimportするか、
独立管理conceptにproject-owned namespaceを使用します。

## UN/CEFACT資料

WORKの分析資料には、UN/CEFACT CCL D25A、UNTDED、UNTDID又はcode list由来の
内容があります。対応する`source/unece/`及びtaxonomy experiment構造は、現在の
target Private repositoryへ登録されていません。無償利用できることを、無制限の
再配布又は派生物公開許可とは扱いません。

- UN/CEFACT standards: <https://unece.org/trade/uncefact/standards>
- UN/CEFACT call to action:
  <https://unece.org/trade/uncefact/CallToAction-Digitalization>
- United Nations terms of use:
  <https://www.un.org/en/about-us/terms-of-use>

コピーしたD25A分析データについて書面による再配布許可は記録されていないため、
Private repository外に置きます。将来の利用には、公式download recipe、source固有の
permissive license又は書面許可が必要です。mappingではUN unique ID及びrelease
provenanceを保持します。

## Python tool

target repositoryには過去scriptがあり、WORKには新しい候補があります。明示MIT表示を
持つ、又はproject authorshipが別途確認されたscriptだけをMIT対象候補とします。
表示を保持し、sourceの完全なSHA-256を記録します。著作者とlicenseが未確認のscriptは
Private登録対象にしません。

## Project文書及びreview evidence

改訂Framework DOCX及び`docs/ChatGPT` review evidenceはWORKにありますが、この候補
には登録しません。保有又はrepository所有は公開権限の証拠ではありません。Private
登録前にも、project authorship及び共有範囲の明示判断が必要です。

## Release規則

コピー前にfileをproject-authored、external original、derivative、generated output、
consumer data又はreview evidenceへ分類します。source、version、SHA-256、適用条件、
データ機密性及び承認済み共有範囲を記録します。生成Phase 0 manifestは計画中の
evidenceであり、この候補には登録しません。

README linkを修復するためだけに保留fileを登録してはなりません。このnoticeは来歴・
公開管理記録であり、法律意見ではありません。
