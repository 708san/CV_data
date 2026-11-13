# 水辺のごみ位置 — WasteSegCluster

水辺の画像1,947枚に、ごみ4カテゴリの位置を示す物体検出データです。位置やカテゴリ別の分布を記録・比較できます。清掃場所の確認や活動記録などは使用例です。

- 画像1,947枚、4クラス3,900枠。出典のCOCO bboxを正規化YOLO形式へ変換し、画像画素は変更していません。
- 出典: [Mendeley Data v4](https://data.mendeley.com/datasets/3wnf3n242s/4)、CC BY 4.0。ダッカ周辺で撮影。
- 元データのpolygon形状ではなくbboxで提供します。注釈のない1枚は「ごみがない」と確認された画像ではありません。

```python
from cvlesson import datasets
data = datasets.get("wastesegcluster")
print(data.to_df().head())
```

日本の水辺で同じ種類・写り方をするとは限らないため、地域写真で別途確かめてください。水質や健康影響は判定しません。[監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/wastesegcluster-v0.1.0-audit.json)。
