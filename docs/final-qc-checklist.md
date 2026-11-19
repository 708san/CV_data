# 最終QCチェック表

対象ブランチ：`codex/library-ocr-runtime`

対象コミット：自動切替実装 `f5034d2845401198fc4b5de88b7dbf12afdc7d47`、受け入れNotebook `8a3ad64`

この表は、ライブラリの修正・固定artifact・Colab実機確認・配布物検査を分けて記録する。PyPI公開、Release作成、`main`へのマージはこの表の確認だけでは実行しない。

| 確認項目 | 受け入れ条件 | 状態 | 証拠・備考 |
|---|---|---|---|
| GeoSetEnnea取得 | 固定SHA-256を検証し、`datasets.get("geoset_ennea")`が完了する | 完了 | 136件を一時領域で全量検証。CPU/T4 Notebookでも取得成功 |
| RDD2020取得 | 固定SHA-256を検証し、7,900件・16,469 bboxを検証する | 完了 | 7,900件、16,469 bboxを一時領域で全量検証。CPU/T4 Notebookでも確認 |
| `val` / `valid` | 両方を受け付け、集計プロパティは`valid`、DataFrameの`split`は元表記を保持する | 完了 | GeoSetEnneaは`val`、RDD2020は`valid`を保持 |
| bbox | 有限値で、極小のシリアライズ丸め誤差を除き画像範囲内 | 完了 | RDD2020全16,469 bboxで確認 |
| 日本語ラベル | 元ラベルを保持し、日本語ラベルを併記する | 完了 | Orange、FruitSeg30、Indoor Waste、Fire、Fresh/Rotten、AgriFreshNETを確認 |
| `timm` | `vision` extraから導入できる | 完了 | `pyproject.toml`と依存関係テストで確認 |
| device別名・自動切替 | `cuda` / `cuda:0`を機能間で一貫して扱い、既定`auto`はGPU優先・なければ警告付きCPU | 部分完了 | 実装とネットワーク不要テスト完了。CPU/T4の新Notebook実行待ち |
| ResNet | CPU/T4で分類・回帰、進捗表示、特徴再利用、`auto`切替が動作する | 部分完了 | 既存T4実行と単体テスト完了。新`auto`実モデル実行待ち |
| DETR / SAM | CPU/T4で固定revisionの読み込みと推論が完了する | 部分完了 | 既存T4実行完了。CPUの同一固定モデル実行と`auto`実行待ち |
| 画像生成 | GPUではSDXL、CPUではTiny-SDを使い、Tiny-SDのLoRA/image-to-image拒否が明確 | 部分完了 | 既存T4のSDXL完了。Tiny-SD CPU実生成と新`auto`Notebook実行待ち |
| OCR | PNG/JPEG/WebP/Pillow Image、壊れた画像、日本語実画像、`auto`切替を確認する | 部分完了 | CPU Notebookで既存経路は完了。`auto`確認セルの再実行待ち |
| ネットワーク不要テスト | 指定テストが対応Pythonで成功する | 完了 | Python 3.13で92件OK、任意依存不足による18件skip |
| Notebook静的検査 | JSON、セル依存、固定SHA、pip引用符を検査する | 完了 | `tests.test_notebook_integrity` 3件OK。`auto_device_model_acceptance_test.ipynb`を追加 |
| wheel / sdist | 現在のHEADからbuildし、metadata検査とwheelインストールを完了する | 完了 | `cv_data_lesson-0.1.0a1-py3-none-any.whl`（75,676 bytes、SHA-256 `bf7b18d27a722e773f4b36c76f981c3257bb6206a03746b9bde04d8867d3501c`）とsdist（89,097 bytes、SHA-256 `f124373b8f9d0e30b3de8c6b9268b2c9ddc55c7b0a04c523ca9a0759ddbccd29`）をtwine check・依存なしwheel install・importで確認 |
| PyPI / Release / main | 明示的許可後にのみ公開・マージする | 保留 | 今回は実行しない |

## 環境上の注意

- OCR専用Colabでは、Colab既存のLangGraph・Requestsと依存関係警告が出る場合がある。OCR推論は完了済みであり、他のLangGraph機能との同居を保証するものではない。
- Hugging Face未認証警告は、公開モデルの取得失敗を示すものではない。レート制限を避ける場合だけ`HF_TOKEN`を設定する。
- `ccache`、Transformers、Diffusersの`FutureWarning`は今回のライブラリAPIの失敗ではない。
