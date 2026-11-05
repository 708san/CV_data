# Codexへの次の依頼：CV_data 初期導入と固定Releaseの実機確認

## 対象と禁止事項

- **変更してよいのは `708san/CV_data` のみ**。`708san/CV_sample_data`は完全な読み取り専用。ブランチ・タグ・Release・README・配布物・スクリプトなど、すべて変更禁止。`CV_sample_data`でのIssue作成も禁止。
- このパッケージに入っているスターターの構成と`AGENTS.md`を読み、`CV_data`の作業ブランチへ導入する。
- `CV_data`の`main`へ直接コミット・マージしない。変更案をPR（Pull Request：変更提案）にする。
- PyPI公開、GitHub Releaseの新設、元画像の再配布、Notebook本文の書き換えは禁止。

## 作業順

1. GitHubの`708san/CV_data`が空であることを確認し、既存ファイルがある場合は競合を報告してから編集する。
2. スターターの`src/`、`tests/`、`docs/`、`AGENTS.md`、`pyproject.toml`、`registry/`などを作業ブランチに配置。
3. `python -m unittest discover -s tests -v`でネットワーク不要の8テストを実行。失敗する場合は原因と修正内容を報告する。
4. `python -m pip install -e .`のインストールと、READMEのコード例を確認する。
5. **読み取りのみ**で`CV_sample_data`の2つの固定Release、アセット名、サイズ、SHA-256を確認する。
   - `tomato-v1.2.0`、`tomato-leaves.zip`
   - `festival-v1.0.0`、`festival-icons.zip`
6. 小さな文化祭アイコンのRelease（約2.8MB）について、実際のダウンロード→ハッシュ照合→展開→`manifest.json`・`labels.csv`・`metadata.jsonl`の整合性を実機で確認。元リポジトリは絶対に変更しない。
7. トマトの葉は約124MBなので、必要な容量と通信条件を確認したうえで実機検査する。テスト不能な場合は未検証として報告。
8. `CV_data`への変更を小さなPRに整理し、テスト・実機結果と未検証事項を記載。マージは利用者の承認後。

## 特に確認すること

- 固定版・画像数・ZIPのSHA-256が元の公開Releaseと一致すること。
- ZIPのパス逸脱・シンボリックリンク・不正なラベルが検出できること。
- `dataset.get()`の返り値に分類用とLoRA素材用の違いが表現されること。
- `festival_icons`を勝手にオープンライセンス扱いしないこと。
- `CV_data`のREADMEとPyPI予定説明を日本語で統一すること。現時点で未公開であると明記すること。
- NotebookにLevel 2以降の話は加えないこと。
- 50件の候補台帳はすべて未承認のまま保持し、正式提供リストに混ぜないこと。

## 作業結果

PRのURL、変更ファイル、テスト結果、実機で検証したReleaseのファイルサイズ・SHA-256・画像件数、残るリスクを報告してください。
