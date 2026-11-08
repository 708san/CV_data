# カタログ候補の精査状況

更新日：2026-11-08

このページは`registry/candidates_50_unreviewed.json`を、ライブラリに追加する前の判断材料として整理したものです。台帳に書かれたライセンスは候補者の申告であり、ここで「CC BY 4.0」「CC0」などと書かれていても、画像そのものの権利確認や教材での再配布承認を意味しません。

## 現在の扱い

| 区分 | 件数 | ライブラリでの扱い |
| --- | ---: | --- |
| 固定Releaseの正式データ | 2 | `tomato_leaves`は生徒向け、`festival_icons`は教師向けLoRA素材 |
| 教師向けプレビュー | 1 | `fashion_mnist`。固定コミット・4ファイル・件数・IDX形式を検査済み。権利の最終確認中 |
| 固定取得条件または公開条件で保留 | 3 | `fashion_mnist`、`kuzushiji_mnist`、`fruits_360`。Fruits-360には固定タグReleaseがなく、実体取得は未開始 |
| artifact準備済み・Release/API待ち | 5 | `bangladeshi_e_waste_image`、`food_waste_bangladesh`、`smallfishbd`、`fruitseg30`、`recyclable_waste`。共通形式化・manifest検証済み。正式公開条件はデータ別説明を参照 |
| 全量技術監査済み・権利/注釈保留 | 1 | `strawberry_ds`。固定v1の247画像・YOLOラベルを検査。MendeleyのCC BY 4.0と同梱Roboflow metadataの`Private`表示の関係、および2件の境界外注釈を解決するまで変換・配布しない |
| 公式ページのライセンス表記を再確認した候補 | 8 | `geosetennea`、`indian_origin_flowers`、`pistachio_image_dataset`、`fresh_rotten_fruits`、`banana_guava_quality`、`tangerines`、`image_dataset_of_indian_coins`、`rgb_d_button_mushroom_growth`。実体検査と再配布審査が未完了 |
| 固定版メタデータ確認・実体展開保留 | 1 | `hgm_4_hand_gestures`。CC BY表示・固定RARのSHAと安全な目録を確認したが、画像を展開・検査できず公開保留 |
| その他の未審査候補 | 32 | 取得APIへ追加しない。画像を収録・再配布しない |

上表の正式Release 2件は候補50件とは別の既存配布物です。候補50件の内訳は、固定取得条件または公開条件で保留3件、artifact準備済み5件、全量技術監査済み・保留1件、公式ページのライセンス表記を再確認した8件、固定版メタデータ確認・実体展開保留1件、その他32件です。準備済み候補もRelease asset公開までは正式一覧・取得APIに表示しません。

## 課題別の候補

HGM-4 v8はMendeleyのCC BY 4.0表示、固定RAR（228,825,330 bytes）のSHA-256、および安全なアーカイブ目録を確認しましたが、標準の展開ツールがRAR内フィルターに対応せず、完全展開できませんでした。画像実体・同意・プライバシーを未検査のため、配布・教材化は保留です（[データ別説明](datasets/hgm_4_hand_gestures.md)）。

FruitSeg30 v3は公式固定版の全3,938ファイルを取得し、サイズ・SHA-256を照合しました。1,969画像と1,969マスクを全量デコードし、Guava 55組のうち52組で同名画像とマスクの寸法が不一致と判明したため、同クラス全体を除外した29クラス1,914組の共通artifact v0.1.0をローカル作成・manifest検証しました。画像・マスクは512×512で、マスクは0〜255の8-bit grayscaleです。データ用ReleaseとライブラリAPIは未登録です（[データ別説明](datasets/fruitseg30.md)）。

### 画像分類

