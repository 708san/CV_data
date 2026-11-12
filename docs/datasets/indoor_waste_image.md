# 屋内に残ったごみの位置 — Indoor Waste Image Dataset

学校行事後などに床に残ったごみを見つけ、清掃箇所の確認を補助する物体検出教材です。

- 画像4,000枚、4種類6,968枠。1280×720の元画像は変更していません。
- 出典: [Mendeley Data v1](https://data.mendeley.com/datasets/dy7smxr93r/1)、CC BY 4.0。
- 複数動画に由来する画像は、同じ動画が別splitへ混ざらないよう分割しています。画像外にはみ出した注釈380件を画像内へ収めました。
- 50枚を目視確認。離れた人物が写る画像もあるため、代表確認を全画像のプライバシー審査とはみなしません。

```python
from cvlesson import datasets
data = datasets.get("indoor_waste_image")
print(data.to_df().head())
```

モデルはごみ候補の位置を示すだけです。実際の分別は地域のルールを確認し、人が判断してください。帰属・変更内容は[監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/indoor_waste_image-v0.1.0-audit.json)を参照。
