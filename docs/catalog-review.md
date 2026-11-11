# カタログ候補の精査状況

更新日：2026-11-11

このページは`registry/candidates_50_unreviewed.json`を、ライブラリに追加する前の判断材料として整理したものです。台帳に書かれたライセンスは候補者の申告であり、ここで「CC BY 4.0」「CC0」などと書かれていても、画像そのものの権利確認や教材での再配布承認を意味しません。


### 2026-11-09 再確認

FruitSeg30、Pistachio Image Dataset、Recyclable Wasteは、公式ページのCC BY 4.0表示に基づき再配布条件を確認しました。Pistachioは画像が研究者自身により作成されたという関連論文の記載も確認し、出典・変更通知・指定論文2件の引用を条件に承認しました。Pistachio artifactはmanifest全件照合とCRC検査に成功し、固定Release v0.1.0を公開、取得APIをmainに反映済みです。Recyclable Wasteは第三者の商標・肖像審査が未完了のため保留です。PyPI配布版への反映はパッケージ更新時です。Food Waste Bangladeshは人物の写り込みがあった画像を除外してv0.1.1を公開し、取得APIへ登録します。Bangladeshi E-Wasteはブランド・製品文字の権利確認が残るため保留です。

## 現在の扱い

| 区分 | 件数 | ライブラリでの扱い |
| --- | ---: | --- |
| main APIで利用できる生徒向けデータ | 18 | `fabricspotdefect`、`bdroadsigns`、`orange_fruit`、`rdd2020_japan`、`lefood_set`、`tomato_leaves`、`bangladeshi_ewaste_image`、`pust_cafeteria_food`、`fashion_mnist`、`geoset_ennea`、`road_traversing_knowledge`、`fruitseg30`、`fresh_rotten_fruits`、`food_waste_bangladesh`、`smallfishbd`、`pistachio_image_dataset`、`indoor_plant_varieties`、`chakmalipi` |
| 教師向けLoRA素材 | 1 | `festival_icons`。公開許可のみ確認済み。改変・商用利用・再配布許諾は未確認 |
| 固定取得条件または公開条件で保留 | 3 | `kuzushiji_mnist`、`fruits_360`、`recyclable_waste`。Kuzushiji-MNISTはCC BY-SA 4.0表記を確認済みだが、配布データの固定版とSHA-256を確定できず保留。Fruits-360には固定タグReleaseがなく、実体取得は未開始。Recyclable Wasteは第三者の肖像・商標審査が未完了のため生徒APIから除外 |
| 全量技術監査済み・権利/注釈保留 | 1 | `strawberry_ds`。固定v1の247画像・YOLOラベルを検査。MendeleyのCC BY 4.0と同梱Roboflow metadataの`Private`表示の関係、および2件の境界外注釈を解決するまで変換・配布しない |
| 公式ページのライセンス表記を再確認した候補 | 6 | `geosetennea`、`indian_origin_flowers`、`banana_guava_quality`、`tangerines`、`image_dataset_of_indian_coins`、`rgb_d_button_mushroom_growth`。実体検査と再配布審査が未完了 |
| 固定版メタデータ確認・実体展開保留 | 1 | `hgm_4_hand_gestures`。CC BY表示・固定RARのSHAと安全な目録を確認したが、画像を展開・検査できず公開保留 |
| その他の未審査候補 | 30 | 取得APIへ追加しない。画像を収録・再配布しない |

候補台帳54件の現状は、`student_enabled` 14件、`candidate` 30件、`hold` 10件です。Fashion-MNISTは固定コミットの公式リポジトリでMITを確認し、公式Keras実装もデータへのMIT適用を明記するため、権利審査を承認済みに更新しました。FabricSpotDefect、BDRoadSigns、Orange Fruitは公式CC BY 4.0、固定版、整形済みReleaseを確認して生徒向けAPIへ追加しました。BDRoadSignsは交通標識の見分けやすさを調べる課題に使えますが、日本の交通規則や実際の安全判断には使いません。Orange Fruitは画像カテゴリを使った分類や背景・照明の影響を調べる課題に使えますが、鮮度・食用可否・食品安全・病気の判断には使いません。生徒向けAPIで取得できるデータは18件、目標20件まであと2件です。

