# 歩道上の物体候補 — Obstacles Avoidance Assistance

歩道や道路脇の画像1,250枚に、段差・柵・穴・ポールのbboxを付けた物体検出データです。配布元にtest splitはなく、train 1,000枚・valid 250枚です。

```python
from cvlesson import datasets

data = datasets.get("obstacles_assistance")
print(data.classes)       # ('bump', 'fence', 'hole', 'pole')
print(data.splits)        # train / valid の件数
print(data.annotations_jsonl)
```

## 課題に使うとき

歩道の通りにくさを記録する地図づくりを試作できます。画像上に出るのは物体の位置候補です。柵やポールは写っているだけで通行を妨げるとは限らず、通路幅・迂回路・利用する人の状況もラベルにはありません。実際の移動支援や通行案内をモデルだけで行わず、現地の人と当事者が確認してください。配布元が明記する撮影地域はありません。日本の歩道で使う場合は、地域で撮影した画像で見直します。

## 内容・整形

- 画像1,250枚、bbox注釈1,627件
- train 1,000枚、valid 250枚。test splitはありません
- クラス: `bump`, `fence`, `hole`, `pole`
- 640×640のJPEGを元の画素のまま収録。正規化YOLO bbox座標も変更していません
- 画像とラベルの対応、クラス、座標範囲を全件確認。画像に欠損はなく、完全一致重複はありません
- 元のYOLO形式に加え、共通JSONL注釈・metadata・日本語クラス名を収録

## 権利・出典

Yi Xian Wang (2025), [Obstacles Avoidance Assistance for Visually Impaired, Mendeley Data v1](https://data.mendeley.com/datasets/xwhnp82rhk/1), DOI [10.17632/xwhnp82rhk.1](https://doi.org/10.17632/xwhnp82rhk.1), CC BY 4.0. 出典と変更内容は[権利記録](https://github.com/708san/CV_data_artifacts/blob/main/licenses/obstacles_assistance-v1.0.md)に記載しています。

配布元説明では、画像は公開Roboflowデータから選び、手作業でラベルを付けたとされていますが、個別の上流データセットIDやライセンス一覧は掲載されていません。この出所の限界も含め、Mendeleyに明記されたCC BY 4.0表示に基づいて帰属表示付きで整備しました。

## AIで課題を試作する

```python
from cvlesson import datasets

data = datasets.get("obstacles_assistance")
print(data.manifest["split_counts"])
print(data.class_names_ja)
```

このライブラリはデータの取得と形式の統一をします。物体検出モデルの学習APIは提供していません。モデルの出力は現地の通りやすさ・安全性を決めるものではありません。
