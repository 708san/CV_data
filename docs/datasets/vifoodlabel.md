# 食品包装OCR・項目整理（ViFoodLabel）

食品包装の写真600枚と、商品名・原材料・添加物・注意書き・栄養表示・原産地・内容量・製造日・期限の構造化正解を収録します。包装の文字を読み、必要な項目を整理する補助機能の試作や、項目ごとの読み取り間違いを比べる課題に使えます。画像はベトナム語を中心とする多言語表示です。

正解は項目ごとのJSONで、文字単位の転記や文字領域の枠ではありません。OCRモデルの文字認識学習用データではなく、OCR出力から情報を整理する評価用として扱います。商品表示の内容は必ず原包装で確認してください。

- 出典：Dung Huynh Thi Cam et al. (2026), [Mendeley Data v2](https://data.mendeley.com/datasets/v97x4ys84h/2), DOI [10.17632/v97x4ys84h.2](https://doi.org/10.17632/v97x4ys84h.2)
- ライセンス：CC BY-NC 4.0。非商用利用のみ。出典表示と変更表示が必要。
- 画像：600枚、全件を評価用`eval`へ配置。画素とJSONの正解値は変更していません。
- 状態：固定Release公開済み（[vifoodlabel-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/vifoodlabel-v0.1.0)）。asset SHA-256：`3845c8794b74c80deabe52dd6c1dcfd4b33a1af9d385cc3188ea4d357d43fff6`。

出典・制約は[監査記録](../../reports/vifoodlabel-v0.1.0-audit.json)を参照。