FabricSpotDefectはMendeley Data v1のCC BY 4.0表示と、著者による家庭の布の撮影説明を確認しました。洗濯前に衣類の目立つ汚れを見つける補助という生徒課題に合わせ、柄布も含む元画像1,014枚・注釈3,288件を共通形式化しました。増強画像は除き、元画像は変更せず、0.5ピクセル以下の端のはみ出しがある矩形29件だけを補正しました。帰属・変更表示を同梱したartifactを固定Release `fabricspotdefect-v0.1.0`として公開し、掲載サイズとSHA-256を照合して生徒向けAPIへ登録しました（[監査記録](../reports/fabricspotdefect-v1-audit.json)、[データ別説明](datasets/fabricspotdefect.md)）。

## 課題別の候補

ChakmaLipī v6はMendeley DataのCC BY 4.0表示と、関連論文の参加同意・倫理審査の説明を確認しました。37,708画像を全量デコードし、同じ数字クラス内の完全一致重複1,450枚を除外。残る36,258枚を48クラス別に分割し、画素値を変えずに共通形式化しました。書き手IDがないため、書き手を分けた評価はできません。`CV_data_artifacts` PR #36をマージし、固定Release assetを公開、SHA-256を再取得照合しました（[データ別説明](datasets/chakmalipi.md)）。

HGM-4 v8はMendeleyのCC BY 4.0表示、固定RAR（228,825,330 bytes）のSHA-256、および安全なアーカイブ目録を確認しましたが、標準の展開ツールがRAR内フィルターに対応せず、完全展開できませんでした。画像実体・同意・プライバシーを未検査のため、配布・教材化は保留です（[データ別説明](datasets/hgm_4_hand_gestures.md)）。

FruitSeg30 v3は公式固定版の全3,938ファイルを取得し、サイズ・SHA-256を照合しました。固定artifact `fruitseg30-v0.1.0` のReleaseを公開し、取得API設定もmainへ反映済みです。PyPI配布版は別途更新が必要です。1,969画像と1,969マスクを全量デコードし、Guava 55組のうち52組で同名画像とマスクの寸法が不一致と判明したため、同クラス全体を除外した29クラス1,914組の共通artifact v0.1.0をローカル作成・manifest検証しました。画像・マスクは512×512で、マスクは0〜255の8-bit grayscaleです。Release asset公開済み。mainブランチのライブラリAPIで利用可能です（[データ別説明](datasets/fruitseg30.md)）。

### 画像分類

採用済み：`bdroadsigns`、`orange_fruit`。BDRoadSignsはバングラデシュの道路標識の見分けやすさを試すクイズに、Orange Fruitは見た目カテゴリの分類や背景・照明による違いを調べる食品ロス課題の試作に使えます。それぞれ日本の交通安全判断、食品の鮮度・安全・病気の判定には使いません。

候補：`quickdraw`、`kuzushiji_mnist`、`kuzushiji_49`、`fruits_360`、`recyclable_waste`、`indian_origin_flowers`、`food_waste_bangladesh`、`mushroom_disease_dataset`、`fishnet`、`smallfishbd`、`cds_cricket`、`thermal_visible_fruits_and_vegetables`、`image_dataset_of_indian_coins`、`vehicle_make_model_images`、`banana_and_guava_quality`、`dry_fruit_image_dataset`、`fresh_and_rotten_fruits`、`indian_medicinal_flower_imfi`、`fruitnet_indian_fruits`、`signalphaset`、`asl_fingerspelling_original_keypoints`、`tangerines`、`clearlens`、`surface_water_floating_waste`、`ghana_currency_gc3558`、`hgm_4_hand_gestures`、`kathakali_mudras`、`growth_stage_flower`、`chakmalipi`、`egg_variety_and_freshness`。

