# 日本語OCRを使う

更新日：2026-11-13

`cvlesson.ocr`は、写真に写っている文字と位置を返す推論用APIです。既定モデルは日本語に対応するPP-OCRv5 mobileです。OCRモデルの学習・追加学習は行いません。

## 準備

ColabでCPU推論を試すときは[日本語OCRのColab Notebook](https://colab.research.google.com/github/708san/CV_data/blob/codex/library-ocr-runtime/notebooks/colab/ocr_smoke_test.ipynb)を新しいランタイムで開いてください。PyTorchを使うDETR・SAMのNotebookとは環境を分けます。Colab上での実行結果は未確認です。

PaddlePaddleはCPU/GPUとCUDAの組み合わせにより導入コマンドが異なります。PyTorch系ライブラリとの競合を避けるため、OCR専用の仮想環境を使う方法を勧めます。[インストール手順](installation.md#ocr用の環境)で環境に合うPaddlePaddleを導入してください。利用者が`import paddle`を書く必要はありません。`ocr.load()`を呼んだ時にライブラリが必要なモジュールを読み込みます。

```bash
python -m pip install -e '.[ocr]'
```

これはPaddleOCR 3.1.0、互換範囲を3.2未満に固定したPaddleX 3.1系、LangChain 1.0未満、Colabの標準`requests`版を保つ範囲、およびHugging Face Hubを導入します。PaddleX 3.1系がLangChain 1.xの旧APIを参照するため、LangChainの上限を指定しています。Hugging Face Hubは1.xも利用でき、Colabに入っている他のAIパッケージを古いHubへ下げません。PaddlePaddle本体はCPU/GPU・CUDA環境に合わせて別に導入します。OCRモデルは合計約22 MBで、次の`load()`時に固定revisionからキャッシュへ取得されます。公開モデルの取得にHugging Faceのログインや`HF_TOKEN`は不要です。ライブラリはOCRを呼んだ時だけPaddle系モジュールをimportし、実行中にpip installは行いません。

以前のColabランタイムで`No module named 'langchain.docstore'`が出た場合は、修正済みの依存指定を入れ直してからランタイムを再起動してください。古い`cvlesson`をimportしたままでは、入れ直した依存は反映されません。

## 文字を読む

```python
from cvlesson import ocr

print(ocr.available_devices())  # CPUとGPUの利用可否を確認
reader = ocr.load()             # CPUを使う。初回だけモデルを取得
result = reader.predict("receipt.jpg")

print(result.text)
for line in result.lines:
    print(line.text, line.confidence, line.polygon)
```

GPUを使う場合は、CUDA対応PaddlePaddleを導入したうえで明示します。

```python
reader = ocr.load(device="gpu:0")
```

`result.text`は読み取った行を改行でつないだ文字列です。`confidence`はモデルの信頼度で、正解である確率を保証しません。`polygon`は画像の左上を原点とする四つの座標です。読み取り結果は元画像と照合してください。

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

- 検出：[`PaddlePaddle/PP-OCRv5_mobile_det`](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det/tree/0d63e78e2b680928f6b1747d76a08db6e645efb7)
- 文字認識：[`PaddlePaddle/PP-OCRv5_mobile_rec`](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_rec/tree/682f20538d8c086cb2128e5cfac775e6c4904e85)
- [PaddleOCR 3.1.0 OCR仕様](https://www.paddleocr.ai/v3.1.0/en/version3.x/pipeline_usage/OCR.html)
- [PaddleOCR/PaddleX公式バージョン対応表](https://www.paddleocr.ai/main/en/version3.x/paddleocr_and_paddlex.html)

このAPIはネットワーク不要のテストで形式を検査できますが、OCR実モデルのCPU/GPU推論はまだ実環境で確認していません。
