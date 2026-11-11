# Custom Bangladeshi E-Waste Image Dataset（廃棄物品12分類）

画像の中の物品を囲み、12種類のラベルを付ける物体検出教材の候補です。電池・携帯電話・基板などの電子関連品のほか、紙・有機物・医療ごみ・金属・ガラス・プラスチックも含みます。「電子ごみだけ」のデータではありません。

## 出典と利用条件

- 出典：[公式Mendeley Data v1](https://data.mendeley.com/datasets/77383kmdnw/1)、DOI `10.17632/77383kmdnw.1`。
- 提供者：Tanzila Afrin、Azizul Abedin Azmi。
- 公式ページとZIP内READMEにCC BY 4.0と記載されています。再配布時は作者・データ名・出典・ライセンスへのリンクを示し、変更点を記載します。
- アーカイブにはRoboflowで出力されたversion 5のデータであること、画像を640×640へstretch resizeし、auto-contrastを適用したことが記されています。元画像は未加工の撮影画像ではありません。
- 画像中に製品ロゴ等が見えることがあります。ライセンスは画像内の商標や他の第三者権利まで許諾するとは限らないため、商標の識別・推薦教材にはしません。

## 実体検査

- 固定Release：71,712,360 bytes、SHA-256 `70f1bc03d605922370611a7b326d1647fd2bddf030e2acb95c60f55edb6eb6f3`。
- 4,326項目。パス逸脱・シンボリックリンクなし。ZIP全体のCRC検査に成功しました。
- JPEG 2,157枚すべてをデコードし、640×640であることを確認しました。画像とラベルは同名で2,157組すべて対応し、完全一致画像重複はありません。
- クラスはBattery Waste、Glass Waste、Keyboard、Light Bulb、Medical Waste、Metal Waste、Mobile、Mouse、Organic Waste、PCB、Paper Waste、Plastic Wasteの12種です。
- 全2,157枚を一覧で目視し、画像は各ラベルの物品におおむね合っていることを確認しました。多くは明るい緑色の布に物品を並べた写真で、実際の回収現場を写したものではありません。製品名やロゴが見える画像もあります。
- train/valid/testは1,500/330/327画像。ラベルは矩形752件とpolygon 1,407件が混在し、計2,159件です。空ラベル4件を含み、クラスID・座標・ラベル形式エラーは見つかりませんでした。
- polygonを検出用矩形へ変換する場合は、各頂点の最小・最大座標から外接矩形を作ります。対象物の輪郭情報は失われます。元のZIPとpolygonラベルは保持し、変換内容をmanifestに明記します。

## 授業での扱い

まずは画像中の物品を枠で囲み、12種類からラベルを選ぶ課題に使えます。教材では「廃棄物品の写真を使った物体検出」と説明し、電子ごみの回収現場や実際の分別を再現したデータとは紹介しません。

予測結果を、実際のごみ分別、医療廃棄物の処理、危険物の取り扱いに使いません。クラス名はこのデータに付けられたラベルであり、地域の分別規則や安全基準を示すものではありません。polygonから外接矩形へ変換した共通artifact v0.1.0を公開し、固定SHA-256で取得できます。共通artifact v0.1.0は固定Releaseで公開済みです。画像は変更せず、polygon 1,407件を外接矩形へ変換しています。

詳細：[全量監査JSON](../../reports/bangladeshi-ewaste-full-audit.json)、[全画像の目視確認](../../reports/bangladeshi-ewaste-visual-review-2026-11-08.json)。


## 公開版

[CV_data_artifactsのRelease](https://github.com/708san/CV_data_artifacts/releases/tag/bangladeshi-ewaste-v0.1.0)から、画像2,157枚を取得できます。