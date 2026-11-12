# 道路の穴の領域分割

[Mendeley Data v3](https://data.mendeley.com/datasets/t576ydh9v8/3)の画像2,235枚と、道路の穴を白く示すマスク2,235枚を収録しています。元画像とマスクの画素は変更せず、同じ道路区間の画像が複数のsplitへまたがらないよう、ファイル名から読み取った区間単位でtrain/val/testへ分けました。元データにある道路全体・ひび割れのマスクは含めていません。

配布元ページのライセンス表記はCC BY 4.0です。出典と変更内容を表示してください。画像はブラジルのDNITから情報公開請求を通じて提供されたと説明されており、元画像にDNITの透かしが残っています。DNITの推薦を示すものではありません。[ライセンス・監査記録](https://github.com/708san/CV_data_artifacts/blob/main/licenses/brazil_road_potholes-v1.md)。

```python
from cvlesson import datasets

data = datasets.get("brazil_road_potholes")
print(data.to_df().head())
```

通学路や地域の道路の穴を記録し、修繕要望を伝えやすくする試作に使えます。画像はブラジルの道路を2014〜2017年に撮影したものなので、日本の道路へそのまま適用できません。モデル出力は安全性や修繕の必要性を判定しません。地域の写真を使って別途確かめてください。
