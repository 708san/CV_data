# Road Traversing Knowledge（道路環境の領域分割）

## 概要

ブラジル南部サンタカタリーナ州の地方道路で撮影された701枚の画像と、同じ大きさの画素マスクを組にしたデータです。道路や道路標示、水たまり、穴、ひび割れなど12種類と背景を、マスクの画素値0〜12で表します。画像は352×288ピクセルです。

生徒の課題例は「画像の中で、路面・水たまり・穴・ひび割れがどこにあるかを色分けし、地域の道路環境を調べる」です。日本の道路を代表するデータではないため、実際の通学路の安全性を判定するAIとしては使いません。

## 使い方

```python
from cvlesson import datasets

data = datasets.get("road_traversing_knowledge")
print(data.classes)
print(data.class_names_ja)
print(data.splits)  # train 561、val 140、test 0
examples = data.to_df()
print(examples[["image_path", "mask_path", "split"]].head())
```

画像とマスクをPyTorch形式で読み込むと、マスクは各画素のクラスIDを保持する`torch.long`テンソル（高さ×幅）になります。モデルの出力クラス数は13です。画像は`data.images_dir`、マスクは`data.masks_dir`から参照できます。学習・検証には公式trainとvalidationを使います。公式test splitはありません。

## 分割と形式

公式のtrain 561組・validation 140組をそのまま維持しています。画像・マスクのPNGファイルは画素を変更せずコピーし、`labels.csv`、`metadata.jsonl`、`classes.json`を追加して共通形式にまとめました。mask ID 8（マンホール）はクラス定義にありますが、全マスクの画素中には現れません。

道路環境のマスクは多クラス画素ID方式です。FruitSeg30などの濃淡前景マスクとは形式が異なり、PyTorchでは二値マスクとして0〜1へ変換しません。

## 出典・利用条件

Thiago Rateke, Aldo von Wangenheim, Rafael Toledo (2023), “Road Traversing Knowledge,” Mendeley Data v1, [DOI: 10.17632/hssswvmjwf.1](https://doi.org/10.17632/hssswvmjwf.1)。掲載ページはCC BY 4.0を示します。再配布には著者・出典・ライセンスの表示と、共通形式へ整理した変更の明記が必要です。Mendeleyの固定版スナップショットは、データ内に第三者の権利物がある場合は追加の許諾が必要となる可能性を明記しています。詳細は[権利記録](https://github.com/708san/CV_data_artifacts/blob/main/licenses/road_traversing_knowledge-v1.md)と[全量監査報告](../../reports/road_traversing_knowledge-v1-full-audit.json)を参照してください。

### 注意

- 撮影地・天候・時間帯に偏りがあります。日本の道路やすべての季節・環境には一般化できません。
- 生徒の学習と画像比較に使い、現実の道路の安全・通行可否・修繕の判断には使いません。
- 公式のtest splitはありません。trainとvalidationの成績を、未知の道路すべてに通用する精度として扱わないでください。
- 予測結果だけで自治体・地域・道路管理者を評価しないでください。