高校生の課題には、まず「画像全体を種類に分け、誤分類を調べる」課題が対応します。植物・果物・リサイクル・手の形・文字などは身近な問いにしやすい一方、病気・鮮度・医療に見える名称は、確定診断や安全判断に使わない注意書きを必須にします。人物の手や道路標識などは、撮影者・第三者画像・地域性・個人情報を確認してから扱います。

### 物体検出

候補：`geosetennea`、`strawberry_ds`、`indian_coin_currency_dataset`、`concrete_column_detection`、`uav_weed_crop_dataset`、`trash_detection_dataset_pavel_kan`、`bangladeshi_e_waste_image`。

「画像の中のどこに何があるか」を扱う課題に向きます。画像とアノテーションの対応、座標形式、境界外座標、学習・テストの分離を全量または明示範囲で確認できるまで、検出APIへ追加しません。UAV画像は撮影場所や第三者の写り込み、構造物の欠陥・廃棄物の判定は実社会の判断へ直結し得るため、教材では実験用の予測として扱います。

### 領域分割

候補：`rgb_d_button_mushroom_growth`、`fruitseg30`、`uav_aquatic_plant_dataset`。

「画像のどの画素が対象か」を扱う課題です。元画像とマスクの同一性、画素値、背景、画像サイズを確認し、マスクを推測で補わない専用アダプタが必要です。最初の実装候補は、台帳上で優先度が高く、食品画像の課題に結び付けやすい`fruitseg30`ですが、採用は実体・権利検査後に決めます。

### 画像生成・LoRAまたは素材

候補：`the_met_open_access`、`poly_haven`、`ambientcg`、`twemoji_graphics`、`kenney_game_icons`、`kenney_board_game_icons`。

これらは分類ラベルへ変換せず、素材・出典・クレジット・改変条件を別管理します。`festival_icons`も同じ扱いで、公開許可を改変・商用利用・再配布の許諾へ読み替えません。モデル重みは本ライブラリへ収録しません。

## 次に実体検査する順番

| 順番 | 候補 | 高校生向けの問い | 先に確認すること |
| ---: | --- | --- | --- |
| 1 | `fruits_360` | 見た目から果物の種類を分類できるか | 固定版、同一個体の撮影系列、画像再配布条件 |
| 2 | `recyclable_waste` | ごみ分別を画像で補助できるか | 元画像の権利、クラス定義、地域依存、誤分類の扱い |
| 3 | `geosetennea` | 画像の中の対象物を囲めるか | アノテーション形式、座標、撮影場所、固定SHA-256 |
| 4 | `fruitseg30` | 果物の領域を画素単位で分けられるか | マスク値、画像との対応、分割条件、固定SHA-256 |
| 5 | `pistachio_image_dataset` | 画像から2種類のピスタチオを分類できるか | 元画像の権利、クレジット、画像以外の同梱ファイル |
| 6 | `fresh_rotten_fruits` | 果物の画像分類と食品ロス、見た目ラベルの限界を考える | CC BY 4.0と著者撮影説明を確認。原画像3,200枚を全量検査し、3,193枚を整形。安全・健康判定には使わない。Release asset待ち |
| 7 | `banana_guava_quality` | 果物の品質クラスを分類できるか | ラベル定義、件数差、元画像の権利、健康・安全用途の禁止 |
| 8 | `quickdraw` | 線画を種類に分けられるか | 大容量取得、利用者投稿の不適切内容、再配布範囲 |

この順番は採用決定ではありません。各候補は、公式ページ・固定版・ライセンス本文・元画像の権利・実ファイル検査・教材公開可否がそろった時点で初めて正式候補になります。

Indian Origin Flowersは公式APIの8,098画像・10クラスを固定し、各クラス1枚のSHA-256照合とJPEGデコードを行いました。ページ記載15,044枚との差、全量デコード、元画像の権利、再配布条件が未完了のため、台帳は`under_review`・公開保留です（[データ別説明](datasets/indian_origin_flowers.md)）。