候補：`quickdraw`、`kuzushiji_mnist`、`kuzushiji_49`、`fruits_360`、`recyclable_waste`、`indian_origin_flowers`、`pistachio_image_dataset`、`food_waste_bangladesh`、`bdroadsigns`、`mushroom_disease_dataset`、`fishnet`、`smallfishbd`、`cds_cricket`、`thermal_visible_fruits_and_vegetables`、`image_dataset_of_indian_coins`、`vehicle_make_model_images`、`banana_and_guava_quality`、`dry_fruit_image_dataset`、`fresh_and_rotten_fruits`、`indian_medicinal_flower_imfi`、`fruitnet_indian_fruits`、`signalphaset`、`asl_fingerspelling_original_keypoints`、`tangerines`、`clearlens`、`surface_water_floating_waste`、`ghana_currency_gc3558`、`hgm_4_hand_gestures`、`kathakali_mudras`、`growth_stage_flower`、`chakmalipi`、`egg_variety_and_freshness`。

高校生の課題には、まず「画像全体を種類に分け、誤分類を調べる」課題が対応します。植物・果物・リサイクル・手の形・文字などは身近な問いにしやすい一方、病気・鮮度・医療に見える名称は、確定診断や安全判断に使わない注意書きを必須にします。人物の手や道路標識などは、撮影者・第三者画像・地域性・個人情報を確認してから扱います。

### 物体検出

候補：`geosetennea`、`strawberry_ds`、`indian_coin_currency_dataset`、`concrete_column_detection`、`uav_weed_crop_dataset`、`trash_detection_dataset_pavel_kan`、`fabricspotdefect`、`bangladeshi_e_waste_image`。

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
| 6 | `fresh_rotten_fruits` | 元画像と拡張画像を分けて果物の状態を分類できるか | 元画像の権利、全量重複、分割漏洩、健康・安全用途の禁止 |
| 7 | `banana_guava_quality` | 果物の品質クラスを分類できるか | ラベル定義、件数差、元画像の権利、健康・安全用途の禁止 |
| 8 | `quickdraw` | 線画を種類に分けられるか | 大容量取得、利用者投稿の不適切内容、再配布範囲 |

この順番は採用決定ではありません。各候補は、公式ページ・固定版・ライセンス本文・元画像の権利・実ファイル検査・教材公開可否がそろった時点で初めて正式候補になります。

Indian Origin Flowersは公式APIの8,098画像・10クラスを固定し、各クラス1枚のSHA-256照合とJPEGデコードを行いました。ページ記載15,044枚との差、全量デコード、元画像の権利、再配布条件が未完了のため、台帳は`under_review`・公開保留です（[データ別説明](datasets/indian_origin_flowers.md)）。

Pistachio Image Datasetは固定ZIPをSHA-256検証後に安全展開し、画像2,148枚を全量デコードしました。破損0、完全一致重複0で教材分類候補として有望ですが、元画像の権利、クレジット、非画像ファイルの扱い、再配布条件が未完了のため公開保留です（[データ別説明](datasets/pistachio_image_dataset.md)）。

Fresh and Rotten FruitsはOriginal 3,200枚とAugmented 12,335枚の固定ZIPを確認し、Original各クラス代表16枚のCRC・JPEGデコードに成功しました。拡張画像を混ぜた評価漏洩、全量監査、元画像権利、健康・安全用途を確認できるまで公開保留です（[データ別説明](datasets/fresh_rotten_fruits.md)）。

Banana and Guava Qualityは固定ZIPの1,748画像・6グループを確認し、各グループ代表6枚のCRC・JPEGデコードに成功しました。公式説明の1,738枚との差、ラベル定義、全量監査、元画像権利が未完了のため公開保留です（[データ別説明](datasets/banana_guava_quality.md)）。

Food Waste Bangladeshは固定v1 ZIPをSHA-256照合後に安全展開し、645画像すべてをデコードしました。5フォルダは撮影場面ラベルで、婚礼320枚・野菜16枚と偏りがあります。全量の完全一致重複・危険パス・symlinkは0、EXIF/GPS/XMPも検出されませんでした。共通classification artifactを生成・検証しました。食品廃棄量の推定には使えず、Release assetと全画像の権利審査が残るためAPI未公開です（[データ別説明](datasets/food_waste_bangladesh.md)）。

