# Phase 1：固定Releaseの実ファイル検査

日本語の教材用データの安全性を確認するための手順です。

## 手動検査

初回は公開元からデータを取得します。画像の形式とラベルの対応を確認するには、Pillow（画像を読み込むPythonライブラリ）を追加します。

```bash
python -m pip install -e '.[display]'
python -m cvlesson.audit festival_icons --check-images --check-similar --report report.json
```

トマトの葉は `festival_icons` を `tomato_leaves` に変更します（初回のZIPは約124 MB）。保存済みのデータのみを検査する場合は `--no-download` を付けます。`--check-similar`は8×8平均ハッシュでレビュー候補を記録しますが、自動削除や重複確定は行いません。

GitHub Actions の **Fixed Release manual audit** を実行して同じ検査を行うこともできます。これは手動実行専用です。通常の自動テストでは外部データを取得しません。

結果の `status=passed` は、取得した固定ZIPのハッシュ値・ラベル整合性と、指定した画像検査の成功を示します。`image_decode=not_checked` は画像の実体検査が未実施であることを意味します。**データの権利審査はこの検査で完了しません。**

`CV_sample_data` に対しては、参照・ダウンロード以外の操作を一切行いません。
