# 利用者向け導入・実使用の監査

確認日：2026-11-13
対象：PyPI `cv-data-lesson==0.1.0a4`、GitHub `main`（`9f1c8142d3688ed5d817a8a9835735657f0ddefb`）、公開Notebookと主要利用ガイド。

## GitHubとPyPIの表示差は問題か

配布名`cv-data-lesson`、import名`cvlesson`、日本語の表示名「CV教材ライブラリ」は役割が違うため、名前自体が異なることはPythonでは通常の設計です。PyPIは`pyproject.toml`のproject名・version・summaryを表示し、READMEを公開時点の内容として表示します。GitHubのREADMEは`main`が更新されるたびに変わります。そのため公開直後から文面が違うこと自体は異常ではありません。

ただし、最新PyPI READMEからGitHub `main`へ移動したとき、導入方法・機能・利用条件がインストール済み版と違えば実用上の問題です。PyPI側の説明が古いまま残る、PyPIリンク先が先行開発中の`main`を表示する、といったずれは初心者を混乱させます。リリースごとにPyPI READMEとmetadata、バージョン対応文書、GitHubの説明を照合する必要があります。

## 問題一覧

| 優先度 | 問題 | 根拠と利用者への影響 | 改善方針 |
|---|---|---|---|
| 高 | 使用ガイドと実際の依存が不一致 | 基本installはpandas・Pillow・Matplotlibを含むが、ガイド冒頭は`to_df()`に`dataframe`、画像表示に`display`の追加導入が必要としている。不要なextra追加や「動かない」という誤解につながる。 | 基本installと機能extra表を正本にそろえ、古い補足コメントを更新。 |
| 高 | 機能別extraの導入動作が不統一 | `torch` extraはTorch/Torchvisionを入れ、`diffusion`は`diffusers[torch]`経由でTorchを依存に含む。一方`vision`はTorch/Torchvisionを含まず、モデル実行に別installを求める。 | `vision`にもTorch/Torchvisionを含める。GPU用wheelを先に選ぶ場合だけ公式手順を案内。 |
| 高 | 画像生成でTorchが必要か分かりにくい | 現行`diffusion` extraは既にTorchを入れるのに、インストール案内は先にPyTorchを入れるよう読み取れる。二重導入やColabでの不要な環境変更を心配させる。 | クリーン環境用の一回installを先に示す。Colab/独自CUDA環境は既存Torchの版を確認し、必要な場合だけ公式版を選ぶ手順を別枠にする。 |
| 高 | Colab NotebookがPyPI配布物を試していない | 生成・分類/回帰・OCR・検出Notebookが別々のGit commitを直接installする。PyPIへ上がったwheelとNotebookが使うコードが違っていても気づけない。 | Notebookはテスト対象版のPyPI packageをinstallする。開発コードの確認は別の開発者用workflowとして扱う。 |
| 高 | OCR Notebookに同じパッケージの重複導入がある | OCR Notebookでextra付きinstall後、同じcheckoutを`--force-reinstall --no-deps`でもう一度入れている。古いColab環境に対する一時回避が恒久導線へ残っている。 | fresh runtimeで必要なPaddlePaddleとPyPI extraを一度ずつ入れる。 |
| 中 | PyPIの詳細リンク先が固定されない | GitHub `main`はPyPI公開後も変わるため、利用者が別版の手順を読んでしまう可能性がある。 | PyPIからの主要文書リンクはリリースタグの文書へ向け、READMEに対応版を明記。次回Release時にリンク版を更新。 |
| 中 | 名前の対応が一目で分からない | PyPI page title、GitHub repository名、pip名、Python import名、日本語表示名が異なる。個々は正当でも、コピーする名前を間違えやすい。 | READMEと導入文書の先頭に「配布名 / import名 / 表示名」を並べる。 |
| 中 | Colabの全機能検証の道順がない | 個別Notebookは存在するが、CPU OCRとT4向けPyTorch/SDXLをどの順に、何のランタイムで試すか一覧化されていない。一つのランタイムに混ぜると依存競合や容量問題が起きる。 | 実行順、ランタイム、確認内容、所要容量、結果記録欄を持つColabチェックリストを追加。CPU OCRとT4は別ランタイム。 |
| 中 | 画像入力例をそのまま実行できない | ガイドに`street.jpg`のような未定義の例示パスがある。初心者は画像をどこから準備するか分からずFileNotFoundErrorになる。 | アップロード済みパスの作り方をガイドの直前に置くか、データから得た実在パスをコード例に使う。 |
| 低 | alpha版`--pre`が必要な理由を毎回読み替える | pipの既定ではpre-releaseを選ばないため`--pre`が必要だが、コマンドが機能別文書に散ると版やupgradeの挙動で迷う。 | 先頭に一度だけ理由と基本コマンドを書き、表は同じ規則を使う。既存インストール更新用コマンドも記載。 |
| 低 | extras名が利用者のやりたいことから想像しにくい | `vision`、`diffusion`など内部実装名だけではどれを選ぶべきかすぐ分からない。 | 表の左に「分類/回帰」「検出/分割」「画像生成」と目的を書く。extra名はコマンド内で説明する。 |

## 導入方針の判断

- **画像生成**：PyPIの`diffusion` extraは`diffusers[torch]`を含むため、Torchの別installは通常不要。Hugging Face公式Diffusers案内も`diffusers[torch]`がPyTorchとAccelerateを入れると説明している。ただしColabやCUDA環境では既存TorchやGPU wheelを優先する。パッケージが実行中にpipを動かすことはしない。
- **ResNet**：`torch` extraがTorch/Torchvisionを含むため、通常環境なら一度のinstallで足りる。独自CUDA wheelを選ぶ場合はPyTorch公式selectorを先に使う。
- **検出/領域分割**：現在の`vision` extraはTorchを含まないため、初心者向けには不統一。次alphaからTorch/Torchvisionもextraに含め、環境に合う既存インストールはpipに再利用させる。CUDA版を手動で選ぶ導線も残す。
- **OCR**：PaddlePaddleはOS・CPU/GPU・CUDAごとの配布wheelを選ぶ必要がある。利用時だけ環境に適したPaddlePaddleを別導入する設計を維持し、理由を短く説明する。
- **基本データ利用**：データ本体やモデル重みはinstall時に取得しない。データは`datasets.get()`、モデルは用途別`load()`で明示取得する。

## 情報源

- このリポジトリの`README.md`、`pyproject.toml`、`docs/installation.md`、`docs/student-guide.md`、`docs/quickstart.md`、`notebooks/colab/*.ipynb`（2026-11-13に確認）
- [PyPI cv-data-lesson 0.1.0a4](https://pypi.org/project/cv-data-lesson/0.1.0a4/)
- [Hugging Face Diffusers installation guide](https://huggingface.co/docs/diffusers/installation)（`diffusers[torch]`の依存内容を確認）
- [PyTorch公式インストーラー](https://pytorch.org/get-started/locally/)（OS・GPU別のwheel選択）
