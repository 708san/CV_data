# Orange Fruit Image Dataset

バングラデシュで撮影されたオレンジ画像15,000枚、5カテゴリの分類データです。画像上のカテゴリを使った分類の試作や、背景・照明・角度が見分けやすさに与える影響を調べる課題に使えます。

## 使い方

```python
from cvlesson import datasets

data = datasets.get("orange_fruit")
print(data.classes)
print(data.to_df().head())
```

初回取得時に約113 MBをダウンロードします。画像は元の224×224 JPEGの画素を保ち、各クラスをseed 42でtrain/validation/testへ分割しています。

## 利用条件と出典

- ライセンス：CC BY 4.0。出典と変更内容の表示が必要です。
- 出典：Ashif Shuvo, Most.Subrina Afrin Monika, Wahada Jinnat Oishy Bhuian (2026), “Orange Fruit Image Dataset for Classification,” Mendeley Data v2, [DOI: 10.17632/zk4hzhtcdd.2](https://doi.org/10.17632/zk4hzhtcdd.2).
- 公式ページ：[Mendeley Data v2](https://data.mendeley.com/datasets/zk4hzhtcdd/2)
- 整形済み固定版：[orange-fruit-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/orange-fruit-v0.1.0)
- 出典5カテゴリ各3,000枚：黒点、かいよう、fresh、green、rottenの画像カテゴリ。

## 課題上の注意

このデータのラベルは元データに付いた画像カテゴリです。果物の鮮度、食用可否、食品安全、植物病害の診断には使わないでください。バングラデシュで撮影されており、日本で流通するオレンジ全体を代表するものではありません。食品ロスを考える際は、画像だけで食べられるかを決めず、見た目分類の誤りや背景・照明の影響を調べる課題として使います。

## 監査

固定v2のZIPと内側ZIPのSHA-256、CRC、安全パスを確認しました。全15,000枚をデコードし、寸法224×224、完全一致重複0を確認。各クラス1枚を目視しましたが、全画像の目視確認ではありません。[監査レポート](../../reports/orange-fruit-v2-audit.json)
