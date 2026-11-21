# 最終QCチェック表

対象ブランチ：`codex/library-ocr-runtime`

対象コミット：`v0.1.3`公開時のタグ先頭（0.1.2の監査指摘修正候補）

この表は、ライブラリの修正・固定artifact・Colab実機確認・配布物検査を分けて記録する。PyPI公開、Release作成、`main`へのマージはこの表の確認だけでは実行しない。

| 確認項目 | 受け入れ条件 | 状態 | 証拠・備考 |
|---|---|---|---|
| GeoSetEnnea取得 | 固定SHA-256を検証し、`datasets.get("geoset_ennea")`が完了する | 完了 | 136件を一時領域で全量検証。CPU/T4 Notebookでも取得成功 |
| RDD2020取得 | 固定SHA-256を検証し、7,900件・16,469 bboxを検証する | 完了 | 7,900件、16,469 bboxを一時領域で全量検証。CPU/T4 Notebookでも確認 |
| `val` / `valid` | 両方を受け付け、ライブラリの`split`と集計プロパティは`val`へ統一し、配布元表記は`source_split`へ保持する | 実装完了 | GeoSetEnneaは`val`、RDD2020は`valid`を受け入れ、出力を`val`へ正規化 |
| bbox | 有限値で、極小のシリアライズ丸め誤差だけを許容し、ゼロ幅・NaN・無限大・意味のある範囲外・annotation/YOLO不一致を拒否 | 実装完了 | RDD2020全16,469 bboxの通過と異常artifactの単体テストを追加。公開DataFrameでは境界内へ正規化 |
| 日本語ラベル | 元ラベルを保持し、日本語ラベルを併記する | 完了 | Orange、FruitSeg30、Indoor Waste、Fire、Fresh/Rotten、AgriFreshNETを確認 |
| `timm` | `vision` extraから導入できる | 完了 | `pyproject.toml`と依存関係テストで確認 |
| device別名・自動切替 | PyTorch標準の`cuda`を第1GPUの正規名とし、`cuda:0`を入力別名として受け付け、既定`auto`はGPU優先・なければ警告付きCPU | 実装完了 | 実装、ネットワーク不要テスト、公開版への同梱を確認。CPU/T4実モデルの再実行はColabで別途確認 |
| ResNet | CPU/T4で分類・回帰、進捗表示、特徴再利用、`auto`切替が動作する | 部分完了 | 既存T4実行と単体テスト完了。公開版Colabでの再実行待ち |
| DETR / SAM | CPU/T4で固定revisionの読み込みと推論が完了する | 部分完了 | 既存T4実行完了。公開版ColabでのCPU/T4再実行待ち |
| 画像生成 | GPUではSDXL、CPUではTiny-SDを使い、Tiny-SDのLoRA/image-to-image拒否が明確 | 部分完了 | 既存T4のSDXL完了。公開版ColabでTiny-SD CPU実生成を再確認する |
| OCR | PNG/JPEG/WebP/Pillow Image、壊れた画像、日本語実画像、`auto`切替を確認する | 部分完了 | CPU Notebookで既存経路は完了。公開版OCR専用ランタイムで再確認する |
| ネットワーク不要テスト | 指定テストが対応Pythonで成功する | 実行待ち | 0.1.3候補のテスト実行後に件数を記録 |
| Notebook静的検査 | JSON、セル依存、固定SHA、pip引用符を検査する | 完了 | `tests.test_notebook_integrity` 3件OK。`auto_device_model_acceptance_test.ipynb`を追加 |
| wheel / sdist | `0.1.3`をbuildし、metadata検査・バイナリ混入検査・wheelインストールを完了する | 実行待ち | 0.1.3候補のCIで確認する |
| PyPI通常導入 | `pip install cv-data-lesson`で新しい自動切替APIを取得する | 実行待ち | v0.1.3公開後に一時環境で確認する |
| PyPI / Release | 明示的許可後に公開し、公開版から再検証する | 実行待ち | v0.1.3のRelease公開後にTrusted PublishingとPyPIを確認する |
| `main`へのマージ | ユーザーの明示的許可後にのみ実行する | 保留 | 開発ブランチで公開版を作成。`main`へは直接マージしていない |

## 環境上の注意

- OCR専用Colabでは、Colab既存のLangGraph・Requestsと依存関係警告が出る場合がある。OCR推論は完了済みであり、他のLangGraph機能との同居を保証するものではない。
- Hugging Face未認証警告は、公開モデルの取得失敗を示すものではない。レート制限を避ける場合だけ`HF_TOKEN`を設定する。
- `ccache`、Transformers、Diffusersの`FutureWarning`は今回のライブラリAPIの失敗ではない。
