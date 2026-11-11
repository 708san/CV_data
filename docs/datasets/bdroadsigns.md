# BDRoadSigns

バングラデシュで撮影された道路標識18種類の画像分類データです。標識の見分けやすさを調べるクイズや、案内表示の伝わりやすさを考える試作に使えます。

## 使い方

```python
from cvlesson import datasets

data = datasets.get("bdroadsigns")
print(data.classes)
print(data.to_df().head())
```

初回取得時に約191 MBをダウンロードします。データは`Compress Dataset`の5,136枚で、画像の画素は変更せず、クラスごとにseed 42でtrain/validation/testへ分割しています。

## 利用条件と出典

- ライセンス：CC BY 4.0。出典表示と変更内容の表示が必要です。
- 出典：Tawhid Ahmed Komol, Pulak Deb Nath, Rinvi Jaman Riti, “BDRoadSigns: An Image-Based Dataset of Bangladeshi Traffic Signs for Supervised Classification Models,” Mendeley Data v1, [DOI: 10.17632/rnkd74xdtr.1](https://doi.org/10.17632/rnkd74xdtr.1).
- 公式配布ページ：[Mendeley Data v1](https://data.mendeley.com/datasets/rnkd74xdtr/1)
- 整形済み固定版：[bdroadsigns-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/bdroadsigns-v0.1.0)
- 元画像5,136枚は480×640です。分類クラスの合計は公式ページの記載5,135枚と1枚異なり、Compress DatasetのRoundAboutが284枚（ページ記載283枚）です。監査では収録分を保持し、この差を記録しました。

## 課題上の注意

バングラデシュの道路標識と撮影環境を使った学習用データです。日本の交通規則と同じ意味を示すとは限らず、運転・通学路の安全判断や実際の案内には使わないでください。背景の道路風景も写ります。標識以外の要素が認識結果に影響するかを調べる題材にもできます。

## 監査

全5,136画像の形式・寸法・デコードと重複を確認し、18クラスから1枚ずつ目視しました。代表画像では標識とクラスの対応を確認しましたが、全画像を目視したわけではありません。監査内容は[JSONレポート](../../reports/bdroadsigns-v1-audit.json)にあります。
