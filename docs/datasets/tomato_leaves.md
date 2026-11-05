# トマトの葉の画像

5種類の状態のトマトの葉、計7,209枚。葉の状態を画像から分類する学習に使います。学習用5,768枚、テスト用1,441枚に分かれています。

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

data = datasets.get("tomato_leaves")
print(data.labels_csv)
print(data.train_dir)
print(data.test_dir)
```

画像は`images/train/<ラベル>/`と`images/test/<ラベル>/`に格納されています。ラベルは`labels.csv`の`image,label,split`で確認できます。元の画像サイズは統一していません。モデルを学習するときは画像サイズなどを揃えます。

## 出典と利用条件

- 元データ：Pandianj, Arun; Geetharamanigopal (2019), *Data for: Identification of Plant Leaf Diseases Using a 9-layer Deep Convolutional Neural Network*, [Mendeley Data v1](https://doi.org/10.17632/tywbtsjrjv.1)
- 元データの公開ライセンス：CC0 1.0（元配布元の記載）
- 教材用に5クラスを抽出、完全一致重複を除き分割したもの： [CV_sample_data](https://github.com/708san/CV_sample_data/tree/main/cases/tomato-leaves)
- 利用する固定版：[tomato-v1.2.0](https://github.com/708san/CV_sample_data/releases/tag/tomato-v1.2.0)

葉の撮影条件や背景が違うと結果が変わることがあります。**画像の判定は植物の病気の確定診断ではありません。**

## 画像とラベルの検査

固定Releaseから取得した7,209枚を検査するには、開発用の `python -m cvlesson.audit tomato_leaves --check-images --report report.json` を使います。Pillowが必要です。初回のZIP取得は約124 MBです。
