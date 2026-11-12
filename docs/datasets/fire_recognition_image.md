# 火・煙の教材画像 — Fire Recognition Image Dataset

火や煙の画像を分類し、周囲の人が確認する手順を考える教材です。

- 元画像PNG 1,112枚、4クラス。加工済み増補画像を除き、画像画素を保ったまま分割しました。
- 出典: [Mendeley Data v4](https://data.mendeley.com/datasets/7jk6xh7h6w/4)、CC BY 4.0。
- クラス名は作成者の画像カテゴリです。`Safe_Fire`は実場面の安全を意味しません。

```python
from cvlesson import datasets
data = datasets.get("fire_recognition_image")
print(data.to_df().head())
```

警報・避難・緊急時の行動をモデルに決めさせないでください。火災設備や大人・緊急窓口の指示に置き換わるものではありません。[監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/fire_recognition_image-v0.1.0-audit.json)。