Pistachio Image Datasetは固定ZIPをSHA-256検証後に安全展開し、画像2,148枚を全量デコードしました。破損0、完全一致重複0で教材分類候補として有望ですが、元画像の権利、クレジット、非画像ファイルの扱い、再配布条件が未完了のため公開保留です（[データ別説明](datasets/pistachio_image_dataset.md)）。

Fresh and Rotten Fruitsは公式v1のCC BY 4.0表示と、著者が青果店・実地で撮影したという説明を確認しました。原画像3,200枚を全量デコード・完全一致重複監査し、7枚を除く3,193枚を整形。64枚を代表目視し、変更・帰属表示を含むartifactを固定Releaseで公開、取得後のサイズ・SHA-256を確認済みです。見た目のラベルは食品安全・可食判定に使用できません（[データ別説明](datasets/fresh_rotten_fruits.md)）。

Banana and Guava Qualityは固定ZIPの1,748画像・6グループを確認し、各グループ代表6枚のCRC・JPEGデコードに成功しました。公式説明の1,738枚との差、ラベル定義、全量監査、元画像権利が未完了のため公開保留です（[データ別説明](datasets/banana_guava_quality.md)）。

Food Waste Bangladesh v1はCC BY 4.0を確認し、固定ZIPの既知SHA-256照合と645画像の全量検査・コンタクトシート確認を完了しました。人物の一部が写る11枚とQR風表示の1枚を除外した633枚で共通artifact v0.1.1を作成し、638ファイルのmanifest・CRC検証を通して固定Releaseを公開しました。ライブラリAPI登録をこの変更で反映します。食器・容器の一部に商品表示が残りますが、推薦・承認を意味しない旨を表示します。撮影場面ラベルで食品廃棄量を測る用途には使いません（[データ別説明](datasets/food_waste_bangladesh.md)）。

SmallFishBD v0.1.1は10魚種1,697枚の固定Releaseを公開し、ZIP SHA-256・サイズと固定URLのHTTP 200を確認しました。CC BY 4.0の帰属・変更表示条件を満たすLICENSE.mdを同梱し、ライブラリAPIへ登録します。青系背景への偏りがあるため自然環境での魚種判定には使えません（[データ別説明](datasets/smallfishbd.md)）。

Tangerines_Imagesは固定RARのSHA-256を照合後、340枚すべてをデコードしました。20組の完全一致重複があり、アーカイブ内にgood／poorラベルとの対応表は見つかりませんでした。ラベルを推測せず、分類変換と公開を保留しています（[データ別説明](datasets/tangerines.md)）。

Image Dataset of Indian Coinsは固定ZIPの中央ディレクトリで6,680画像・7額面を確認し、額面ごとの代表画像7枚をCRC・JPEG検査しました。額面・記念デザイン・表裏の系列単位で分割する方法、全量監査、元画像権利が未完了のため公開保留です（[データ別説明](datasets/indian_coins.md)）。

RGB-D Time-Series Dataset of White Button Mushroom Growthは公式ページでCC BY 4.0と129時点のRGB・深度・COCOインスタンスマスクを説明しています。一方、固定版v1の公式APIが返すのはREADME 1件のみで、画像・注釈ファイルがありません。READMEのSHA-256は照合しましたが、教材用データとして実体確認できないため公開保留です（[データ別説明](datasets/rgb_d_button_mushroom_growth.md)）。

Recyclable Wasteの公開API調査で、ページ記載の1,000枚とAPI一覧の989画像が一致しないことが分かりました。第三者の肖像・商標審査が終わっていないため、整形済みRelease assetは残したままライブラリの生徒向けAPIから除外しています。詳細は[データ別説明](datasets/recyclable_waste.md)に記録しています。

