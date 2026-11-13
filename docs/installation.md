# インストール案内

このページはPyPIから利用する人向けです。開発用checkoutの手順は含みません。

## 基本環境

Python 3.11〜3.13が対象です。仮想環境の利用をおすすめします。

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 目的別にインストール

画像表示も使う基本的な導入：

```bash
python -m pip install --pre 'cv-data-lesson[display]'
```

データ一覧と取得だけなら`display`を省略できます。alpha版を使うため`--pre`を付けてください。

| 使いたい機能 | インストール・準備 | 実行時に取得するもの |
|---|---|---|
| データ一覧・説明・取得 | `python -m pip install --pre cv-data-lesson` | `datasets.get()`を呼んだデータの固定Release ZIP |
| 表・画像例の確認 | `python -m pip install --pre 'cv-data-lesson[display]'` | データ取得時のZIP |
| DataFrame | `python -m pip install --pre 'cv-data-lesson[dataframe]'` | データ取得時のZIP |
| ResNet分類・回帰 | GPU/OSに合うPyTorchとTorchvisionを公式手順で導入後、`python -m pip install --pre 'cv-data-lesson[torch]'` | ResNetの重み |
| 日本語OCR | 対応するPaddlePaddleを導入後、`python -m pip install --pre 'cv-data-lesson[ocr]'` | OCRモデル（`ocr.load()`時） |
| 検出・領域分割 | PyTorchとTorchvisionを公式手順で導入後、`python -m pip install --pre 'cv-data-lesson[vision]'` | DETRまたはSAMのモデル（load時） |
| SDXL画像生成・画像変換 | 対応するPyTorchを導入後、`python -m pip install --pre 'cv-data-lesson[diffusion]'` | SDXLと指定LoRA（load時、数GB） |

PyTorchのCPU/CUDA版はOS・CUDA・Pythonで異なります。[PyTorch公式インストーラー](https://pytorch.org/get-started/locally/)で環境に合うPyTorch/Torchvisionを選んでください。`vision` extraはPyTorch本体を含みません。GPUを自動選択することはありません。各機能の`available_devices()`で確認してから`device`を指定します。

## 日本語OCR

PaddlePaddleは環境に合わせた公式wheelが必要です。先に[PaddlePaddle公式インストール案内](https://www.paddlepaddle.org.cn/install/quick)からCPUまたはGPU/CUDA版を選び、その後にOCR extraを追加します。

```bash
python -m pip install --pre 'cv-data-lesson[ocr]'
```

Colab・ローカルでPaddleOCRとPyTorch系を同じ環境に入れる場合の互換性は組み合わせにより異なります。OCR専用の仮想環境に分ける方法をおすすめします。ライブラリが実行中にpip installを行ったり、利用者に`import paddle`を要求したりすることはありません。

## キャッシュと取得

パッケージのインストールだけでは、画像データ・LoRA・基盤モデル重みはダウンロードされません。データは`datasets.get()`、OCRモデルは`ocr.load()`、検出・分割モデルは`vision.load_detector()` / `load_segmenter()`、画像生成モデルは`generation.load()`を呼んだときに取得します。データは既定でリポジトリ外に保存されます。容量と削除方法は[データ取得ガイド](student-guide.md#1-データを選ぶ)を確認してください。

## 動作確認の範囲

インストールできることと、全モデル・全OSで推論が検証済みであることは別です。Colabで実行した機能と実データの範囲は[開発状況](development-progress.md)と各機能ページに記載します。GPUや大容量モデルが必要な機能は、利用可能なGPUと空き容量を先に確認してください。
