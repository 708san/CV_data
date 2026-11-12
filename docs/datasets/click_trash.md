# CLICK Trash Dataset

屋外に捨てられたごみの位置を、画像上の枠で示すデータです。学校や地域の清掃活動で、見つけた場所を記録・共有する試作に使えます。

```python
from cvlesson import datasets

data = datasets.get("click_trash")
print(data.classes)       # ('trash',)
print(data.splits)        # train / valid / test の件数
print(data.annotations_jsonl)  # 画像ごとのbbox注釈
```

## 内容と形式

- 画像1,126枚、single-class `trash` のbbox注釈2,213件
- train 901枚、valid 113枚、test 112枚。ごみが写らない背景画像4枚は空ラベルで保持
- 長辺1,024px以下のJPEG。ラベルはYOLO正規化bboxと共通形式JSONL
- 元の13クラス版とCOCOポリゴン注釈は含みません。希少クラスの学習・評価が困難なため、1クラス版を選びました

## 課題に使うとき

清掃活動の写真でごみの位置を見つけ、活動場所の記録を作る補助システムの試作に向きます。撮影地はインドで、日本の通学路・学校周辺の景色を代表しません。地域での活動に使う場合は、生徒が撮影した現地画像でも確かめてください。モデルの出力は分別方法や危険性を判定せず、人が画像を確認してください。

## 出典とライセンス

Manjit Baishya (2026), [CLICK Trash Dataset, Mendeley Data v2](https://data.mendeley.com/datasets/htcvvz6fm2/2), DOI [10.17632/htcvvz6fm2.2](https://doi.org/10.17632/htcvvz6fm2.2), CC BY 4.0. 出典と変更内容は[権利・監査記録](https://github.com/708san/CV_data_artifacts/blob/main/licenses/click_trash-v0.1.0.md)に記載しています。

画像を長辺1,024px以下・JPEG品質0.88で再書き出しし、元のEXIF・GPS・撮影機器情報を除去しました。bbox座標は変更せず、`val`を`valid`に表記しています。包装の文字や商標が写る場合があり、企業・商品の推薦を意味しません。
