# 日本語OCRを使う

更新日：2026-11-14

`cvlesson.ocr`は、写真に写っている文字と位置を返す推論用APIです。既定モデルは日本語に対応するPP-OCRv5 mobileです。OCRモデルの学習・追加学習は行いません。

## 準備

ColabでCPU推論を試すときは[日本語OCRのColab Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/ocr_smoke_test.ipynb)を新しいランタイムで開いてください。PyTorchを使うDETR・SAMのNotebookとは環境を分けます。Colab Python 3.13のCPUで、合成英数字画像から`TOTAL 1280 JPY`を読み取り、文字列・信頼度・座標を返すことを確認済みです。日本語実画像での精度、GPU、他OSの動作は未確認です。

CPUで使う場合、PaddlePaddle CPU版を含む`ocr` extraを一度入れるだけで使えます。GPU版を使う場合だけは、OS/CUDAに合うGPU wheelを[PaddlePaddle公式案内](https://www.paddlepaddle.org.cn/install/quick)で選んでください。利用者が`import paddle`を書く必要はなく、`ocr.load()`を呼んだ時に必要なモジュールを読み込みます。

```bash
python -m pip install --pre 'cv-data-lesson[ocr]'
```

これはPaddlePaddle CPU版、PaddleOCR 3.1.0、互換範囲を3.2未満に固定したPaddleX 3.1系、LangChain 1.0未満、Hugging Face Hubを導入します。PaddleX 3.1系がLangChain 1.xの旧APIを参照するため、LangChainの上限を指定しています。OCRモデルは合計約22 MBで、`load()`時に固定revisionからキャッシュへ取得されます。公開モデルの取得にHugging Faceのログインや`HF_TOKEN`は不要です。ライブラリはOCRを呼んだ時だけPaddle系モジュールをimportし、実行中にpip installは行いません。

OCRと検出・領域分割、画像生成を同じ環境で使う場合も、機能をまとめて指定できます。新しい仮想環境で先に依存解決してください。Colabはランタイムに既に入っているパッケージとの組み合わせがあるため、問題が出た場合は機能別に新しいランタイムを使います。

```bash
python -m pip install --pre 'cv-data-lesson[ocr,vision,diffusion]'
```

以前のColabランタイムで`No module named 'langchain.docstore'`が出た場合は、修正済みの依存指定を入れ直してからランタイムを再起動してください。古い`cvlesson`をimportしたままでは、入れ直した依存は反映されません。

## 文字を読む

`image_path`にはOCRを試す画像のパスを入れます。Colabでは次のコードで画像を選びます。ローカルでは`image_path = "./自分の画像.jpg"`のように指定してください。

```python
from google.colab import files

uploaded = files.upload()
image_path = next(iter(uploaded))
```

```python
from cvlesson import ocr

print(ocr.available_devices())  # CPUとGPUの利用可否を確認
reader = ocr.load()             # CPUを使う。初回だけモデルを取得
result = reader.predict(image_path)

print(result.text)
for line in result.lines:
    print(line.text, line.confidence, line.polygon)
```

GPUを使う場合は、CUDA対応PaddlePaddleを導入したうえで明示します。

```python
reader = ocr.load(device="gpu:0")
```

手元のPillow Imageを直接渡すこともできます。ライブラリが推論中だけ一時PNGを作り、処理後に削除します。

```python
from PIL import Image

with Image.open(image_path) as opened:
    image = opened.convert("RGB")
result = reader.predict(image)
print(result.text)
```

`result.text`は読み取った行を改行でつないだ文字列です。`confidence`はモデルの信頼度で、正解である確率を保証しません。`polygon`は画像の左上を原点とする四つの座標です。読み取り結果は元画像と照合してください。

`print(result)`でも読み取った行を表示できます。データ構造や座標が必要なときは`result.lines`または`result.to_dict()`を使います。文字位置を画像に重ねるには、文字の多い画像でラベルが重ならないよう`show_labels=False`を指定できます。

```python
from cvlesson import display

display.show(image_path, result, show_labels=False)
display.save(image_path, "results/ocr_boxes.png", result, show_labels=False)
```

## 別のモデルを使う

対応するPaddle推論形式の検出・認識モデルを手元に用意した場合、モデル名をリモートから自動取得させず、両方のローカルディレクトリを指定できます。

```python
reader = ocr.load(
    detection_model_dir="./my_text_detection_model",
    recognition_model_dir="./my_text_recognition_model",
)
```

検出モデルと認識モデルの互換性・利用条件は、利用者が個別に確認してください。

## 教材データとの利用

レシートや食品表示の画像にOCRを試せます。画像に正解文字列が付いていない場合、読み取った文の文字認識精度を数値で評価することはできません。項目別の正解が付属するデータは、その正解項目とOCR結果を人が対応付けて確認します。レシートの店舗・取引番号・QRコードなどの情報を、公開前に確かめてください。

このOCRは文字を読む補助です。金額・期限・注意書きなどの正しさは必ず人が原票と照合してください。モデルはローカル推論しますが、モデル取得時はHugging Faceからファイルをダウンロードします。

## モデル情報

既定の検出・認識モデルはそれぞれApache-2.0表示で、Hugging Faceの固定revisionを利用します。モデル本体はGitやPyPIに含めません。

OCRの文字位置は`cvlesson.display`で元画像に重ねて表示・保存できます。画像表示用の基本依存は基本インストールに含まれています。

```python
from cvlesson import display, ocr

reader = ocr.load(device="cpu")
result = reader.predict(image_path)
print(result.text)
display.show(image_path, result, show_labels=False)
display.save(image_path, "results/receipt_ocr.png", result, show_labels=False)
```

- 検出：[`PaddlePaddle/PP-OCRv5_mobile_det`](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det/tree/0d63e78e2b680928f6b1747d76a08db6e645efb7)
- 文字認識：[`PaddlePaddle/PP-OCRv5_mobile_rec`](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_rec/tree/682f20538d8c086cb2128e5cfac775e6c4904e85)
- [PaddleOCR 3.1.0 OCR仕様](https://www.paddleocr.ai/v3.1.0/en/version3.x/pipeline_usage/OCR.html)
- [PaddleOCR/PaddleX公式バージョン対応表](https://www.paddleocr.ai/main/en/version3.x/paddleocr_and_paddlex.html)

このAPIはColab Python 3.13 CPUで、合成英数字画像の実モデル推論を確認済みです。[Colab Notebook](../notebooks/colab/ocr_smoke_test.ipynb)には、CC BY-NC 4.0の公開実レシート1枚を使う追加確認も用意しました。新しい実レシート手順はまだColab未実行です。日本語実画像の認識品質、GPU、他OS・他Python版の実機確認は未実施です。
