# 開発進捗

## 2026-11-05：共通APIと分割・監査の土台

### 変更目的

- 固定Release取得を、英語IDと登録済み日本語名の完全一致で呼び出せるようにする。
- 分類データのパス・ラベル・日本語ラベル・クラス番号・分割を共通DataFrameへそろえる。
- 公式testを保持し、trainから再現可能なvalを作る。
- CPUで利用できる遅延読み込みのPyTorch Datasetと、機械可読な品質監査項目を用意する。

### 実装結果

- `DatasetBundle.to_df()`、`show_examples()`、`to_torch_dataset()`を追加。
- `classes`、`class_names_ja`、`splits`、`license_info`、`source_info`を追加。
- 日本語名は登録済み別名の完全一致だけを受け付け、曖昧な推測はしない。
- train/val分割はseed `42`、クラス別、公式test保持で固定。
- 取得失敗時は最大3回まで再試行し、既存のSHA-256・サイズ・安全なZIP展開を維持。
- 監査JSONに、元画像数・使用可能数・クラス数・分割数・破損数・完全一致重複候補・ラベル不一致・除外理由・分割方法・漏洩リスク・検証日時を追加。
- `CV_sample_data`、Release、既存Notebookは変更していない。

### festival_iconsの実体監査結果

- 固定ZIP：2,838,163 bytes、SHA-256一致。
- 画像168枚を全量デコードし、破損0枚、キャプション欠損0件。
- 完全一致重複候補0件、ラベル不一致0件。
- 8×8平均ハッシュで類似候補417組を抽出したが、レビュー用であり重複確定・自動削除はしていない。権利審査は未実施。LoRA素材のため分類用splitは作成していない。
- 詳細：[festival-icons-v1.0.0.json](../reports/festival-icons-v1.0.0.json)

### tomato_leavesの実体監査結果

- 固定ZIP：124,334,101 bytes、SHA-256一致。
- 画像7,209枚を全量デコードし、破損0枚、完全一致重複候補0件、ラベル不一致0件。
- 元の分割はtrain 5,768枚・test 1,441枚。標準化後はtrain 5,191枚・val 577枚・test 1,441枚。
- 8×8平均ハッシュで類似候補14,571組を抽出したが、レビュー用であり重複確定・自動削除はしていない。同一個体・撮影系列のグループ分離と権利審査は未実施。
- 詳細：[tomato-leaves-v1.2.0.json](../reports/tomato-leaves-v1.2.0.json)

### Fashion-MNISTのプレビュー整備

- 公式GitHubの固定コミット`b2617bb6d3ffa2e429640350f613e3291e10b141`を使用。
- 4つのIDX gzipをSHA-256・ヘッダー・件数まで検査し、PGMキャッシュへの変換を確認。
- 標準化後はtrain 54,000 / val 6,000 / test 10,000。
- MIT表記は確認済みだが、教材公開・再配布の最終確認中。正式一覧には未掲載。
- 詳細：[fashion-mnist-github-b2617bb6.json](../reports/fashion-mnist-github-b2617bb6.json)

### CV分類Notebookの新設

- LLM講座の基準Notebookは変更せず、CV分類用の[新Notebook](../notebooks/cv/classification_v1.ipynb)を追加。
- トマトの葉の出典確認、DataFrame、画像例、train/val/test、CPU向け小型CNN、テスト記録、振り返りを含めた。
- Fashion-MNISTとKuzushiji-MNISTは権利・公開状態の理由から生徒向けNotebookには含めていない。

### 検証条件と結果

- オフラインの標準テスト：Python 3.9環境で19件中19件成功（Pillow未導入による2件のskip）。
- Python 3.10環境で19件中19件成功（pandas未導入による1件のskip）。
- `compileall`で`src`と`tests`を検査済み。
- 固定Releaseの全量画像監査を実施済み。取得と画像検査は通常のネットワーク不要テストから分離している。

### 未完了・保留

- `registry/candidates_50_unreviewed.json`は未承認候補のまま。Fashion-MNISTのプレビュー以外は正式APIへ追加していない。
- Kuzushiji-MNISTはライセンス表記を確認したが、公式データファイルの固定版とSHA-256が不足するため保留中。
- 詳細：[kuzushiji_mnist.md](datasets/kuzushiji_mnist.md)
- `festival_icons`はLoRA学習素材としてのみ扱い、分類データや一般的なオープンライセンスとして扱わない。
- CV分類Notebookは新規作成済み。PyTorchを含む実Colab検証と、次の検出・分割Notebookは次の課題。

### データ・LoRA選択基盤

- `datasets.list_preview()`で権利確認中の教師向けデータを正式一覧から分離。
- Fashion-MNISTは固定IDXファイルを検証済みのプレビューとして管理。
- `cvlesson.loras`を追加し、素材・キャプション・トリガーワード・基盤モデル・権利状態を管理。
- 承認済みLoRAがないため、`loras.list_available()`は空。文化祭アイコンは明示的なプレビュー取得のみ。

### 2026-11-05：課題選択カタログと候補精査

- `datasets.list_available(task=..., audience=..., include_preview=...)`を追加し、課題タイプ・対象者・プレビュー状態で候補を絞れるようにした。
- `datasets.list_tasks()`を追加し、生徒が選べる課題タイプとデータIDを一覧化した。未承認の検出・分割候補は表示しない。
- `DatasetBundle`に課題タイプ、対象者、用途、入力・出力、概算取得サイズを追加した。
- `docs/catalog-review.md`に50候補を分類・検出・分割・素材の課題へ対応付け、全候補をAPIへ追加しない理由と次の実体検査順を記録した。
- `Fruits-360`、`Recyclable Waste`、`GeoSetEnnea`、`FruitSeg30`は公式ページでライセンス表記と概要を再確認した。GeoSetEnneaは公式APIのフォルダ別メタデータを追加確認し、画像966件・YOLOラベル966件と別置きのaugmented/rawを記録したが、固定アーカイブSHA-256と実体監査が未完了のため、台帳は`under_review`・公開保留のままにした。
- PyPI向けのパッケージビルドを行うが、本番公開・Release作成・mainへのマージは行わない。
