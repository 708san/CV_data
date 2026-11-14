# 画像AIのデータ・処理を探す

更新日：2026-11-14。生徒向けに正式登録されたデータを、課題の種類から探すための入口です。現在のカタログは**23件**です。ここにない調査候補や教師向けプレビューは、利用可能データに数えていません。

## まず処理を選ぶ

| やりたいこと | 処理 | 入力と主な結果 | 使い方へ |
|---|---|---|---|
| 画像に写るものを種類分けする | 分類 | 画像 → クラス名。自分のラベルで出力層を学習 | [ResNet分類](student-guide.md#2-分類数値予測) |
| 画像から重さなどの数値を予測する | 回帰 | 画像または画像ペア → 数値 | [ResNet回帰](student-guide.md#2-分類数値予測) |
| 画像内の文字を読む | OCR | 画像 → 文字・信頼度・位置 | [OCRの使い方と表示](ocr.md#文字を読む) |
| 物体の位置を枠で探す | 物体検出 | 画像 → ラベル・枠・スコア | [検出と表示](vision.md) |
| 画像内の対象を画素単位で塗り分ける | 領域分割 | 画像と点または枠 → マスク | [SAM領域分割](vision.md#枠や点からマスクを作る) |
| 文章や画像から画像を作る・変える | 画像生成・変換 | 文章、または文章と元画像 → 画像 | [画像生成・Image-to-Image・LoRA](image-generation.md#画像から画像への変換) |

処理をまだ決めていない場合は、[課題から選ぶ](student-guide.md)と[データとモデルの対応表](data-model-compatibility.md)を見てください。検出・領域分割・OCRは登録データの注釈を使った追加学習機能ではなく、基盤モデルによる推論です。データセットに正解注釈があることと、モデルがその注釈を使って学習・評価できることは別です。

## 生徒向けデータ一覧

「件数」はカタログに登録された画像数・サンプル数です。全画像の監査結果や学習可能性を表す数字ではありません。元split、列名、ラベルの意味、ライセンス、出典、注意事項は各データ説明で確認してください。

### 分類（9件）

| データID・説明 | カタログ件数 | 入力と含まれる情報 | 詳細 |
|---|---:|---|---|
| `tomato_leaves` — トマトの葉 | 7,209画像 | 葉画像、5種類のラベル | [内容・形式・権利](datasets/tomato_leaves.md) |
| `sky_weather_next_day` — 空と翌日の天気 | 1,000画像 | 全天空画像、晴れ/曇り/雨、撮影時刻、翌日の降水量・雲量等 | [内容・列・権利](datasets/sky_weather_next_day.md) |
| `orange_fruit` — オレンジの見た目 | 15,000画像 | オレンジ画像、見た目の5カテゴリ | [内容・形式・権利](datasets/orange_fruit.md) |
| `fresh_rotten_fruits` — 果物の見た目 | 3,193画像 | 8種類の果物×新鮮/傷みの16ラベル | [内容・形式・権利](datasets/fresh_rotten_fruits.md) |
| `indoor_plant_varieties` — 観葉植物 | 1,162画像 | 観葉植物画像、7種類のラベル | [内容・形式・権利](datasets/indoor_plant_varieties.md) |
| `trashnet` — 家庭ごみの素材 | 2,527画像 | 白背景のごみ画像、6種類の素材ラベル | [内容・形式・権利](datasets/trashnet.md) |
| `energy_meter_digits` — 電力量計の数字 | 977画像 | 切り出した1桁画像、0〜9のラベル | [内容・形式・権利](datasets/energy_meter_digits.md) |
| `fire_recognition_image` — 火・煙 | 1,112画像 | 火や煙の画像、原作者の4カテゴリ | [内容・形式・権利](datasets/fire_recognition_image.md) |
| `agrifreshnet` — 青果の見た目 | 14,084画像 | 8種類の青果×Fresh/Semi-Fresh/Rottenの24カテゴリ | [内容・形式・権利](datasets/agrifreshnet.md) |

### 回帰（1件）

| データID・説明 | カタログ件数 | 入力と含まれる情報 | 詳細 |
|---|---:|---|---|
| `lefood_set` — 食事の食前・食後 | 1,048画像 / 524組 | 食前・食後の画像ペア、重量差、見た目評価 | [内容・列・権利](datasets/lefood_set.md) |

### 物体検出（8件）

| データID・説明 | カタログ件数 | 入力と含まれる情報 | 詳細 |
|---|---:|---|---|
| `rdd2020_japan` — 日本の道路損傷 | 7,900画像 | 車載画像、ひび・穴の種類と位置 | [内容・形式・権利](datasets/rdd2020_japan.md) |
| `bangladeshi_ewaste_image` — 廃棄物品 | 2,157画像 | 画像、電子廃棄物12種類の位置 | [内容・形式・権利](datasets/bangladeshi_ewaste_image.md) |
| `geoset_ennea` — 製図用具 | 136画像 | 文具画像、9種類・物体位置 | [内容・形式・権利](datasets/geoset_ennea.md) |
| `fabricspotdefect` — 布の汚れ・変色 | 1,014画像 | 布画像、汚れ候補の矩形位置 | [内容・形式・権利](datasets/fabricspotdefect.md) |
| `indoor_waste_image` — 屋内のごみ | 4,000画像 | 床面画像、紙・プラスチック等の位置 | [内容・形式・権利](datasets/indoor_waste_image.md) |
| `wastesegcluster` — 水辺のごみ | 1,947画像 | 水辺画像、ごみの種類と位置 | [内容・形式・権利](datasets/wastesegcluster.md) |
| `click_trash` — 屋外のごみ | 1,126画像 | 屋外画像、ごみの位置 | [内容・形式・権利](datasets/click_trash.md) |
| `obstacles_assistance` — 歩道上の物体 | 1,250画像 | 歩道画像、段差・柵・穴・ポール等の位置 | [内容・形式・権利](datasets/obstacles_assistance.md) |

### 領域分割（3件）

| データID・説明 | カタログ件数 | 入力と含まれる情報 | 詳細 |
|---|---:|---|---|
| `road_traversing_knowledge` — 道路環境 | 701画像 | 道路画像、背景を含む13クラスのIDマスク | [内容・形式・権利](datasets/road_traversing_knowledge.md) |
| `fruitseg30` — 果物 | 1,914画像 | 果物画像、前景を示すマスク | [内容・形式・権利](datasets/fruitseg30.md) |
| `brazil_road_potholes` — 道路の穴 | 2,235画像 | 道路画像、穴の白黒マスク | [内容・形式・権利](datasets/brazil_road_potholes.md) |

### OCR（2件）

| データID・説明 | カタログ件数 | 入力と含まれる情報 | 詳細 |
|---|---:|---|---|
| `japanese_receipts_detailed` — 日本語レシート | 100画像 / 100サンプル | レシート画像、選択領域の文字・位置の注釈。全文正解ではない | [内容・形式・権利](datasets/japanese_receipts_detailed.md) |
| `vifoodlabel` — 食品包装表示 | 600画像 / 600サンプル | 多言語の包装画像、項目ごとの構造化文字情報 | [内容・形式・権利](datasets/vifoodlabel.md) |

## どの形式で受け取る？

データ本体はpip install時には入りません。`datasets.get()`を呼ぶと、固定版の整形済みデータ一式を取得して、リポジトリ外のキャッシュへ置きます。取得した後、表形式で確認するか、元のファイル構造を見られます。

```python
from cvlesson import datasets

# カタログだけを見る。ダウンロードは始まらない
for task in datasets.list_tasks(audience="student"):
    print(task["task"], task["datasets"])

# この呼び出しでデータ一式を取得
bundle = datasets.get("sky_weather_next_day")
frame = bundle.to_df()
print(frame.columns.tolist())  # 実際の列名を先に確認
print(frame.head())
bundle.show_examples(6)
```

`to_df()`はデータセットに応じたpandas表を返します。画像そのものではなく、画像ファイルへのパス、ラベル、split、登録された追加情報が入ります。分類・回帰の列名と検出・マスク・OCR注釈の格納方法はデータごとに異なるため、上の詳細リンクと`frame.columns`で確かめてください。データセット全体のファイル構造や変換後の形式は`bundle.root`と各説明ページにあります。

## 使い始める順番

1. 上の表から処理か題材を選ぶ。
2. 詳細ページで中身、列・注釈、出典、ライセンス、注意を読む。
3. [インストール案内](installation.md)に従って必要な機能だけ導入する。
4. `datasets.get("データID")`でデータを取得し、`to_df()`と`show_examples()`で中身を確認する。
5. 処理別ガイドの例を動かし、入力や出力を自分の課題に合わせて変える。

[AIへ開発を頼むためのプロジェクト仕様](ai-project-context.md)は、コードを書くAIにこのライブラリの約束と参照先を伝えるための文書です。
