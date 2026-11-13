# CLICK Trash Dataset

屋外に捨てられたごみの位置を画像上の枠で示すデータです。位置検出、画像上への表示、画像ごとの個数比較などに応用できます。清掃活動の記録・共有は使用例の一つです。

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

## データの範囲と使用例

ごみの位置を示す単一クラスのbboxを使った検出を試せます。清掃記録や画像上の位置共有などは使用例です。撮影地はインドで、日本の通学路・学校周辺の景色を代表しません。分別方法や危険性は判定しません。

## 出典とライセンス

Manjit Baishya (2026), [CLICK Trash Dataset, Mendeley Data v2](https://data.mendeley.com/datasets/htcvvz6fm2/2), DOI [10.17632/htcvvz6fm2.2](https://doi.org/10.17632/htcvvz6fm2.2), CC BY 4.0. 出典と変更内容は[権利・監査記録](https://github.com/708san/CV_data_artifacts/blob/main/licenses/click_trash-v0.1.0.md)に記載しています。

画像を長辺1,024px以下・JPEG品質0.88で再書き出しし、元のEXIF・GPS・撮影機器情報を除去しました。bbox座標は変更せず、`val`を`valid`に表記しています。包装の文字や商標が写る場合があり、企業・商品の推薦を意味しません。
