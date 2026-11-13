# 青果の見た目の段階 — AgriFreshNET

8種類の青果を元データのFresh・Semi-Fresh・Rottenカテゴリに分類するデータです。画像の整理やカテゴリ・撮影条件ごとの比較などに応用できます。元ラベルの日数は残存日数や可食性を示しません。

- 重複・ラベル競合画像を除いた14,084枚、24クラス。
- 出典: [Mendeley Data v1](https://data.mendeley.com/datasets/42m5tb7yv9/1)、CC BY 4.0。
- 同じ元画像から作られた増補画像は同一splitにまとめました。画像データ自体は変更していません。

```python
from cvlesson import datasets
data = datasets.get("agrifreshnet")
print(data.to_df().head())
```

クラス名の括弧内の日数は出典のラベルで、保存可能日数の実測値ではありません。画像分類は食べられるか・食品安全を判定しません。現物を確認してください。[監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/agrifreshnet-v0.1.0-audit.json)。
