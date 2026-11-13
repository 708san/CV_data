# 公開版をColabで確認する

この手順は、GitHub上の開発コードではなく、PyPIから公開された同じ版のwheelを動かすためのチェックリストです。確認対象の`cv-data-lesson==0.1.0a5`はPyPIで公開済みで、Python 3.13の軽量なクリーン環境では導入・カタログ一覧・依存整合性を確認しました。以下のデータ取得とモデル推論は、Colabでの実行がまだ必要です。

## 実行前

1. 下のNotebookリンクを開き、自分のGoogle Driveへコピーします。
2. 各Notebookの先頭にある `%pip install` 行が`0.1.0a5`を指定していることを確認します。これはPyPIで公開済みの版です。
3. OCRとPyTorch系は別ランタイムで試します。OCRはPaddlePaddleのCPU環境、分類・回帰・検出・領域分割・生成はPyTorch環境を使います。依存を入れ替えながら一つのランタイムで連続実行しないでください。
4. 画像データ・モデル重みを初回に取得します。モデル重みはLoRAを含めて数GBになるため、T4を選び、Colabの空きディスクを確認してください。データ・モデルの利用条件はNotebookに表示される説明を読んでください。
5. インストール後にランタイム再起動を求められた場合は再起動し、Notebook先頭から実行します。

## 機能別の確認

| 順番 | Notebook | Colabランタイム | 確認する動作 | 記録 |
|---|---|---|---|---|
| 1 | [分類Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/cv/classification_v1.ipynb) | T4 GPU推奨。CPUでも動くが学習は遅くなる | PyPI install、`tomato_leaves`の取得、表・日本語画像表示、ResNet分類のfit/predict/predict_proba/score | 未実行 |
| 2 | [回帰Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/resnet_regression_smoke_test.ipynb) | T4 GPU推奨 | `lefood_set`の取得、画像ペアのResNetRegressor、validation/test評価 | 未実行 |
| 3 | [日本語OCR Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/ocr_smoke_test.ipynb) | 新しいCPUランタイム | PaddlePaddleと`ocr` extraの導入、OCRモデル取得、文字・信頼度・座標の戻り値、レシート画像推論 | 未実行 |
| 4 | [検出・領域分割Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/vision_smoke_test.ipynb) | T4 GPU | DETR検出、SAMマスク、画像重ね合わせ、FruitSeg30のテスト画像で比較 | 未実行 |
| 5 | [SDXL・LoRA Notebook](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/generation_smoke_test.ipynb) | T4 GPU | PyPI install、text-to-image、image-to-image、登録LoRA4件それぞれのモデル読み込み・生成・保存 | 未実行 |

Colabの実際のGPU名、Python、`cv-data-lesson`の版を記録してください。T4以外で成功した場合も結果を残せますが、「T4実測」とは分けます。失敗した場合は、最後に成功したセル、エラー全文、ランタイム、GPU、`cv-data-lesson`と主要依存の版を控えます。

## 実行結果の記録

| 項目 | 結果 |
|---|---|
| 実行日 | 未実行 |
| Python / cv-data-lesson | 未実行 |
| ランタイム / GPU名 | 未実行 |
| データ取得・表示 | 未実行 |
| 分類・回帰 | 未実行 |
| OCR | 未実行 |
| DETR・SAM | 未実行 |
| SDXL text-to-image / image-to-image / LoRA 4件 | 未実行 |
| 失敗・制約・Colab出力リンク | 未実行 |

NotebookのJSON・Pythonセル構文とPyPI install行をCIでも確認します。それはColabでの実行成功を意味しません。実際の実行ログを確認してから、[開発進捗](development-progress.md)の検証状態を更新します。
