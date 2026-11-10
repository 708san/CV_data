# FruitSeg30（教師向け参照）

## 状態

候補ID：`DS-099`。固定Release v0.1.0に29クラス1,914組の画像・マスクを収録し、Mendeley Data v3のCC BY 4.0表示と出典を記録しています。生徒向け一覧には掲載せず、教師向けの領域分割形式例として残します。

[公式データページ](https://data.mendeley.com/datasets/vkht8pfsp3/3)、DOI `10.17632/vkht8pfsp3.3`。Guavaの55組は寸法不一致のため除外しました。固定artifactのZIPは68,242,354 bytes、SHA-256 `129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5`です。

## 生徒向け課題に採用しない理由

画像は果物単品が中心で、家庭や学校の食堂にある混在した果物かご・実際の在庫状況を表しません。マスクは果物の前景を示しますが、果実の個数、重量、廃棄状態や食品ロスを示しません。果物の領域を分ける技術例だけでは、身近な課題を改善する効果を説明できないため、生徒向け課題選択肢から外します。

## 技術記録

固定版の画像・マスク全3,938ファイルをSHA-256照合し、全量デコードしました。29クラス1,914組のマスク値は変更していません。全量監査、権利・変換記録は[監査report](https://github.com/708san/CV_data_artifacts/tree/main/reports)と[利用条件](https://github.com/708san/CV_data_artifacts/tree/main/licenses)にあります。