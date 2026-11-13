# LeFood-Set：食べ残しを画像と計測値で調べる

## 出典と利用条件

- 固定版：[Mendeley Data v1](https://data.mendeley.com/datasets/cchsk79jkt/1)、DOI `10.17632/cchsk79jkt.1`
- 論文：[Sari, Nakazawa & Wani (2025), PLOS ONE](https://doi.org/10.1371/journal.pone.0320426)
- artifact Release：[lefood-set-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/lefood-set-v0.1.0)
- ライセンス：CC BY 4.0。出典・ライセンス・変更内容を表示してください。
- ZIP：53,035,809 bytes、SHA-256 `ca1846273d0636ea59f387a586c6f004cfc02d58a639ad5a3c7c844b66cb863a`

## データでできること・使用例

食前・食後画像、実測重量差、7段階の見た目評価の関係を調べられます。残量の見積もりや食事記録などは使用例です。画像から重量を確定するデータではなく、測定値との比較に使います。

データはインドネシアの病院食研究に由来し、日本の学校給食を代表しません。画像だけで食べ残し重量を確定せず、実測と比べてください。健康、栄養、患者個人の判断や医療用途には使いません。

## 内容

524組、1,048枚の食前・食後JPEGと34料理カテゴリを収録します。表には食前・食後重量、重量差、残量比、観察者評価、pair単位のtrain/validation/test分割があります。食前・食後の組が欠けていた154行を除きました。食後重量が増えていた10組は値を直さず、`weight_order_anomaly`で示します。

全画像をデコードし、全524組のコンタクトシートを目視しました。人物・顔・個人識別情報は見つからず、GPS/EXIFメタデータはありません。元画像の画素データは変更していません。

## ライブラリから取得

```python
from cvlesson import datasets

data = datasets.get("lefood_set")
frame = data.to_df()
print(frame[["food_category", "weight_before_g", "weight_after_g", "leftover_ratio"]].head())
data.show_examples(6, split="train")
```

ダウンロードは約53 MBです。取得時に固定ReleaseのサイズとSHA-256を照合します。画像と表はリポジトリ外のキャッシュに保存されます。`to_df()`の1行は1組を表し、`image_before_path`と`image_after_path`に画像の場所が入ります。

## 帰属表示と変更

出典：Sari, Yuita Arum; Wani, Yudi Arimba; Nakazawa, Atsushi (2025), “LeFood-Set: Leftovers Food Dataset,” Mendeley Data v1, DOI: 10.17632/cchsk79jkt.1. CC BY 4.0.

変更：画像が揃う524組を選び、ファイル名を整理。食前・食後重量差と残量比、pair単位のデータ分割を追加しました。画像画素は変更していません。画像欠落154行を除外し、重量順が逆の10組は注記を付けて残しました。
