# Tangerines_Images（公開保留）

ミカンの外観を題材に、撮影環境が揃った画像で分類を考える候補です。公式ページは「good／poor condition」を peel appearance に基づくカテゴリと説明し、340枚・640×480 RGB・管理照明・黒背景としています。品質分類の結果を販売・食用可否・安全性の判断に使わないでください。

## 現時点で確認したこと

- 公式Mendeley Dataの固定版1とCC BY 4.0表記を確認しました。
- 固定RARは4,154,193 bytes、SHA-256は`0beab31ff2ae3b7e17068f62de3ba8861739f0ab8733454cf4c123a5cca11ada`です。
- RARにはJPEGが340枚あり、全画像が640×480 RGBとしてデコードできました。破損はありません。
- 20組の完全一致画像がありました。分割時は同一画像がtrainとtestへ分かれないようにまとめる必要があります。
- 画像`mandarina_331.jpg`には果実の横に手が写っています。生徒向けに利用する場合は、第三者の写り込みを含む素材として扱いを検討する必要があります。
- アーカイブ内に確認できたのは連番の画像ファイルです。「good／poor」の対応を示すラベル表は確認できませんでした。画像番号や見た目から正解ラベルは作っていません。
- 固定source manifestは`CV_data_artifacts`に保存しました。分類用共通形式への変換と公開artifactは、対応ラベルの確認後に判断します。

出典：[公式Mendeley Dataページ](https://data.mendeley.com/datasets/9tfbpxpyjz/1)
