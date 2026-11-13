# まず試す

このページは、課題や使うデータを固定しない短い使い始め方です。候補を見てからデータを選び、内容を確認して、選んだ機能の説明へ進みます。

## 1. 必要な機能を入れる

PyPIにはまだ公開していません。インストールは[目的別の手順](installation.md#目的から選ぶ)から選んでください。データ一覧だけなら追加依存なし、画像表示も使う場合は`display`を追加します。`display`には画像サンプル表示に必要なDataFrame依存も含み、`show_examples()`のMatplotlib図はライブラリが日本語フォント設定を行います。

```bash
python -m pip install -e '.[display]'
```

## 2. 課題とデータを選ぶ

カタログ表示ではデータをダウンロードしません。まずtaskとデータ候補を選び、`info()`で出典・利用条件・形式を確認してから取得します。

```python
from cvlesson import datasets

tasks = datasets.list_tasks(audience="student")
for task in tasks:
    print(task["task"], task["name_ja"], task["datasets"])

# 例として分類候補を表示。別のtaskを選ぶ場合は、そのtaskの形式に合う案内も参照します。
choices = datasets.list_available(task="classification", audience="student")
for item in choices:
    print(item["id"], item["name_ja"], item["画像数"], item["ダウンロードサイズMB"], "MB")
```

使うIDを一覧から選びます。`get()`を呼んだときに、そのデータ一式がダウンロードされ、リポジトリ外のキャッシュへ展開されます。

```python
dataset_id = choices[0]["id"]  # choicesから別のIDを選んでも同じ手順
print(datasets.info(dataset_id))  # 出典、利用条件、形式、注意を取得前に確認

data = datasets.get(dataset_id)
print(data.kind, data.splits)
data.show_examples(n=6, split="train")
frame = data.to_df()
print(frame.head())
```

画像データの列や正解注釈はtaskに合わせて異なります。[全データとモデルの対応表](data-model-compatibility.md)で、ラベル・bbox・マスク・OCR正解とモデルAPIの接続方法を確認してください。ResNet分類・回帰は学習できます。OCR・DETR・SAMは既定モデルの推論APIで、データセットの正解注釈を使った学習機能ではありません。

## 3. 手元の画像で推論する

ローカルでは自分の画像ファイルのパスを指定します。

```python
image_path = "my_image.jpg"
```

Colabでは次のセルで自分の画像をランタイムへアップロードし、そのパスを使えます。どちらも以降は同じモデルAPIに渡せます。Pillow Imageとして開いた画像も同じモデルAPIに渡せます。

```python
# Colabで実行する場合。選んだ画像は現在の一時ランタイムへアップロードされます。
from google.colab import files

uploaded = files.upload()
if not uploaded:
    raise RuntimeError("画像ファイルを選んでください")
image_path = next(iter(uploaded))
```

ローカルPythonでは`image_path = "my_image.jpg"`のように自分のファイルを指定します。以下はどちらでも同じです。

```python
from PIL import Image
from cvlesson import display, vision

with Image.open(image_path) as opened:
    image = opened.convert("RGB")

print(vision.available_devices())
detector = vision.load_detector(device="cpu")  # GPU利用時は確認後、device="cuda:0"を指定
results = detector.predict(image)
display.show(image, results)
```

この短い例は、入力から結果表示までの形を示しています。既定DETRはCOCOの80カテゴリを検出するため、任意の物体名を理解するモデルではありません。課題・データに合うモデルを選び、限界を[検出と領域分割](vision.md)で確認してください。

## 機能別の例

| やりたいこと | API・案内 |
|---|---|
| データと形式を調べる | [データとモデルの対応表](data-model-compatibility.md) |
| ResNetで画像分類・回帰 | [データとモデルの対応表](data-model-compatibility.md#タスク別にモデルへ渡す方法) |
| 文字を読む | [OCRの使い方](ocr.md) |
| 物体の枠や領域マスクを得る | [検出と領域分割](vision.md) |
| 画像を作る・描き変える | [画像生成とLoRA](image-generation.md) |
| OSやColabに合わせて導入する | [インストール案内](installation.md) |

## Colabで機能と実データを確認する

各NotebookはColabの新しいランタイムで別々に実行します。OCRはCPU、ResNet・検出・領域分割・SDXLはT4 GPUを選んでください。全Notebookを同じランタイムで続けて実行しないでください。

| Notebook | 確認する内容 | データ・注意 |
|---|---|---|
| [ResNet分類](../notebooks/cv/classification_v1.ipynb) | 実データで`fit`、validation/testの`score`、`predict`、`predict_proba` | トマト葉7,209枚、CC0 1.0、約124 MB。病気の確定診断には使わない |
| [ResNet回帰](../notebooks/colab/resnet_regression_smoke_test.ipynb) | 画像ペアで`fit`、R²、実測値と予測値の比較 | LeFood-Set 524組、CC BY 4.0、約53 MB。研究環境は日本の学校給食を代表しない |
| [OCR](../notebooks/colab/ocr_smoke_test.ipynb) | 合成画像と公開実レシート画像1枚での推論 | 詳細レシート版、CC BY-NC 4.0、約130 MB。非商用のみ。残存情報があるため結果を公開しない |
| [検出・領域分割](../notebooks/colab/vision_smoke_test.ipynb) | 自分の画像とFruitSeg30のtest画像でDETR/SAMを推論 | FruitSeg30はCC BY 4.0、約68 MB。SAM比較は1画像の動作確認で、全体性能ではない |
| [SDXL・LoRA](../notebooks/colab/generation_smoke_test.ipynb) | text-to-image、image-to-imageと登録LoRA 4件 | T4と数GBの空き容量が必要。入力画像は合成画像か明示アップロードを選択 |

同じモデル名でも入力やデータの条件で結果は変わります。これらのNotebookは各APIと一部実データで一連の処理が動くか確認するもので、一般化性能の保証ではありません。Colabから開くNotebookの変更がGitHubに反映されていない場合は、作業ブランチの更新後に再読み込みしてください。

