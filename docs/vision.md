# 物体検出と領域分割

更新日：2026-11-13

この機能は学習済みモデルによる推論だけを行います。データを使った追加学習・微調整には対応しません。モデル重みはPyPIやGitに含めず、読み込み時にHugging Face Hubから固定revisionを取得してキャッシュします。

## できること

| タスク | 既定モデル | 出力と範囲 |
| --- | --- | --- |
| 物体検出 | [DETR ResNet-50](https://huggingface.co/facebook/detr-resnet-50/tree/557a3b6fcdb1be415f074c22da2e16ab4f7e8265) | COCO 2017の80カテゴリ名（英語）、信頼度、画像上の矩形。モデルカード表示はApache-2.0、約167 MB |
| プロンプト式領域分割 | [SAM ViT-B](https://huggingface.co/facebook/sam-vit-base/tree/70c1a07f894ebb5b307fd9eaaee97b9dfc16068f) | 指定した点または矩形に合うマスクと品質スコア。モデルカード表示はApache-2.0。Transformersが使うsafetensors重みは約375 MB |

DETRはCOCOにあるカテゴリだけを検出する閉集合モデルです。任意の文章で物体を探す機能ではなく、COCO外の物体を検出できる保証はありません。SAMは点・枠で指定した対象の形をマスク化しますが、その対象が何かという名前は付けません。これは意味領域分割ではありません。

検出結果をSAMへ渡す場合、ラベルはDETRの予測、マスクはSAMの予測です。枠がずれていればマスクも意図と異なることがあり、どちらの結果も画像を見て確認してください。

## インストール

Colab T4での動作確認には[DETR・SAMのColab Notebook](https://colab.research.google.com/github/708san/CV_data/blob/codex/library-ocr-runtime/notebooks/colab/vision_smoke_test.ipynb)を使えます。Python 3.13のT4で合成図形画像を実行し、DETRの検出結果とSAMのマスク・重ね合わせ表示を確認済みです。NotebookにはFruitSeg30のtest画像・正解マスクを使った追加比較も用意しましたが、Colabではまだ実行していません。1画像のIoUは全体の精度評価ではありません。

PyTorch/TorchvisionはOS、Python、CUDAに合う公式コマンドで先に導入してください。その後、Transformers等を追加します。

```bash
python -m pip install 'cv-data-lesson[vision]'
```

この追加依存はHugging Face Hub 1.xを許容し、Colabにある新しいTransformers等が必要とするHubを古い版へ下げません。

開発版の場合は`cv-data-lesson`を`-e '.[vision]'`へ置き換えます。CPUを既定にします。GPUを使う場合は、PyTorchが認識している装置を確認して明示的に選びます。

```python
from cvlesson import vision

print(vision.available_devices())
```

## 物体を検出する

```python
from cvlesson import vision

detector = vision.load_detector()  # CPU。初回は固定版モデル約167 MBを取得
results = detector.predict("street.jpg", threshold=0.6)

for item in results:
    print(item.label, item.score, item.box)
```

画像パスの代わりにPillow Imageを渡すこともできます。

```python
from PIL import Image

with Image.open("street.jpg") as opened:
    image = opened.convert("RGB")
results = detector.predict(image)
```

`box`は元画像の`(x_min, y_min, x_max, y_max)`です。信頼度しきい値は`threshold`で変更できます。GPUを使う場合は、利用可能性を確認して指定します。

```python
detector = vision.load_detector(device="cuda:0")
```

GPUが使えない場合、ライブラリはCPUへ自動で切り替えません。

別の互換検出モデルを使う場合は、Hugging Faceのrepository IDと40桁のrevisionを両方指定します。指定モデルのライセンス、容量、構造の互換性は事前に確認してください。

```python
detector = vision.load_detector(
    model_id="organization/detr-compatible-model",
    revision="0123456789abcdef0123456789abcdef01234567",  # 例。実在するcommit SHAに置き換える
)
```

## 枠や点からマスクを作る

```python
segmenter = vision.load_segmenter()  # CPU。初回は固定版の重み約375 MBを取得

# 枠：(左, 上, 右, 下)。座標は元画像上のピクセル
result = segmenter.predict("street.jpg", box=(80, 40, 360, 300))
print(result.mask.shape, result.score)
```

点を指定する場合は次のようにします。

```python
result = segmenter.predict("street.jpg", point=(210, 150))
```

`result.mask`は元画像と同じ縦横サイズのNumPy真偽値配列です。Trueの画素が対象と推定された範囲です。SAMは対象名を返しません。`result.score`はSAMが出すマスク品質の予測値です。実際のIoUや正解確率ではなく、0〜1の範囲も保証されません。マスクの正しさは画像と照らして確かめてください。

## 推論結果を画像で確認・保存する

`cvlesson.display`で検出枠、OCRの文字位置、SAMのマスクを元画像に重ねられます。`show()`はNotebookで表示し、`render()`は合成したPillow Imageを返します。`save()`は指定先へ保存します。

```python
from cvlesson import display, vision

image_path = "street.jpg"
detector = vision.load_detector(device="cpu")
detections = detector.predict(image_path)
result_image = display.show(image_path, detections)
display.save(image_path, "results/detections.png", detections)
```

SAMの場合は、マスク結果または`segment_detections()`の結果を同じ方法で渡せます。OCRでは`ocr_result`を渡すと文字枠と読み取り文字を重ねます。文字表示に使える日本語フォントが環境にない場合、枠のみ描画されることがあります。

```python
mask_result = segmenter.predict(image_path, point=(240, 180))
display.show(image_path, mask_result)
```

導入時は機能別に`display` extraを追加してください：`pip install 'cv-data-lesson[display]'`。

別のSAM互換モデルを指定するときも、repository IDと完全な40桁revisionを両方渡してください。指定モデルの利用条件やモデル構造を、このライブラリが自動で審査するものではありません。

## DETRの枠をSAMに渡す

```python
detector = vision.load_detector()
segmenter = vision.load_segmenter()

detections = detector.predict("street.jpg", threshold=0.7)
objects = segmenter.segment_detections("street.jpg", detections)

for item in objects:
    print("DETRのカテゴリ:", item.detection.label)
    print("DETRの信頼度:", item.detection.score)
    print("SAMのマスク品質スコア:", item.segmentation.score)
```

この例では検出結果ごとにSAMを実行するため、複数物体では処理時間とメモリ使用量が増えます。`detection.label`はSAMの分類結果ではありません。

## モデル・権利・確認状況

| モデル | 固定revision | 配布元のライセンス表示 | 重み容量 | 実環境テスト |
| --- | --- | --- | --- | --- |
| DETR ResNet-50 | `557a3b6fcdb1be415f074c22da2e16ab4f7e8265` | Apache-2.0 ([model card](https://huggingface.co/facebook/detr-resnet-50/tree/557a3b6fcdb1be415f074c22da2e16ab4f7e8265)) | 約167 MB | Colab T4で合成画像の検出を確認 |
| SAM ViT-B | `70c1a07f894ebb5b307fd9eaaee97b9dfc16068f` | Apache-2.0 ([model card](https://huggingface.co/facebook/sam-vit-base/tree/70c1a07f894ebb5b307fd9eaa97b9dfc16068f)) | safetensors約375 MB。Hub上の全ファイルは約1.13 GB | Colab T4でboolマスクと重ね合わせ表示を確認 |

Hugging FaceのTransformers公式手順に沿ってSAMの枠・点プロンプトとマスク後処理を実装しています（[Mask Generation task guide](https://huggingface.co/docs/transformers/tasks/mask_generation)）。固定revision、モデルカード上のライセンス表示、容量は2026-11-13に確認しました。Colab T4でモデル実取得と合成画像の推論を確認済みです。CPU推論、他環境との互換性、実データでの精度評価は未確認です。通常のテストではモデル重みをダウンロードしません。
