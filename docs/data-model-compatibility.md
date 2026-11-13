# データとモデルの対応表

更新日：2026-11-13  
対象：生徒向けデータカタログ22件。データ本体は取得せず、カタログ・変換処理・モデルAPIの実装を照合。

この文書は、登録済みデータを取得したあと何ができるかを示します。カタログ登録は、すべての基盤モデルとの互換性や、注釈を使った学習・評価を意味しません。ライセンス、出典、固定版、注意事項は`datasets.info(dataset_id)`と各データ説明を確認してください。

## まず共通の使い方

```python
from cvlesson import datasets

# 課題から選ぶ。カタログ表示ではデータをダウンロードしない
datasets.list_tasks(audience="student")
datasets.list_available(task="classification", audience="student")

# IDを指定して初めて取得する。整形済みartifact全体をキャッシュへ展開
data = datasets.get("tomato_leaves")
print(data.id, data.kind, data.splits)
data.show_examples(n=6, split="train")

# pandasは[dataframe] extraが必要。画像自体はDataFrameに読み込まずパスで参照
frame = data.to_df()
print(frame.head())
```

`get()`はデータ全体を取得してキャッシュします。`to_df()`はデータ本体ではなく、画像・ラベル・注釈ファイルへのパスとメタデータを表にします。各タスクの元splitを保ちます。分類で元データにvalidationがない場合だけ、trainからseed固定でvalidationを作ります。取得量、権利条件、キャッシュの確認には`datasets.info()`、`datasets.cache_info()`を使ってください。

## 登録データ一覧

| タスク / 件数 | ID | `kind` | `to_df()`の主な内容 | 現行のモデル接続 |
|---|---|---|---|---|
| 分類 8件 | `tomato_leaves`、`orange_fruit`、`fresh_rotten_fruits`、`indoor_plant_varieties`、`trashnet`、`energy_meter_digits`、`fire_recognition_image`、`agrifreshnet` | `classification` | `image_path`, `label`, `label_ja`, `label_id`, `split`, `sample_id` ほか | ResNet分類の学習・予測に接続可能 |
| 回帰 1件 | `lefood_set` | `regression` | 食前・食後の`image_before_path` / `image_after_path`、重量値、残食率、`split` | 画像ペアを入力するResNet回帰に接続可能 |
| 物体検出 8件 | `rdd2020_japan`、`bangladeshi_ewaste_image`、`geoset_ennea`、`fabricspotdefect`、`indoor_waste_image`、`wastesegcluster`、`click_trash`、`obstacles_assistance` | `detection` | `image_path`, `label_file`, `boxes`, `split`, `sample_id` | 画像をDETRへ渡してCOCOカテゴリを推論可能。教師注釈を使う学習・評価APIはない |
| 領域分割 3件 | `road_traversing_knowledge`、`fruitseg30`、`brazil_road_potholes` | `segmentation` | `image_path`, `mask_path`, `label`, `label_id`, `split`, `sample_id` | 画像をSAMへ渡し、別途指定した点・枠からマスクを推論可能。教師マスクを使う学習・評価APIはない |
| OCR 2件 | `japanese_receipts_detailed`、`vifoodlabel` | `ocr` | `image_path`, 構造化された`ground_truth`, `split`, `sample_id` | 画像をOCRへ渡して文字を推論可能。正解との自動評価・OCR学習APIはない |

`energy_meter_digits`は数字画像を0〜9のクラスに分類するデータです。連続した文字列を読むOCRデータではありません。

## タスク別にモデルへ渡す方法

### 画像分類：ResNetで学習できる

`ResNetClassifier.fit(X, y)`は画像パスまたはPillow Imageの列とラベル列を受け取ります。データから使う場合は、画像パスを含むDataFrameを渡せます。`to_df()`の行を使うなら、学習splitだけを選びます。

```python
from cvlesson.models import ResNetClassifier

frame = data.to_df()
train = frame[frame["split"] == "train"]
model = ResNetClassifier(device="cpu", epochs=5)
model.fit(train["image_path"], train["label"])
```

予測はラベルのNumPy配列、`predict_proba()`はクラスごとの確率目安の配列、`score()`は正解率を返します。クラス名の順は`model.classes_`で確認できます。手元の画像は`PIL.Image.open(...)`で開いてそのまま`predict()`へ渡せます。`to_torch_dataset()`も分類データを遅延読込の`(画像tensor, label_id)`にできますが、ResNetEstimatorの`fit()`はこのDatasetを直接受け取るAPIではありません。

### 画像回帰：食前・食後のペアと実測値を使う

`lefood_set`は画像1枚ではなく食前・食後の2枚を組にして扱います。`ResNetRegressor`はこの2列を含むDataFrameを入力にできます。自分の画像ペアを使うときは各要素をパスまたはPillow Imageで指定できます。

```python
from cvlesson.models import ResNetRegressor

data = datasets.get("lefood_set")
frame = data.to_df()
train = frame[frame["split"] == "train"]
model = ResNetRegressor(device="cpu", epochs=5)
model.fit(train[["image_before_path", "image_after_path"]], train["consumed_weight_g"])
```

単一の数値を学習した場合、`predict()`はサンプルごとの数値を返します。複数出力も扱えますが、回帰データの測定値の意味・単位と、異常値の扱いを確認してから目的の列を選んでください。

### 物体検出：データ注釈とDETR推論は別々に扱う

