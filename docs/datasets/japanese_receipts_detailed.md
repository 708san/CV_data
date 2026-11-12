# 日本語レシートOCR（詳細版）

**状態：固定Release公開済み、生徒向けAPIに登録済み。** 取得時に約130MBをダウンロードします。

## どんな課題に使えるか

文化祭や部活動の支出入力を補助するOCRを試作し、日付・品目・合計の候補を読み取ります。読み取り結果は会計担当者がレシート原本と照合します。自動で会計や支払いを決める用途ではありません。

## 内容と使い方

- 日本語の実レシート画像100枚、領域ラベル2,005件、文字転記1,802件。
- 全画像がeval splitです。OCRモデルの推論と、注釈のある範囲で結果を比べる用途向けです。学習用データや全文OCR正解集ではありません。
- 詳細版は配布元の基本版1,010枚から選ばれた部分集合で、追加の100枚ではありません。
- ラベルには店舗名、日時、明細、税額、合計などが含まれます。画像に写る文字のすべてに転記が付いているわけではありません。
- データセットを取得するには次のようにします。

```python
from cvlesson import datasets

data = datasets.get("japanese_receipts_detailed")
records = data.to_df()  # image path, ground_truth, split, sample_id
```

## 権利・個人情報

出典は[IngCrowd Inc.のデータセット](https://huggingface.co/datasets/IngCrowd/japanese-receipts-detailed)、ライセンスは[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)です。**非商用利用のみ**可能です。IngCrowd Inc.とデータセットを表示し、変更内容を明記してください。

配布元の黒塗りは一部で、完全な匿名化ではありません。店舗情報、公開連絡先、QRコード、取引・レシート番号が残ることがあります。個人の特定・プロファイリングに使わず、生徒自身のレシートを共有サービスへアップロードしないでください。

## 出典・固定版

IngCrowd Inc., *Japanese Receipt Image Dataset (Detailed Annotations)*, fixed revision `e679e42ba2a408038d4151ced36eb6f32589422c`. 画素は変更せず、画像を共通の配置にし、選択注釈を百分率座標と構造化OCR記録に整理しました。全画像をeval splitとして保持しています。

- [公開Release](https://github.com/708san/CV_data_artifacts/releases/tag/japanese_receipts_detailed-v0.1.0)
- SHA-256: `4f3a480f09eeacfda9f9ca4d84dd01ad8aefa49cce776ec06a7d64f5f25dfb5a`
- [全量監査レポート](../../reports/japanese_receipts_detailed-v1-full-audit.json)
