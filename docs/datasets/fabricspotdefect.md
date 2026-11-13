# FabricSpotDefect（衣類の汚れの位置）

## データでできること・使用例

布画像のspot（汚れ・変色など）の位置を検出し、柄・色・撮影条件による違いを比べられます。洗濯前の確認や布画像の整理などは使用例です。画像中の位置を示す物体検出を試せます。

このデータは「spot」の位置を一つの種類として示します。衣類の清潔さ、着用可否、安全性、汚れが落ちたかどうか、布の品質を判定するものではありません。バングラデシュの家庭で撮影された画像で、日本の衣類全般を代表するわけではありません。

## 収録内容

- 元画像1,014枚（train 643 / validation 219 / test 152）
- spot注釈3,288件、1クラス
- 元画像の画素と寸法を保持。COCOの矩形を共通の正規化中心座標に変換
- 増強画像は含めない
- Mendeley掲載説明は元画像の注釈を3,286件と記載していますが、アーカイブおよび論文は3,288件です。この配布版はアーカイブの注釈を使用します。
- Mendeley v1 ZIP SHA-256：`2e4fd58488734fe3b888c0c3633ca4d68da76f3a96f1e9bba08ec710645d6ab2`
- 共通artifact ZIP：744,311,786 bytes、SHA-256 `b40dca04e3879e92533face725d4e12bbfe9ba85e41b1c7ef59e290f1421943d`
- 固定Release：[`fabricspotdefect-v0.1.0`](https://github.com/708san/CV_data_artifacts/releases/tag/fabricspotdefect-v0.1.0)。サイズとSHA-256はReleaseに掲載された値を照合済みです。

29個の矩形が画像端を最大0.5ピクセル越えていたため、画像範囲内に収めました。変更内容はartifact内の`README.md`と`ATTRIBUTION.txt`に記録しています。

## 出典・ライセンス

Sumaya, Farzana Islam, Md. Fahad Monir, and Ashraful Islam (2024), “FabricSpotDefect: An Annotated Dataset for Identifying Spot Defects in Different Fabric Types,” Mendeley Data v1, DOI: [10.17632/6574nhzm8x.1](https://doi.org/10.17632/6574nhzm8x.1)。[Mendeley掲載ページ](https://data.mendeley.com/datasets/6574nhzm8x/1)はCC BY 4.0を示しています。再利用時は作者・出典・ライセンスを表示してください。このライブラリ用に増強画像を除き、注釈形式を変換し、29個の境界外れをクリップしました。作者による推奨・承認を意味しません。

## 使い方

```python
from cvlesson import datasets

data = datasets.get("fabricspotdefect")
print(data.classes)
examples = data.to_df()
print(examples[["image_path", "boxes", "split"]].head())
```

Mendeleyページと論文では、日常の家庭用布や柄のある布を含むと説明されています。柄が写ること自体は利用を避ける理由にしていません。見た目だけの検出なので、結果は本人が確認するための参考として扱ってください。
