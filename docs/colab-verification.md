# 公開版をColabで確認する

この手順は、GitHub上の開発コードではなく、PyPIから公開された同じ版のwheelをColabで動かすチェックリストです。公開中の安定版は`0.1.0`です。Notebookはこの版を指定しますが、安定版でのColab実機再実行は未確認です。下記の結果は利用者からの実行報告に基づき、報告のない機能は未確認のまま記録します。

## 実行前

1. 下のNotebookリンクを開き、自分のGoogle Driveへコピーします。
2. 各Notebookの先頭にある `%pip install` 行は`0.1.0`を指定しています。安定版を新しいColabランタイムで確認してください。
3. OCR Notebookは`[ocr]`だけでPaddlePaddle CPU版を含めて導入します。OCRとPyTorch系をまとめて使う場合は`[ocr,vision,diffusion]`を一度に指定できます。Colabの既存パッケージと競合した場合は新しいランタイムを作り、機能別に分けてください。
4. 画像データ・モデル重みを初回に取得します。モデル重みはLoRAを含めて数GBになるため、T4を選び、Colabの空きディスクを確認してください。データ・モデルの利用条件はNotebookに表示される説明を読んでください。
5. インストール後にランタイム再起動を求められた場合は再起動し、Notebook先頭から実行します。

## 機能別の確認

| 順番 | Notebook | Colabランタイム | 確認する動作 | 記録 |
|---|---|---|---|---|
| 1 | [分類Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/cv/classification_v1.ipynb) | T4 GPU推奨。CPUでも動くが学習は遅くなる | PyPI install、`tomato_leaves`の取得、表・日本語画像表示、ResNet分類のfit/predict/predict_proba/score | 利用者確認済み。test正解率0.825の報告あり |
| 2 | [回帰Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/resnet_regression_smoke_test.ipynb) | T4 GPU推奨 | `lefood_set`の取得、画像ペアのResNetRegressor、validation/test評価 | 利用者確認済み（正しく動作との報告） |
| 3 | [日本語OCR Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/ocr_smoke_test.ipynb) | 新しいCPUランタイム | `ocr` extraによるPaddlePaddle CPU版とOCR依存の導入、OCRモデル取得、文字・信頼度・座標の戻り値、レシート画像推論 | OCR推論・戻り値とalpha8の全文＋折りたたみ詳細はColabで利用者確認済み。alpha9では未実行（GPU・Python版は未報告） |
| 4 | [検出・領域分割Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/vision_smoke_test.ipynb) | T4 GPU | DETR検出、SAMマスク、画像重ね合わせ、FruitSeg30のテスト画像で比較、Chromeでポップアップ画像アップロード | 利用者確認済み。DETR/SAM動作、マスク画像の単一表示、Chromeアップロードを確認 |
| 5 | [SDXL・LoRA Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/generation_smoke_test.ipynb) | T4 GPU | PyPI install、text-to-image、image-to-image、選択したLoRA1件の読み込み・生成・保存 | LoRA生成とImage-to-Imageは利用者確認済み。LoRA ID・GPU等は未報告 |

Colabの実際のGPU名、Python、`cv-data-lesson`の版を記録してください。T4以外で成功した場合も結果を残せますが、「T4実測」とは分けます。失敗した場合は、最後に成功したセル、エラー全文、ランタイム、GPU、`cv-data-lesson`と主要依存の版を控えます。

## 実行結果の記録

利用者から共有されたColab実行結果を記録します。機能ごとの確認報告は複数回に分かれており、実行日時・Python版・GPU名が特定できない場合は補完せず「未報告」とします。

| 項目 | 結果 |
|---|---|
| 実行日 | 個別の実行日時は未報告（確認報告日：2026-11-14） |
| 実行環境 / Python / cv-data-lesson | すべてColab。Python版とライブラリ版は未報告 |
| ランタイム / GPU名 | Colab。GPU名は未報告（T4実測としては記録しない） |
| 分類 | 確認済み。test正解率0.825との報告 |
| 回帰 | 確認済み。正しく動作との報告 |
| OCR推論・戻り値・表示 | OCR推論の`TOTAL 1280 JPY`（confidence 0.993）と、alpha8の全文優先表示を利用者確認済み。安定版の再実行なし。実行環境詳細は未報告 |
| DETR・SAM | 確認済み。SAMマスク表示は1枚、Chromeのポップアップアップロードも確認 |
| LoRA生成 / Image-to-Image | 利用者がColabで両方の動作を確認。LoRA ID・GPUなど実行条件は未報告 |
| 失敗・制約・Colab出力リンク | 上記の確認済み事項以外は未報告 |

NotebookのJSON・Pythonセル構文とPyPI install行をCIでも確認します。それはColabでの実行成功を意味しません。実際の実行ログを確認してから、[開発進捗](development-progress.md)の検証状態を更新します。