SmallFishBDは固定v2元画像ZIPをSHA-256照合後に安全展開し、1,700枚すべての320×320 JPEGデコードとクラス枚数を確認しました。完全一致重複3枚を除外し、1,697枚で共通classification artifactを生成・検証しました。増強画像ZIPは取得・収録していません。青系背景への偏りがあるため自然環境での魚種判定には使えません。Release assetと全画像の権利審査が残るためAPI未公開です（[データ別説明](datasets/smallfishbd.md)）。

Tangerines_Imagesは固定RARのSHA-256を照合後、340枚すべてをデコードしました。20組の完全一致重複があり、アーカイブ内にgood／poorラベルとの対応表は見つかりませんでした。ラベルを推測せず、分類変換と公開を保留しています（[データ別説明](datasets/tangerines.md)）。

Image Dataset of Indian Coinsは固定ZIPの中央ディレクトリで6,680画像・7額面を確認し、額面ごとの代表画像7枚をCRC・JPEG検査しました。額面・記念デザイン・表裏の系列単位で分割する方法、全量監査、元画像権利が未完了のため公開保留です（[データ別説明](datasets/indian_coins.md)）。

RGB-D Time-Series Dataset of White Button Mushroom Growthは公式ページでCC BY 4.0と129時点のRGB・深度・COCOインスタンスマスクを説明しています。一方、固定版v1の公式APIが返すのはREADME 1件のみで、画像・注釈ファイルがありません。READMEのSHA-256は照合しましたが、教材用データとして実体確認できないため公開保留です（[データ別説明](datasets/rgb_d_button_mushroom_growth.md)）。

Recyclable Wasteの公開API調査で、ページ記載の1,000枚とAPI一覧の989画像が一致しないことが分かりました。詳細は[データ別説明](datasets/recyclable_waste.md)に記録し、公開状態を保留にしています。

GeoSetEnneaは公式公開APIのフォルダ一覧をメタデータだけ確認しました。分割済みの画像966件と対応するYOLOラベル966件は確認できましたが、augmented/rawの別フォルダもあり、公開用の単一固定アーカイブと全量監査は未確定です。物体検出の教材候補としては有望ですが、現時点では公開保留です（[データ別説明](datasets/geoset_ennea.md)）。

Custom Bangladeshi E-Waste Image Dataset v1は公式ページとアーカイブ内READMEのCC BY 4.0表記を確認しました。固定ZIPのSHA-256照合後、全画像2,157枚のデコード、同名ラベルとの対応、12クラスを確認しました。YOLO矩形752件とpolygon 1,407件が混在するため、共通形式ではpolygonを外接矩形へ変換し、輪郭情報が失われることを記録しています。共通artifact v0.1.0のローカル生成・manifest検証とライブラリ側の読み込み実装は通りました。公開Release assetがまだ作成されていないため、正式一覧と取得APIは未公開のままです（[データ別説明](datasets/bangladeshi_ewaste_image.md)）。

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

Recyclable Wasteは公式v1の公開989画像を全件取得・SHA-256照合・デコードし、完全一致重複12枚を除いた977画像の共通artifactを準備しました。GPS情報を持つ104枚のEXIF等を出力から除き、長辺512px以下へ縮小しました。著者自身の撮影というページ説明とCC BY 4.0を確認しましたが、全画像の人手によるプライバシー確認を終えていないためAPI・Releaseは保留です（[データ別説明](datasets/recyclable_waste.md)）。

Fruits-360公式repoはCC BY-SA 4.0を表示しますが、更新中ブランチ以外に固定タグReleaseを確認できません。source pinningの条件を満たすまで取得しません（[データ別説明](datasets/fruits_360.md)）。
