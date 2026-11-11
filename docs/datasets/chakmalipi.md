# ChakmaLipī（チャクマ文字）

## どんな課題に使える？

チャクマ文字と数字の手書き画像を48種類に分類するデータです。文字を画像として残し、コンピューターで見分けるにはどんな記録が必要かを考える課題に使えます。日本語のくずし字を含むデータではありません。

このデータは文字を一つずつ切り出した画像です。ページ全体から文章を読み取るOCRの性能は調べられません。また、書き手ごとのIDがないため、初めて見る人の文字でも正しく分類できるかを評価する用途には向きません。チャクマの人々や言語について、このデータだけから一般化しないでください。

## データの内容

- 48クラス（文字38種類、数字10種類）、36,258枚
- 40×40画素のRGB PNG
- train 25,348枚、validation 5,426枚、test 5,484枚
- 元データの37,708枚を全量デコードし、完全一致重複1,450枚を除外
- 重複除外後、seed 42で各クラスをおよそ70/15/15に分割
- 同じ書き手が複数の分割に含まれる可能性があります

## 取得

固定Release assetの公開後に、次の方法で取得できます。

```python
from cvlesson import datasets

data = datasets.get("chakmalipi")
print(data.classes)
print(data.class_names_ja)
print(data.splits)
data.show_examples(8)
```

ダウンロードは約95MBです。データはリポジトリの外にあるキャッシュへ保存されます。

## 出典とライセンス

Jannatul Ferdeous; Md. Abdul Kayum; Ahmed Islam; Md Roman Nihal; ASM Shihavuddin; Muhammad Hasan (2026), “ChakmaLipī Dataset,” Mendeley Data v6, DOI: [10.17632/rzjphbvz9f.6](https://doi.org/10.17632/rzjphbvz9f.6).

配布元はCC BY 4.0を表示しています。作者・出典・変更内容を表示してください。関連論文は、参加者から同意を得て倫理審査を受けたことを説明しています。配布物は画素値を変えず、完全一致重複を除いて分割しています。

元画像全件をデコードし、全48クラスから各4枚の見本を確認しました。これは全画像の人手確認ではありません。書き手IDが公開されていないため、書き手単位で分離した評価はできません。詳細は[監査レポート](https://github.com/708san/CV_data_artifacts/blob/main/reports/chakmalipi-v0.1.0-audit.json)を参照してください。

Release assetは準備中です。公開されるまではライブラリから取得できません。
