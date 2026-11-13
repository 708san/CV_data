# インストールと依存関係

更新日：2026-11-13

PyPI公開前の開発版です。次の依存構成は機能単位で分けています。基本のデータ一覧・説明・固定Release取得には追加パッケージを使いません。データ本体・モデル重みもインストール時には取得しません。

## Python

パッケージメタデータ上の対象はPython 3.11〜3.13です。3.10はDiffusersなど一部AI依存の現在の対応範囲と揃いにくいため、初期公開では対象外にします。3.14以降は依存組み合わせの確認後に追加します。

## 目的から選ぶ

PyPIにはまだ公開していません。以下のコマンドは、このリポジトリをcloneしてルートフォルダで実行する開発版向けです。PyTorchやPaddlePaddleのCPU/GPU用wheelは環境によって異なるため、該当機能のリンク先で先に選びます。

| やりたいこと | 追加するもの | 手順 |
|---|---|---|
| データ一覧・取得 | 追加依存なし | `python -m pip install -e .` |
| DataFrameでラベルを確認、画像や結果を表示 | `dataframe`, `display` | `python -m pip install -e '.[dataframe,display]'` |
| ResNetで分類・回帰 | 公式PyTorch/Torchvision、`torch` | 公式サイトでCPU/GPU版を選んでから `python -m pip install -e '.[torch]'` |
| OCR | 環境に合うPaddlePaddle、`ocr` | PaddlePaddleを先に入れてから `python -m pip install -e '.[ocr]'`。PyTorch系とは別環境を推奨 |
| 検出・領域分割 | 公式PyTorch/Torchvision、`vision` | PyTorchを先に入れてから `python -m pip install -e '.[vision]'` |
| SDXL画像生成・画像変換 | 公式PyTorch/Torchvision、`diffusion` | GPU環境を確認し、PyTorchを先に入れてから `python -m pip install -e '.[diffusion]'` |

機能を一括で入れるextraはありません。ColabではランタイムのCPU/GPUを選んでから導入してください。GPUを使う場合も自動切替はせず、各APIの`available_devices()`で確認してから`device`を指定します。詳細なOS・CUDA・依存条件は以下の機能別案内にまとめています。

## 機能別インストール

リポジトリを取得した開発者は、以下の`pip install -e`を使います。PyPI公開後は`-e .`を`cv-data-lesson`へ置き換える予定です。

| 使う機能 | 追加指定 | 主な追加パッケージ | 注意 |
| --- | --- | --- | --- |
| 開発テスト | `test` | pandas、Pillow | 開発・CI専用。PyTorchなど大容量依存は含めない |
| データ一覧・説明・取得 | なし | なし（Python標準ライブラリ） | `import cvlesson`や一覧表示だけではデータ・モデルを取得しない |
| DataFrame | `dataframe` | pandas | `to_df()`を使うときだけ必要 |
| 画像表示・監査 | `display` | NumPy、Pillow、pandas、Matplotlib 3.6以上、japanize-matplotlib 1.1.3以上 | 画像サンプル表示とライブラリ内の日本語タイトル表示に必要 |
| ResNet分類・回帰 | `torch` | NumPy、Pillow、PyTorch、Torchvision | ResNet重みは初回利用時に別途取得。TorchとTorchvisionは公式の対応組み合わせで導入する |
| 日本語OCR | `ocr` | PaddleOCR 3.1.0、PaddleX 3.1系、Pillow、LangChain 1.0未満、Hugging Face Hub | PaddlePaddle本体はCPU/GPU環境に合わせ別途導入。OCR専用環境を推奨 |
| 物体検出・領域分割 | `vision` | NumPy、Pillow、Transformers、Hugging Face Hub（1.x対応） | PyTorchを先に導入。初回の明示読み込み時にDETR約167 MBまたはSAMの重み約375 MBを取得 |
| SDXL生成・画像変換 | `diffusion` | Pillow、Diffusers（Torch extraを含む）、Transformers、Hugging Face Hub | 初回利用時に基盤モデルと選択LoRAを取得。数GBの空き容量が必要 |

