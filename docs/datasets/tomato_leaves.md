# トマトの葉の画像

5種類の状態のトマトの葉、計7,209枚。葉の状態を画像から分類する学習に使います。元のReleaseは学習用5,768枚、テスト用1,441枚です。標準化後は公式testを保持し、trainから検証用577枚を分け、train 5,191枚・val 577枚・test 1,441枚として扱います。

| 元のラベル | 日本語 |
| --- | --- |
| `early_blight` | 輪紋病（元配布READMEの表記：早期疫病） |
| `healthy` | 健全 |
| `late_blight` | 疫病 |
| `septoria_leaf_spot` | 白星病（元配布READMEの表記：セプトリア葉斑病） |
| `leaf_mold` | 葉かび病 |

## 取得して調べる

```python
from cvlesson import datasets

data = datasets.get("トマトの葉")
df = data.to_df()  # pip install -e '.[dataframe]'
print(df.head())
print(df["label_ja"].value_counts())
train_data = data.to_torch_dataset(split="train", image_size=(64, 64))  # pip install -e '.[torch]'
```

画像は`images/train/<ラベル>/`と`images/test/<ラベル>/`に格納されています。ラベルは`labels.csv`の`image,label,split`で確認できます。元の画像サイズは統一していません。モデルを学習するときは画像サイズなどを揃えます。

元のReleaseに検証用分割がないため、DataFrameとPyTorch Datasetでは公式testをそのまま保持し、trainの各クラスからseed `42`で10%を`val`に分けます。`data.splits`で件数を確認できます。個体や連続撮影のグループ情報は元データにないため、グループ単位の漏洩防止は保証していません。

## 出典と利用条件

- 元データ：Pandianj, Arun; Geetharamanigopal (2019), *Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network*, [Mendeley Data v1](https://doi.org/10.17632/tywbtsjrjv.1)
- 元データの公開ライセンス：CC0 1.0（元配布元の記載）
- 教材用に5クラスを抽出、完全一致重複を除き分割したもの： [CV_sample_data](https://github.com/708san/CV_sample_data/tree/main/cases/tomato-leaves)
- 利用する固定版：[tomato-v1.2.0](https://github.com/708san/CV_sample_data/releases/tag/tomato-v1.2.0)

2026-11-05に、公式MendeleyページのCC0 1.0表記とCC0の利用条件を確認しました。CC0は法の許す範囲で複製・改変・再配布を認めますが、肖像・プライバシー・特許・商標など別の権利まで自動的に消すものではありません。そのため、artifactには出典と派生処理を残し、医学的な診断用途や権利の無制限な保証はしません。

葉の撮影条件や背景が違うと結果が変わることがあります。**画像の判定は植物の病気の確定診断ではありません。**

## 画像とラベルの検査

固定Releaseから取得した7,209枚は2026-11-05に全量検査済みです。破損0枚、完全一致重複候補0件、ラベル不一致0件でした。8×8平均ハッシュでは類似候補14,571組が見つかりましたが、これはレビュー用候補であり、自動削除や重複確定はしていません。同一個体・撮影系列の分離と権利審査は未実施です。[監査レポート](../../reports/tomato-leaves-v1.2.0.json)

再検査には開発用の `python -m cvlesson.audit tomato_leaves --check-images --report report.json` を使います。Pillowが必要です。初回のZIP取得は約124 MBです。
