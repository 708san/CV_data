# 次の開発：Phase 1 実データ検査

## 運用ルール

- AGENTS.mdを最優先で守る。
- CV_sample_dataは完全に読み取り専用とし、固定Releaseからダウンロードするだけ。
- 1課題1ブランチ・1PRを基本とし、mainへの直接変更や自動マージをしない。
- Notebook本文やPyPIの公開設定は、この課題では変更しない。

## Phase 1の確認

- 通常のオフライン単体テスト：python -m unittest discover -s tests -v
- パッケージのビルド確認
- 必要な場合だけ手動で実行：python -m cvlesson.audit festival_icons --check-images --report report.json
- GitHub Actionsの Fixed Release manual audit も手動実行のみ。
- 文化祭アイコンの権利確認は別途実施し、公開許可だけで改変・再配布を認めない。

## 次の候補

小規模な文化祭アイコンの固定Releaseについて、ダウンロード・SHA-256・全画像の読み込み結果を確認する。トマトの葉（約124MB）は別途実機検査を行う。これらが完了するまで、50候補を「検証済み」とはしない。
