# RDD2020 Japan：道路のひび・穴を見つける

## 出典と利用条件

- 固定版：[Mendeley Data v2](https://data.mendeley.com/datasets/5ty2wb6gvg/2)、DOI `10.17632/5ty2wb6gvg.2`
- データ論文：[RDD2020: An Image Dataset for Smartphone-based Road Damage Detection and Classification](https://doi.org/10.1016/j.dib.2021.107133)
- artifact Release：[rdd2020-japan-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/rdd2020-japan-v0.1.0)
- ライセンス：CC BY-NC 3.0。非商用の教育目的に限って利用できます。出典・変更内容を表示してください。商用利用はできません。
- ZIP：641,514,873 bytes、SHA-256 `f787feead7fd3b0d63f42c7cfb8e3db6f114e57c83b3b928d5f7c58bcb411955`

## 高校生が取り組める課題

通学路や地域道路にひびや穴がないか画像から探し、画像を根拠に道路管理者へ相談する資料を作る題材です。検出結果を画像と見比べ、見落としや誤検出も確認します。

画像は2020年頃に日本で車載スマートフォンを使って撮影されたものです。今の道路状態や自分の地域の代表例ではありません。モデルの結果だけで道路の安全性や修繕順位を決めず、現地確認や管理者の情報と照らし合わせてください。

## 内容と整形

固定版の日本train 10,506画像・XMLを検査しました。画像はすべてデコードでき、XMLとの寸法不一致、完全一致画像重複、GPSメタデータはありません。全XMLの注釈を読み、データ論文が扱う道路損傷4クラスだけを残しました。

| クラス | 説明 | bbox数 |
| --- | --- | ---: |
| D00 | 縦ひび | 4,049 |
| D10 | 横ひび | 3,979 |
| D20 | 亀甲ひび | 6,198 |
| D40 | ポットホール | 2,243 |

対象クラスのない画像2,606枚と幅0のbbox 1個を除外し、7,900画像・16,469 bboxにしました。画像画素は変更せず、Pascal VOC座標を正規化YOLO形式へ変換しています。train 6,299、valid 802、test 799に画像単位で分けました。

公開元は、明瞭な顔やナンバープレートをぼかしたと説明しています。こちらでは36枚の標本を目視し、明瞭な個人識別情報は確認されませんでした。全画像を個別に目視したわけではありません。人物、車、住所を特定する目的では使わないでください。

## ライブラリから取得

```python
from cvlesson import datasets

data = datasets.get("rdd2020_japan")
print(data.splits)
data.show_examples(9, split="train")
```

ダウンロードは約642 MB、展開後のキャッシュは約646 MBです。取得時に固定ReleaseのサイズとSHA-256を照合します。画像・ラベルはリポジトリ外のキャッシュに保存されます。

`data.to_df()`は画像パス、ラベルファイル、bbox、splitを含む表を返します。bboxの数値は画像の幅・高さで0〜1に正規化されています。クラスIDの順は`D00`, `D10`, `D20`, `D40`です。

## 帰属表示と変更

出典：Deeksha Arya, Hiroya Maeda, Sanjay Kumar Ghosh, Durga Toshniwal, Hiroshi Omata, Takehiro Kashiyama, Toshikazu Seto, Alexander Mraz, Yoshihide Sekimoto (2021), “RDD2020: An Image Dataset for Smartphone-based Road Damage Detection and Classification,” Mendeley Data v2, DOI: 10.17632/5ty2wb6gvg.2. CC BY-NC 3.0.

変更：日本trainから対象4クラスを選び、対象外画像と幅0 bboxを除外。VOC bboxを正規化YOLO形式に変換し、train/valid/testへ分割しました。画像画素は変更していません。