`boxes`列には各画像の矩形、クラスID、クラス名などが入ります。DETRは画像パスまたはPillow Imageを受け取り、`Detection(label, score, box)`のリストを返します。`box`は元画像上の`(x_min, y_min, x_max, y_max)`です。

```python
from cvlesson import vision
from cvlesson import datasets

data = datasets.get("rdd2020_japan")
frame = data.to_df()
detector = vision.load_detector(device="cuda:0")  # GPUを使う場合だけ明示
image_path = frame.iloc[0]["image_path"]
predictions = detector.predict(image_path)
```

手元画像を使う場合は、Pillow Imageを直接渡せます。

```python
from PIL import Image
from cvlesson import display

with Image.open("my_image.jpg") as opened:
    image = opened.convert("RGB")
predictions = detector.predict(image)
display.show(image, predictions)
```

結果は共通表示APIで確認できます。

```python
from cvlesson import display

display.show(image_path, predictions)
display.save(image_path, "results/detections.png", predictions)
```

このDETRはCOCOの80カテゴリを対象とする事前学習モデルです。データセットの教師ラベルを使ってDETRを学習したり、予測と教師bboxを自動比較したりする機能はありません。データ内のカテゴリがCOCOカテゴリに含まれるか、座標の意味が合うかを確認せずに精度評価へ使わないでください。

### 領域分割：SAMに画像と点または枠を渡す

`mask_path`はデータセットが持つ正解マスクです。`to_torch_dataset()`は画像とマスクを遅延読込し、`(画像tensor, mask tensor)`を返します。ただし現行モデルAPIのSAMは基盤モデル推論用で、SAMの学習や正解マスクとのIoU等の自動評価には接続されていません。

```python
from cvlesson import vision
from cvlesson import datasets

data = datasets.get("fruitseg30")
frame = data.to_df()
image_path = frame.iloc[0]["image_path"]
from PIL import Image
with Image.open(image_path) as image:
    width, height = image.size
segmenter = vision.load_segmenter(device="cuda:0")
prediction = segmenter.predict(image_path, point=(width // 2, height // 2))
mask = prediction.mask  # 元画像と同じ縦横のNumPy bool配列
```

```python
from cvlesson import display

display.show(image_path, prediction)
display.save(image_path, "results/segmentation.png", prediction)
```

SAMはクラス名を予測しません。正解マスクと結果を比較するには、画像ごとの対象・クラス・マスク値の意味を確認し、別途比較処理が必要です。`score`はSAMのマスク品質予測値で、確率や実測IoUではありません。

### OCR：画像を読み取り、構造化正解は参照用

OCRデータの`ground_truth`にはデータ固有の文字・項目情報があります。現行OCR APIは画像ファイルパスを読み、`OCRResult`を返します。`result.text`、各行の文字・信頼度・四点座標、または`result.to_dict()`で結果を参照できます。

```python
from cvlesson import ocr
from cvlesson import datasets

data = datasets.get("japanese_receipts_detailed")
frame = data.to_df()
image_path = frame.iloc[0]["image_path"]
reader = ocr.load(device="cpu")
result = reader.predict(image_path)
print(result.text)
print(result.to_dict())
```

```python
from cvlesson import display

display.show(image_path, result)
display.save(image_path, "results/ocr.png", result)
```

OCRモデルは推論専用です。`ground_truth`はデータの正解情報であり、現行APIが自動で読み込んでモデル評価するわけではありません。データに文字列全体ではなく項目別JSONが含まれる場合もあるため、正解形式を確認してから評価方法を決めてください。

## 画像入力・出力形式の現状

| 機能 | 入力 | 主な出力 | 画像パス以外 |
|---|---|---|---|
| ResNet分類・回帰 | 画像パスまたはPillow Imageの列、対応DataFrame。回帰は画像ペア | NumPy配列、正解率またはR² | NumPy画像配列は未対応 |
| OCR | 画像パスまたはPillow Image | `OCRResult`、`OCRLine`。`to_dict()`あり | Pillow入力は推論中だけ一時PNGへ変換。NumPy画像配列は未対応 |
| 物体検出 | 画像パスまたはPillow Image | `Detection`のリスト | NumPy画像配列は未対応 |
| SAM領域分割 | 画像パスまたはPillow Imageと点または矩形 | `Segmentation`（NumPy bool mask、品質予測値、prompt情報） | NumPy画像配列は未対応 |
| SDXL生成 | prompt。画像変換時は画像パスまたはPillow Image | Pillow Image | 画像変換ではPillow Imageも可。NumPy画像は未対応 |

検出・領域分割・OCRの結果クラス自体に`show()`や`save()`はありませんが、`cvlesson.display.render(image, result)`で合成したPillow Imageを作り、`display.show(image, result)`または`display.save(image, path, result)`で確認・保存できます。`display` extraを必要時に導入します。OCR結果だけは別途`to_dict()`も持ちます。

## ここから見える優先改善

1. 最初に`list_tasks()`、`get()`、`show_examples()`、`to_df()`を順に試す短いデータ選択例を入口に置く。
2. 分類・回帰でtrainだけを使い、validation/testを評価へ回す例を用意する。特に回帰のペア列を誤って単画像として扱わない。
3. 検出・領域分割・OCRは「正解注釈の閲覧」と「基盤モデル推論」が別操作であることをNotebookで示す。
4. 結果表示は共通化済み。次は画像入力と描画を実モデルを使うColabで確認する。
5. タスク別の教師注釈評価が必要になったら、座標系・クラス対応・マスクencoding・OCR正解JSONの形を明記した上で別要件として追加する。

