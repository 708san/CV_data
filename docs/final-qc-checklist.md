# 最終QCチェック表

対象ブランチ：`codex/library-ocr-runtime`

対象HEAD：`d820588d8302568cddb51d54eebe5b0c86b45953`

この表は、ライブラリの修正・固定artifact・Colab実機確認・配布物検査を分けて記録する。PyPI公開、Release作成、`main`へのマージはこの表の確認だけでは実行しない。

| 確認項目 | 受け入れ条件 | 状態 | 証拠・備考 |
|---|---|---|---|
| GeoSetEnnea取得 | 固定SHA-256を検証し、`datasets.get("geoset_ennea")`が完了する | 完了 | 136件を一時領域で全量検証。CPU/T4 Notebookでも取得成功 |
| RDD2020取得 | 固定SHA-256を検証し、7,900件・16,469 bboxを検証する | 完了 | 7,900件、16,469 bboxを一時領域で全量検証。CPU/T4 Notebookでも確認 |
| `val` / `valid` | 両方を受け付け、集計プロパティは`valid`、DataFrameの`split`は元表記を保持する | 完了 | GeoSetEnneaは`val`、RDD2020は`valid`を保持 |
| bbox | 有限値で、極小のシリアライズ丸め誤差を除き画像範囲内 | 完了 | RDD2020全16,469 bboxで確認 |
| 日本語ラベル | 元ラベルを保持し、日本語ラベルを併記する | 完了 | Orange、FruitSeg30、Indoor Waste、Fire、Fresh/Rotten、AgriFreshNETを確認 |
| `timm` | `vision` extraから導入できる | 完了 | `pyproject.toml`と依存関係テストで確認 |
| device別名 | `cuda` / `cuda:0`を機能間で一貫して扱う | 完了 | CPU/T4 Notebook、T4実モデルで確認 |
| ResNet | CPU/T4で分類・回帰、進捗表示、特徴再利用が動作する | 完了 | T4 Notebookで分類・回帰を実行 |
| DETR / SAM | T4で固定revisionの読み込みと推論が完了する | 完了 | T4 Notebookで実行。DETR検出0件は白い合成画像の結果 |
| 画像生成 | SDXLはGPUで動作し、CPUでは明確に拒否する | 完了 | CPU境界とT4の512×512生成を確認 |
| OCR | PNG/JPEG/WebP/Pillow Image、壊れた画像、日本語実画像を確認する | 完了 | CPU NotebookでWebP 1行、壊れた画像は`OCRError`、実レシート推論完了 |
| ネットワーク不要テスト | 指定テストが対応Pythonで成功する | 完了 | Python 3.13で90件OK、任意依存不足による18件skip |
| Notebook静的検査 | JSON、セル依存、固定SHA、pip引用符を検査する | 完了 | `tests.test_notebook_integrity` 3件OK |
| wheel / sdist | 現在のHEADからbuildし、metadata検査とwheelインストールを完了する | 完了 | `cv_data_lesson-0.1.0a1-py3-none-any.whl`（75,676 bytes、SHA-256 `bf7b18d27a722e773f4b36c76f981c3257bb6206a03746b9bde04d8867d3501c`）とsdist（89,097 bytes、SHA-256 `f124373b8f9d0e30b3de8c6b9268b2c9ddc55c7b0a04c523ca9a0759ddbccd29`）をtwine check・依存なしwheel install・importで確認 |
| PyPI / Release / main | 明示的許可後にのみ公開・マージする | 保留 | 今回は実行しない |

## 環境上の注意

- OCR専用Colabでは、Colab既存のLangGraph・Requestsと依存関係警告が出る場合がある。OCR推論は完了済みであり、他のLangGraph機能との同居を保証するものではない。
- Hugging Face未認証警告は、公開モデルの取得失敗を示すものではない。レート制限を避ける場合だけ`HF_TOKEN`を設定する。
- `ccache`、Transformers、Diffusersの`FutureWarning`は今回のライブラリAPIの失敗ではない。
