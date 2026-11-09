# Pistachio Image Dataset（公開済み）

## 出典と権利

[Mendeley Data v1](https://data.mendeley.com/datasets/h7pf57cgg9/1)、DOI `10.17632/h7pf57cgg9.1`。投稿者はMurat Koklu氏で、公式ページはCC BY 4.0を表示しています。

関連する2022年論文は、Kirmizi種とSiirt種の試料を研究のために集め、著者らが専用のコンピュータビジョンシステムで画像を作成したと説明しています。Murat Koklu氏は論文の著者・データ管理者にも含まれています。この記載と投稿者の明示的なCC BY 4.0選択に基づき、帰属と出典が必要な2論文の引用を条件として再配布を承認しました。論文PDFや図表はデータに含めていません。権利移転の独立した書面は確認していない点を監査記録に残しています。

表示する帰属：
> Murat Koklu, “Pistachio Image Dataset,” Mendeley Data v1, DOI: 10.17632/h7pf57cgg9.1, CC BY 4.0.

出典が求める引用：
- Ozkan, Koklu & Saracoglu (2021), DOI [10.23751/pn.v23i2.9686](https://doi.org/10.23751/pn.v23i2.9686)
- Singh et al. (2022), DOI [10.3390/electronics11070981](https://doi.org/10.3390/electronics11070981)

## 整形・検査結果

- 固定v1元ZIP：27,859,492 bytes、SHA-256 `140760707018b7f53d91a86a1d7be96d92b1a0d26a75690ab9280ed1170df895`。
- 画像2,148枚すべてJPEG・600×600 RGBとしてデコード成功。完全一致重複はありません。
- Kirmizi_Pistachio 1,232枚、Siirt_Pistachio 916枚。クラス別seed 42でtrain 1,503 / val 322 / test 323に分割しました。
- 画素は変更していません。画像ではない10ファイル（特徴量表、引用文書等）は除外しました。
- 代表4枚を目視しました。全画像を人手確認したわけではありません。

## 取得

固定Release：[`pistachio_image_dataset-v0.1.0`](https://github.com/708san/CV_data_artifacts/releases/tag/pistachio_image_dataset-v0.1.0)

ZIPは25,875,554 bytes、SHA-256 `32bc15c4788052207e3dd52d4450cc15fec9efade3df169d59bb94556d715f24`です。GitHub mainのライブラリでは次のように取得します。

```python
from cvlesson import datasets

data = datasets.get("pistachio_image_dataset")
frame = data.to_df()
print(data.splits)
```

## 高校生向け課題と注意

「撮影条件がそろった画像から、似たピスタチオ2品種を分類できるか」を調べます。黒背景・固定照明で撮影したデータなので、普通の食品写真や農場での識別性能は示しません。品質・鮮度・食品安全・販売価値の判断に使わないでください。