Hugging Face系の役割は分かれています。**Hugging Face Hub**はモデル・LoRAの取得とキャッシュ、**Transformers**はモデル構成や関連部品、**Diffusers**は画像生成パイプラインを担当します。Hub用パッケージだけ、または3つ全部を基本依存へ入れる構成にはしません。画像例のタイトル・ラベルは`japanize-matplotlib`を通じて日本語フォントへ設定します。ライブラリのimportだけでは読み込まず、`show_examples()`の実行時に適用します。

```bash
python -m pip install -e .
python -m pip install -e '.[test]'
python -m pip install -e '.[dataframe]'
python -m pip install -e '.[display]'
python -m pip install -e '.[torch]'
python -m pip install -e '.[ocr]'
python -m pip install -e '.[vision]'
python -m pip install -e '.[diffusion]'
```

`vision` extraはPyTorch本体を含みません。まず[PyTorch公式インストーラー](https://pytorch.org/get-started/locally/)からCPU/GPU環境に合うPyTorchを導入し、その後にextraを追加してください。モデル取得先は固定revisionです。既定モデル・ライセンス表示・使える範囲は[検出と領域分割](vision.md)を確認してください。

### OCR用の環境

OCRを使うときだけ、PaddlePaddleと`ocr` extraを導入します。ResNet・SDXLのPyTorchとは別の仮想環境に分けると、深層学習基盤の依存競合を避けやすくなります。まず[PaddlePaddle公式インストール案内](https://www.paddlepaddle.org.cn/install/quick)でOS・Python・CPU/GPU・CUDAに合うPaddlePaddleを導入し、次にこのライブラリの`ocr` extraを入れます。`ocr` extraはPaddleOCR 3.1系に合うPaddleX 3.1系と、旧APIを必要とするPaddleX向けのLangChain 1.0未満を選びます。Hugging Face Hubは1.xも許容し、`requests`はColabとの衝突を避ける範囲に制約します。

```bash
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
python -m pip install -e '.[ocr]'
```

上記はCPU環境の例です。GPU環境では公式インストーラーで対応するCUDA版を選び、Colabでも現在のCUDA環境に一致するコマンドを選んでください。PaddlePaddle本体は環境ごとにwheelが異なるため、ライブラリが実行中に自動インストールすることはありません。利用者が`import paddle`を書く必要はなく、`ocr.load()`が必要な時にライブラリ内部で読み込みます。`ocr.load()`の既定はCPUです。GPUを使うときは`device="gpu:0"`を指定し、`ocr.available_devices()`で利用可否を先に確認します。

OCRモデルは`ocr.load()`を呼んだ時に、Apache-2.0表示のPP-OCRv5 mobile検出・認識モデルを固定Hugging Face revisionから取得します。2モデルで約22 MBです。モデルカードの条件は各配布元で確認できます：[検出モデル](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det)、[認識モデル](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_rec)。推論はローカルで実行し、読み取り結果は`text`と行ごとの`confidence`、画像上の四点`polygon`で返します。

Colabで以前のOCR依存を導入済みの場合は、修正版をインストールした後にランタイムを再起動してください。`No module named 'langchain.docstore'`はPaddleOCR未導入ではなく、PaddleX 3.1系とLangChain 1.xの互換性問題です。新しい`ocr` extraはLangChainを1.0未満に制約します。

## PyTorchとCPU/GPU

PyTorchとTorchvisionは機能上対応する版の組み合わせを使います。PyPI extrasはCUDA版を選べないため、GPU利用者は先に[PyTorch公式インストーラー](https://pytorch.org/get-started/locally/)でOS・Python・CUDAまたはCPUを選んでPyTorchとTorchvisionを導入し、その後に`.[torch]`または`.[diffusion]`を追加します。extrasのインストールは既に満たされたPyTorchを再選択しない前提です。GPUの有無はライブラリ側でも明示的に確認し、GPUへ自動切替しません。

現行の公式対応表に基づく最小候補は次のとおりです。`pyproject.toml`の下限は2.6/0.21とし、Python 3.13ではresolverが対応する新しい組を選べるようにします。これはwheelを各OS/GPUで実行確認済みという意味ではありません。

| Python | PyTorch/Torchvision最小候補 | 状態 |
| --- | --- | --- |
| 3.11 | 2.6 / 0.21 | 公式対応表に記載。CPU動作確認は未実施 |
| 3.12 | 2.6 / 0.21 | 公式対応表に記載。CPU動作確認は未実施 |
| 3.13 | 2.7 / 0.22 | 公式対応表に記載。依存resolverとCPU動作確認は未実施 |

```bash
# 先にPyTorch公式サイトで選んだコマンドを実行
python -m pip install -e '.[torch]'
```

インストール済みPyTorchの版、CPU/CUDA/MPSの認識を確認します。

```python
import torch
import torchvision

print(torch.__version__, torchvision.__version__)
print("CUDA:", torch.cuda.is_available())
print("MPS:", torch.backends.mps.is_available())
```

## バージョン・動作確認の範囲

`pyproject.toml`には依存の許容範囲を記載しますが、これは全組み合わせの実機検証を意味しません。開発時は確認したバージョン組み合わせを別途記録します。重量級パッケージの解決・実行は別計算機のCI runnerまたはColabで行います。別計算機を使えない場合は保留します。同じPC上の一時仮想環境はパッケージを分けるだけで、CPU・メモリ・ディスクを分離しません。CUDA/T4など実GPUが必要な確認はColabで行い、GPU未確認の機能をGPU動作確認済みとは案内しません。

## 現在の制限

- OCRはColab Python 3.13のCPUランタイムで、PaddlePaddle 3.2.0・PaddleOCR 3.1.0・PaddleX 3.1.4を導入し、合成した英数字画像の推論と共通戻り値を確認しました。日本語実画像の認識品質、GPU、他OS・他バージョンの組み合わせは未確認です。
- 検出・領域分割はColab Python 3.13のT4でDETRとSAMの固定モデルを取得・推論し、検出結果、SAMのboolマスクと重ね合わせ表示を確認しました。確認はNotebook内の合成図形画像1枚です。実データでの精度、CPU・他OS・他GPUは未確認です。
- OCRがPaddlePaddleなど別の深層学習基盤を必要とする場合、PyTorch系との同一環境での併用は未確認です。競合しないと確認できるまでは、専用仮想環境へ分ける導入例を優先します。機能を全部入れる`all` extraは設けません。
- ResNetの実データ分類・回帰、OCRの公開実レシート推論、SAMの実データ比較を行うColab Notebookを用意しましたが、今回追加した各フローはまだColabで実行していません。Notebookの構文確認とAPIのネットワーク不要テストだけを完了しています。
- 依存範囲の実環境チェックは開発中です。ResNetの既存CPU動作確認はPyTorch 2.2.2/Torchvision 0.17.2で行ったため、更新した推奨下限（PyTorch 2.6/Torchvision 0.21）での再確認が残っています。

## 公式情報

- [PyTorchのインストール選択](https://pytorch.org/get-started/locally/)
- [PyTorchとTorchvisionの対応版](https://github.com/pytorch/vision#installation)
- [Diffusersのインストール条件](https://huggingface.co/docs/diffusers/installation)
- [PaddleOCR 3.1.0の推論インストール](https://www.paddleocr.ai/v3.1.0/en/version3.x/installation.html)
- [PaddleOCR 3.1.0 OCR推論API](https://www.paddleocr.ai/v3.1.0/en/version3.x/pipeline_usage/OCR.html)
- [PaddleOCRとPaddleXの対応バージョン](https://www.paddleocr.ai/main/en/version3.x/paddleocr_and_paddlex.html)