GeoSetEnneaは公式Mendeley Data v1のCC BY 4.0表示と著者撮影説明を確認しました。元画像966枚・8,253注釈を全量技術監査し、拡張画像・画面キャプチャ・同一撮影元の別表現を除いた136枚・1,188注釈を整備。撮影元グループが分割をまたがないtrain 84 / validation 22 / test 30で固定Release v0.1.0を公開し、再取得SHA-256を照合しました。商品名・ロゴは一部に付随的に写るため、出典・変更・非推奨表示を含めています。ライブラリAPIへの登録はPR #46で反映します（[データ別説明](datasets/geoset_ennea.md)）。

Custom Bangladeshi E-Waste Image Dataset v1は公式ページとアーカイブ内READMEのCC BY 4.0表記を確認しました。固定ZIPのSHA-256照合後、全画像2,157枚のデコード、同名ラベルとの対応、12クラスを確認しました。全画像の目視では各ラベルの物品がおおむね一致しましたが、紙・有機物・医療ごみなども含む廃棄物品全般の画像で、電子ごみだけではありません。画像は主に緑色の布上に物品を置いて撮影されています。YOLO矩形752件とpolygon 1,407件が混在するため、共通形式ではpolygonを外接矩形へ変換し、輪郭情報が失われることを記録しています。共通artifact v0.1.0のローカル生成・manifest検証とライブラリ側の読み込み実装は通りました。公開Release assetがまだ作成されていないため、正式一覧と取得APIは未公開のままです（[データ別説明](datasets/bangladeshi_ewaste_image.md)）。

Strawberry-DS v1は固定ZIP（SHA-256照合済み）を安全検査し、247枚のJPEG全量デコード、247件の画像・ラベル対応、1,083個のYOLO矩形を確認しました。6熟度クラスは大きく偏り、2枠が画像上端を約0.005画素越えて現行の厳密検査に通りません。さらにMendeleyのCC BY 4.0表示に対し、同梱Roboflow metadataに`license: Private`とあります。内容権利の確認が済むまで共通artifact化・再配布・API掲載を保留します（[データ別説明](datasets/strawberry_ds.md)）。

## ライブラリへの反映ルール

```python
from cvlesson import datasets

# 生徒向け：承認済みデータだけ
datasets.list_tasks(audience="student")
datasets.list_available(task="classification", audience="student")

# 教師向け：プレビューを含めて確認する場合だけ明示
datasets.list_tasks(audience="teacher", include_preview=True)
```

未審査候補は台帳に残しますが、`list_available()`、`list_tasks()`、Notebookの取得例には出しません。候補を追加するときは、固定URL・SHA-256・画像検査・ライセンス証拠・高校生向けの注意書き・共通アダプタ・ネットワーク不要テストを一つの変更としてそろえます。

Recyclable Wasteは公式v1の公開989画像を全件取得・SHA-256照合・デコードし、完全一致重複12枚を除いた977画像の共通artifactを準備しました。GPS情報を持つ104枚のEXIF等を出力から除き、長辺512px以下へ縮小しました。著者自身の撮影というページ説明とCC BY 4.0を確認しましたが、全画像の第三者権利審査が終わっていないため、生徒向けAPIから除外しています。整形済みRelease assetはすでに公開済みです（[データ別説明](datasets/recyclable_waste.md)）。

Fruits-360公式repoはCC BY-SA 4.0を表示しますが、更新中ブランチ以外に固定タグReleaseを確認できません。source pinningの条件を満たすまで取得しません（[データ別説明](datasets/fruits_360.md)）。


Pistachio Image Dataset v1は固定ZIP・全2,148画像・CC BY 4.0表示・引用条件を確認し、画像だけの共通artifact v0.1.0を準備しました。関連する2021論文自体のCC BY-NC表示とデータセットのCC BY 4.0表示を別々に記録し、画像権利者・第三者権利を追加確認するためRelease/APIは保留です（[データ別説明](datasets/pistachio_image_dataset.md)）。
