# インストール案内

このページはPyPIから利用する人向けです。開発用checkoutの手順は含みません。

## 基本環境

Python 3.11〜3.13が対象です。仮想環境の利用をおすすめします。

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
```

この仮想環境には他の作業用パッケージが入っていません。Colabで試す場合は同じ理由で新しいランタイムを使います。

## 基本インストール

alpha版のため`--pre`を付けてください。通常のデータ利用、DataFrame、表・画像例の確認に必要な軽量パッケージは一緒に入ります。

```bash
python -m pip install --pre cv-data-lesson
```

配布名は`cv-data-lesson`、Pythonのimport名は`cvlesson`です。`[display]`や`[dataframe]`は従来コマンドとの互換用に残っていますが、通常は指定不要です。

| 使いたい機能 | インストール・準備 | 実行時に取得するもの |
|---|---|---|
| データ一覧・説明・取得、表・画像例 | 基本インストール | `datasets.get()`を呼んだデータの固定Release ZIP |
| ResNet分類・回帰 | `python -m pip install --pre 'cv-data-lesson[torch]'` | PyTorch依存とResNetの重み |
| 日本語OCR | `python -m pip install --pre 'cv-data-lesson[ocr]'` | OCRモデル（`ocr.load()`時） |
| 検出・領域分割 | `python -m pip install --pre 'cv-data-lesson[vision]'` | PyTorch依存とDETRまたはSAMのモデル（load時） |
| SDXL画像生成・画像変換 | `python -m pip install --pre 'cv-data-lesson[diffusion]'` | PyTorchを含むPython依存、SDXLと指定LoRA（load時、数GB） |

通常のCPU環境では、`torch`・`vision`・`diffusion`のextraが必要なPyTorch/Torchvisionを一緒に導入します。Colabにも通常はPyTorchが入っています。既存環境へextraを追加すると、pipが依存パッケージの版を変更する場合があります。初めて試す場合はColabの新しいランタイムを使い、インストール後に再起動を求められた場合は再起動してください。既存環境を使う場合は実行前にpipの変更内容を確認し、無関係なパッケージを手動で削除しないでください。既に古い`cv-data-lesson`を導入していて更新したい場合に限り、`--upgrade`を明示します。

独自のCUDA版を選ぶ場合だけ、[PyTorch公式インストーラー](https://pytorch.org/get-started/locally/)でOS・Python・CUDAに合うPyTorch/Torchvisionを先に入れ、その後で機能extraを追加します。extraが必要な版条件を満たす既存環境は再利用されます。GPUは自動選択しません。各機能の`available_devices()`で確認してから`device`を指定します。

## 日本語OCR

CPUで使う場合、`ocr` extraにPaddlePaddle CPU版・PaddleOCR・OCRモデル取得用の依存が含まれます。インストール後は`import paddle`を書かず、`from cvlesson import ocr`と`ocr.load()`を使います。

```bash
python -m pip install --pre 'cv-data-lesson[ocr]'
```

GPU版PaddlePaddleを使う場合だけは、[PaddlePaddle公式インストール案内](https://www.paddlepaddle.org.cn/install/quick)からOS/CUDAに合うwheelを選びます。Paddle GPU版の導入手順はCPU版と異なります。

OCRとPyTorch系のextrasを同時に使う場合は、同じ新規仮想環境へまとめて指定できます。Colab Notebookも一つのinstall行で複数extraを選べます。Python 3.11〜3.13の主要な組み合わせはalpha9のリリースCIで依存解決とclean installを確認済みです。OS固有のGPU wheelやColabに事前導入された全パッケージとの組み合わせを保証するものではありません。alpha9には更新した利用者向け文書が含まれています。

```bash
python -m pip install --pre 'cv-data-lesson[ocr,vision,diffusion]'
```

## キャッシュと取得

パッケージのインストールだけでは、画像データ・LoRA・基盤モデル重みはダウンロードされません。データは`datasets.get()`、OCRモデルは`ocr.load()`、検出・分割モデルは`vision.load_detector()` / `load_segmenter()`、画像生成モデルは`generation.load()`を呼んだときに取得します。データは既定でリポジトリ外に保存されます。容量と削除方法は[データ取得ガイド](student-guide.md#1-データを選ぶ)を確認してください。

## 動作確認の範囲

インストールできることと、全モデル・全OSで推論が検証済みであることは別です。Colabで実行した機能と実データの範囲は[開発状況](development-progress.md)と各機能ページに記載します。GPUや大容量モデルが必要な機能は、利用可能なGPUと空き容量を先に確認してください。

全機能のColab確認に使うNotebook、ランタイム、実行順、記録方法は[Colab実機確認ガイド](colab-verification.md)をご覧ください。

公開メソッドの引数・既定値・戻り値・制約は[APIリファレンス](api-reference.md)にまとめています。Colabではinstallセルを実行した後、Notebookに再起動案内が出た場合はランタイムを再起動し、importセルから順に再実行してください。
