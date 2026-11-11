# Japan OCR Mini Benchmark Alpha10：合成レシート

**状態：整形済み、artifact Releaseと生徒向けAPI登録は未完了。** 公開前の候補です。

## どんな課題に使えるか

文化祭や部活動の支出を整理するツールを試作し、レシート画像からOCRで品目・金額を読み取る題材です。読み取った結果を構造化見本の品目や合計額と照らし、どんなレイアウトや文字で間違えるかを調べられます。

## 内容と制約

- 架空の日本語レシート画像10枚。映画、飲食、交通、コインランドリー、温泉などの例を含みます。
- 画像の画素は変更していません。品目・数量・金額・合計額などを、固定版の公開source JSONから`labels.csv`と`metadata.jsonl`へ整理しました。
- 全文の正解文字起こしはありません。文字誤り率を計算するOCRベンチマークではなく、項目抽出の小規模な練習見本です。
- 10枚だけの合成サンプルで、あらゆるレシート様式を代表しません。実際の会計処理には使わないでください。
- 実際のレシートには個人情報が載ることがあります。授業で生徒のレシート画像を共有サービスへアップロードしないでください。

## 権利・出典

Alpha10承認済みpayloadに限定したCC BY 4.0の許諾と、合成データであることを確認しました。出典はK10124, *Japan OCR Mini Benchmark*, Alpha10 approved payload, fixed revision `c82efda5b823494424e6bc6e9ae7577396ded908`です。画像を変更せず、公開source JSONから課題に必要な構造化項目を取り出し、共通形式へ整理しました。

- 固定版：https://huggingface.co/datasets/K10124/japan-ocr-mini-benchmark/tree/c82efda5b823494424e6bc6e9ae7577396ded908/alpha10
- ライセンス：https://creativecommons.org/licenses/by/4.0/
- Alpha10の権利・合成データ説明：[公式データカード](https://huggingface.co/datasets/K10124/japan-ocr-mini-benchmark)

## OCRを試すモデル

Google ColabのT4で、学習済みの日本語OCRモデルを推論に使えます。PaddleOCRのPP-OCRv5は日本語を含み、公開性能表はT4 GPUでの測定を掲載しています。自由版ColabのT4利用は割当や空き状況によります。まずは学習済みモデルの推論で文字を読み、必要なら少量データで追加学習を検討してください。10枚だけでモデルを一から学習する用途には向きません。

## 利用

artifact ReleaseとAPI登録後に、`datasets.list_available(task="ocr", audience="student")`から選び、`datasets.get("japan_ocr_receipts")`で取得する予定です。取得後の`data.to_df()`は画像パス、構造化見本、split、sample_idを返します。公開前はAPIから取得できません。
