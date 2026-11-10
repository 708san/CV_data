# 開発進捗

## 2026-11-10：CLICK Trash Dataset Version 2の一次情報確認

- Mendeleyの固定Version 2ページで、屋外画像1,126枚、2,213注釈、単一クラス／13素材クラス、YOLOとCOCO形式、分割、rare classの欠落、CC BY 4.0表示を確認した。
- 学校周辺・通学路のポイ捨てを考える題材候補として台帳に追加。ただし撮影地域はインド・アッサムで、日本の現地状況やごみ量を表すデータではない。現地で撮った画像を別途集めない限り、地域の清掃優先度を判断する教材にはできない。
- ページ本文の引用がVersion 1を指し、「GitHub and license: to be added」とする一方で、権利欄にはCC BY 4.0を表示している。固定ファイル・SHA-256・実画像・注釈・第三者権利・プライバシー未確認のため候補にとどめ、取得API・再配布・生徒向け公開は保留。
- 台帳は53件に更新。状態はcandidate 35、hold 13、teacher_reference 4、prepared_artifact_pending_release_asset 1。
- 詳細：[CLICK Trash候補レビュー](datasets/click_trash.md)、[候補表](data-first-shortlist-2026-11-09.md)。


## 2026-11-08：Recyclable Waste 全画像の目視確認

- 整形済みの一意画像977枚を10枚の縮小一覧で確認。素材クラスと画像内容に明らかな不一致は見当たらなかった。
- 縮小一覧では明瞭な人物は確認されず、包装上の肖像写真らしきもの1件と、複数画像のブランド・商品文字を記録。これは法的な肖像・商標審査ではない。
- dataset説明と候補台帳を更新。第三者権利・肖像・商標の再配布審査は未完了のため、正式API・公開Releaseの保留を継続。
- 詳細：[目視監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/recyclable-waste-visual-review-2026-11-08.json)、[データ説明](datasets/recyclable_waste.md)。

## 2026-11-08：リモート専用保管・artifact inventory・キャッシュ管理

- データ本体を`CV_data`・`CV_data_artifacts`のGit履歴やPyPIへ入れず、許諾済み整形データは`CV_data_artifacts`の固定Release assetで管理する方針に更新した。大容量LoRA原本は固定した公式配布元から直接取得し、重みは配布しない。
- `cvlesson`の取得時キャッシュはcheckout外（`XDG_CACHE_HOME`または`~/.cache`配下）に置き、明示的な取得API呼び出しまでダウンロードしない運用を明記した。
- 50候補の状態を再集計：candidate 32、hold 15、整形artifact準備済み・Release待ち2、artifact/asset待ち1。holdは公開承認を意味せず、技術監査の進み具合も異なる。
- `CV_data_artifacts`のPR #7を最新`main`へ合わせてマージし、15 source manifest、6 artifact manifest、監査report・ライセンス記録・変換ツールをmainに追加した。GitHub Actionsは成功。画像バイナリとRelease assetは追加していない。
- `datasets.cache_info()`で登録済みデータのキャッシュ容量・版・ファイル数を確認でき、`datasets.clear_cache(dataset_id=None)`で指定データまたは登録済みIDのキャッシュを削除できるようにした。symlinkや通常ファイル以外は事前検出し、登録外ディレクトリは削除対象にしない。
- 容量計測、指定IDだけの削除、登録外フォルダの保持、一括削除、symlink・不正なcache rootの拒否をオフラインテストで確認。`PYTHONPATH=src python -m unittest discover -s tests -v`は32件成功、Pillow未導入の2件をスキップ。
- 一次情報の並行確認、権利ゲート後の取得、調査範囲の事前決定、既存manifest・監査結果の再利用、候補単位のPRを標準手順にし、権利審査は省略しない。

### 次の作業

- 再配布候補の元画像権利・プライバシー審査を進め、許諾済みの整形データをどの固定Release assetで保持するか決める。Release作成は明示許可が済むまで行わない。
- 承認済みデータが現れたら、取得APIの固定URL・サイズ・SHA-256・外部キャッシュを実データなしのテストで先に検証する。

## 2026-11-05：共通APIと分割・監査の土台

### 変更目的

- 固定Release取得を、英語IDと登録済み日本語名の完全一致で呼び出せるようにする。
- 分類データのパス・ラベル・日本語ラベル・クラス番号・分割を共通DataFrameへそろえる。
- 公式testを保持し、trainから再現可能なvalを作る。
- CPUで利用できる遅延読み込みのPyTorch Datasetと、機械可読な品質監査項目を用意する。

### 実装結果

- `DatasetBundle.to_df()`、`show_examples()`、`to_torch_dataset()`を追加。
- `classes`、`class_names_ja`、`splits`、`license_info`、`source_info`を追加。
- 日本語名は登録済み別名の完全一致だけを受け付け、曖昧な推測はしない。
- train/val分割はseed `42`、クラス別、公式test保持で固定。
- 取得失敗時は最大3回まで再試行し、既存のSHA-256・サイズ・安全なZIP展開を維持。
- 監査JSONに、元画像数・使用可能数・クラス数・分割数・破損数・完全一致重複候補・ラベル不一致・除外理由・分割方法・漏洩リスク・検証日時を追加。
- `CV_sample_data`、Release、既存Notebookは変更していない。

### festival_iconsの実体監査結果

- 固定ZIP：2,838,163 bytes、SHA-256一致。
- 画像168枚を全量デコードし、破損0枚、キャプション欠損0件。
- 完全一致重複候補0件、ラベル不一致0件。
- 8×8平均ハッシュで類似候補417組を抽出したが、レビュー用であり重複確定・自動削除はしていない。権利審査は未実施。LoRA素材のため分類用splitは作成していない。
- 詳細：[festival-icons-v1.0.0.json](../reports/festival-icons-v1.0.0.json)

### tomato_leavesの実体監査結果

- 固定ZIP：124,334,101 bytes、SHA-256一致。
- 画像7,209枚を全量デコードし、破損0枚、完全一致重複候補0件、ラベル不一致0件。
- 元の分割はtrain 5,768枚・test 1,441枚。標準化後はtrain 5,191枚・val 577枚・test 1,441枚。
- 8×8平均ハッシュで類似候補14,571組を抽出したが、レビュー用であり重複確定・自動削除はしていない。同一個体・撮影系列のグループ分離と権利審査は未実施。
- 詳細：[tomato-leaves-v1.2.0.json](../reports/tomato-leaves-v1.2.0.json)

### Fashion-MNISTのプレビュー整備

- 公式GitHubの固定コミット`b2617bb6d3ffa2e429640350f613e3291e10b141`を使用。
- 4つのIDX gzipをSHA-256・ヘッダー・件数まで検査し、PGMキャッシュへの変換を確認。
- 標準化後はtrain 54,000 / val 6,000 / test 10,000。
- MIT表記は確認済みだが、教材公開・再配布の最終確認中。正式一覧には未掲載。
- 詳細：[fashion-mnist-github-b2617bb6.json](../reports/fashion-mnist-github-b2617bb6.json)

### CV分類Notebookの新設

- LLM講座の基準Notebookは変更せず、CV分類用の[新Notebook](../notebooks/cv/classification_v1.ipynb)を追加。
- トマトの葉の出典確認、DataFrame、画像例、train/val/test、CPU向け小型CNN、テスト記録、振り返りを含めた。
- Fashion-MNISTとKuzushiji-MNISTは権利・公開状態の理由から生徒向けNotebookには含めていない。

### 検証条件と結果

- オフラインの標準テスト：Python 3.9環境で19件中19件成功（Pillow未導入による2件のskip）。
- Python 3.10環境で19件中19件成功（pandas未導入による1件のskip）。
- `compileall`で`src`と`tests`を検査済み。
- 固定Releaseの全量画像監査を実施済み。取得と画像検査は通常のネットワーク不要テストから分離している。

### 未完了・保留

- `registry/candidates_50_unreviewed.json`は未承認候補のまま。Fashion-MNISTのプレビュー以外は正式APIへ追加していない。
- Kuzushiji-MNISTはライセンス表記を確認したが、公式データファイルの固定版とSHA-256が不足するため保留中。
- 詳細：[kuzushiji_mnist.md](datasets/kuzushiji_mnist.md)
- `festival_icons`はLoRA学習素材としてのみ扱い、分類データや一般的なオープンライセンスとして扱わない。
- CV分類Notebookは新規作成済み。PyTorchを含む実Colab検証と、次の検出・分割Notebookは次の課題。

### データ・LoRA選択基盤

- `datasets.list_preview()`で権利確認中の教師向けデータを正式一覧から分離。
- Fashion-MNISTは固定IDXファイルを検証済みのプレビューとして管理。
- `cvlesson.loras`を追加し、素材・キャプション・トリガーワード・基盤モデル・権利状態を管理。
- 承認済みLoRAがないため、`loras.list_available()`は空。文化祭アイコンは明示的なプレビュー取得のみ。

### 2026-11-05：課題選択カタログと候補精査

- `datasets.list_available(task=..., audience=..., include_preview=...)`を追加し、課題タイプ・対象者・プレビュー状態で候補を絞れるようにした。
- `datasets.list_tasks()`を追加し、生徒が選べる課題タイプとデータIDを一覧化した。未承認の検出・分割候補は表示しない。
- `DatasetBundle`に課題タイプ、対象者、用途、入力・出力、概算取得サイズを追加した。
- `docs/catalog-review.md`に50候補を分類・検出・分割・素材の課題へ対応付け、全候補をAPIへ追加しない理由と次の実体検査順を記録した。
- `Fruits-360`、`Recyclable Waste`、`GeoSetEnnea`、`FruitSeg30`は公式ページでライセンス表記と概要を再確認した。GeoSetEnneaは公式APIのフォルダ別メタデータを追加確認し、画像966件・YOLOラベル966件と別置きのaugmented/rawを記録した。Recyclable Wasteは9枚の代表画像でAPI SHA-256照合とJPEGデコードを実施したが、固定アーカイブSHA-256と全量監査が未完了のため、いずれも台帳は`under_review`・公開保留のままにした。
- `Fruits-360`、`Recyclable Waste`、`GeoSetEnnea`、`FruitSeg30`は公式ページでライセンス表記と概要を再確認した。GeoSetEnneaは全公開2,898ファイルのsource manifestを作成し、分割済み画像966件・YOLOラベル966件とaugmented/rawを記録、内容SHA重複1グループを確認した。Recyclable Wasteは989画像のsource manifestと12重複グループ、9枚の代表画像検査を記録した。FruitSeg30は当初、全30クラスのメタデータと代表画像のみを検査し、詳細は本ページ後半の2026-11-08監査記録で更新した。
- PyPI向けのパッケージビルドを行うが、本番公開・Release作成・mainへのマージは行わない。

### 2026-11-06：Indian Origin Flowersの一次監査

- 公式Mendeley Data v1のCC BY 4.0表記と公開APIを確認した。
- APIの10フォルダ、8,098枚、約1.62GBをファイル単位のsource manifestへ固定した。全ファイルにAPI記載SHA-256がある。
- 各クラスから1枚ずつ、合計10枚を取得してSHA-256照合とJPEGデコードを実施し、すべて成功した。
- ページ説明の15,044枚とAPIの8,098枚が一致しないため、再配布用artifact・正式API・Notebookには追加せず、`under_review`・公開保留とした。
- 詳細：[Indian Origin Flowers](datasets/indian_origin_flowers.md)、[監査JSON](../reports/indian-origin-flowers-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/indian_origin_flowers-v1.json`に保存した。

### 2026-11-06：Pistachio Image Datasetの全量画像監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- SHA-256一致後に安全展開し、画像2,148枚を全量デコードした。JPEG・600×600・RGB、破損0、完全一致重複0だった。
- Kirmizi 1,232枚、Siirt 916枚をseed 42でtrain/val/testへ分け、共通classification artifactをローカル生成してmanifest照合に成功した。
- 元画像の第三者権利、クレジット、ZIP内の非画像ファイル、再配布条件が未完了のため、正式API・Notebook・PyPIには追加せず公開保留とした。
- 詳細：[Pistachio Image Dataset](datasets/pistachio_image_dataset.md)、[監査JSON](../reports/pistachio-image-dataset-full-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/pistachio_image_dataset-v1.json`に保存した。

### 2026-11-06：Fresh and Rotten Fruitsの構成・代表監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIP2本のサイズ・SHA-256を確認した。
- Original 3,200枚、Augmented 12,335枚、16クラスをZIP中央ディレクトリから確認した。Originalは各クラス200枚だった。
- Original各クラス1枚、合計16枚を範囲取得し、ZIP CRCとJPEGデコードに成功した。
- 元画像と拡張画像を混ぜた評価漏洩、全量デコード・重複・元画像権利が未完了のため、正式API・Notebook・PyPIには追加せず公開保留とした。
- 詳細：[Fresh and Rotten Fruits](datasets/fresh_rotten_fruits.md)、[監査JSON](../reports/fresh-rotten-fruits-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/fresh_rotten_fruits-v1.json`に保存した。

### 2026-11-06：Banana and Guava Qualityの構成・代表監査

- 公式Mendeley Data v2のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- ZIP中央ディレクトリからBanana/Guava × Class_A／Class_B／Defectの6グループ、画像1,748枚を確認した。
- 各グループ1枚、合計6枚を範囲取得し、ZIP CRCとJPEGデコードに成功した。代表画像は1024×1024 RGBだった。
- ページ説明の1,738枚とZIPの1,748枚が一致しないため、全量監査、ラベル定義、元画像権利、再配布条件が未完了のまま公開保留とした。
- 詳細：[Banana and Guava Quality](datasets/banana_guava_quality.md)、[監査JSON](../reports/banana-guava-quality-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/banana_guava_quality-v2.json`に保存した。

### 2026-11-06：Tangerines_Imagesの全量画像監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定RARのSHA-256を確認した。
- パスを検査してから340枚を展開し、全画像がJPEG・640×480・RGBとしてデコードできた。破損0、完全一致重複20グループだった。
- 公式ページはgood／poor condition分類を説明するが、アーカイブには画像との対応ラベル表が見つからなかった。連番や見た目からラベルを割り当てず、共通分類変換・正式API・Notebookへの追加は保留した。
- `mandarina_331.jpg`に手の写り込みがあることも記録した。
- 詳細：[Tangerines_Images](datasets/tangerines.md)、[監査JSON](../reports/tangerines-full-image-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/tangerines-v1.json`に保存した。

### 2026-11-06：Image Dataset of Indian Coinsの構成・代表監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- ZIP中央ディレクトリにJPEG6,680枚と7額面フォルダがあり、公式ページの総数と一致した。パス逸脱、symlink、非画像ファイルはなかった。
- 7額面から代表画像を1枚ずつ取得し、ZIP CRCとJPEGデコードを確認した。
- 額面フォルダの下に記念デザイン、表裏があり、同系列画像の分割漏洩対策が必要。全量画像検査、元画像の権利、グループ分割方法が未完了のため、共通artifact・正式API・Notebookへの追加は保留した。
- 詳細：[Image Dataset of Indian Coins](datasets/indian_coins.md)、[監査JSON](../reports/indian-coins-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/indian_coins-v1.json`に保存した。

### 2026-11-06：RGB-D Mushroom Growthの固定版実体確認

- 公式Mendeley Data v1ページのCC BY 4.0表記と、129件のRGB・深度・COCO注釈という説明を確認した。
- 固定版v1の公式APIに登録されているのは`readme.txt` 1件（4,712 bytes）のみ。公式ダウンロードURLから取得したファイルのSHA-256は`a39f7231cdc51bc7fb103d3ff319830caa63f4b196f81593124d435b18dd032f`で、API記載値と一致した。
- READMEはRGB/Depth/Annotationsの構成と時系列撮影を説明するが、実際の画像・深度・注釈ファイルはAPI一覧に存在しない。マスクや対応関係を実体検査できないため、共通形式への変換、正式API、Notebookへの追加を保留した。
- 詳細：[RGB-D Mushroom Growth](datasets/rgb_d_button_mushroom_growth.md)、[監査JSON](../reports/rgb-d-button-mushroom-growth-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/rgb_d_button_mushroom_growth-v1.json`。

### 2026-11-06：Bangladeshi E-Wasteの全量画像・ラベル監査

- 公式Mendeley Data v1およびアーカイブ内READMEのCC BY 4.0表記、提供者、固定ダウンロードURLを確認した。
- 固定ZIP（72,987,704 bytes、SHA-256 `f73b30286225c208e98b34f81eb5ffef7baf79e883039d2087e8db53f6ee284e`）を検証後に安全展開した。パス逸脱・symlinkなし、CRC検査成功。
- 画像2,157枚すべてがJPEG 640×640でOS画像デコーダーによる読み込みに成功。画像・ラベル2,157組は同名で全件対応し、完全一致画像重複0件だった。
- 12クラス、注釈2,159個を確認。通常のYOLO矩形752個とpolygon 1,407個が混在し、空ラベルは4件、クラスID・座標・形式エラーは0件だった。検出共通変換`detection_yolo_v1.1.0`を追加し、polygonを外接矩形へ変換、元の形式別件数をmanifestに記録するようにした。
- train/valid/test分割は画像1,500/330/327枚。testから各クラス1枚ずつ確認した12枚はすべて明るい緑背景だった。公式ページの「背景に変化がある」という説明と見本に差があるため、背景への依存を調べる教材候補とし、実環境の廃棄物分類器としては扱わない。
- artifact v0.1.0を一時領域へ作成し、画像2,157枚・ファイル4,319件のmanifest照合に成功。polygon由来のbboxは座標精度を維持する17桁で出力。ZIPは71,762,431 bytes、SHA-256 `fe06d5579e3a84010e0e6ccd7d90d8230ca72d5fcd39719d6d6d8731595007fa`。ライブラリの全2,157画像・2,159注釈の構造検査とDataFrame変換にも成功した。データ本体はGit履歴へ追加していない。
- ライブラリには検出bundle検証とDataFrame表示を実装したが、公開Releaseが未作成のためsourceを未公開状態に固定し、正式一覧から隠し、取得要求も拒否する。
- 詳細：[Bangladeshi E-Waste](datasets/bangladeshi_ewaste_image.md)、[監査JSON](../reports/bangladeshi-ewaste-full-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/bangladeshi_ewaste-v1.json`。

### 2026-11-07：Food Waste Bangladesh・SmallFishBDの全量監査と共通化

- Mendeley公式v1/v2ページのCC BY 4.0表示、固定ファイル情報、SHA-256を照合してから安全展開した。
- Food Waste Bangladeshは645枚すべてJPEGデコード成功、重複0、危険パス・symlink 0、EXIF/GPS/XMPなし。5ラベルは撮影場面で、クラス数は91/146/72/16/320と偏る。廃棄量を表すデータではない。
- SmallFishBDは元画像1,700枚すべて320×320 JPEGとしてデコードし、公式クラス数に一致。完全一致重複3枚を除外し、1,697枚を収録。20,400枚の増強画像は取得・収録せず、評価時の分割漏洩を避ける。
- `CV_data_artifacts`にsource manifest、ライセンス記録、除外記録、共通classification artifact、検査reportを準備した。両artifactのサイズ・SHA-256・ZIP内manifest検証は済み。
- ライブラリへ両候補を`published=False`で登録。詳細情報は参照できるが、正式一覧と取得APIから隠れ、Release asset作成までは取得できない。
- サンプル目視ではFood Wasteに人物の顔、SmallFishBDに人物は見つからなかったが、全画像を人手で権利・プライバシー審査した結論ではない。全画像の権利審査とRelease asset作成を保留事項として明記した。
- 詳細：[Food Waste Bangladesh](datasets/food_waste_bangladesh.md)、[SmallFishBD](datasets/smallfishbd.md)、[候補精査状況](catalog-review.md)。

### 2026-11-08：Strawberry-DS v1の全量実体・注釈監査

- Mendeley公式v1のCC BY 4.0表示、固定ファイルID・サイズ・SHA-256を確認。SHA-256一致後にZIP検査を行い、505項目・CRC正常・危険パスとsymlinkなしを確認した。
- 247画像すべて3840×2160 JPEGとしてデコードし、247 YOLOラベルとの対応、完全一致重複0、EXIF/XMP APP1なしを確認した。分割はtrain 172、valid 49、test 26。
- 1,083注釈のクラス内訳はEarly-Turning 34、Green 450、Late-Turning 56、Red 225、Turning 42、White 276。2枠は正規化座標の丸めで上端を約0.005画素超え、現行の厳密な共通検査では失敗する。
- 同梱`data.yaml`はRoboflow v4の`license: Private`と記録。一方Mendeleyの掲載ライセンスはCC BY 4.0で、再許諾の権利関係が確認できないため、画像artifact・共通形式変換・APIへの登録を行わず保留した。
- 監査JSONとsource manifestは`CV_data_artifacts`に記録し、画像本体はartifact repositoryへ追加していない。
- 詳細：[Strawberry-DS](datasets/strawberry_ds.md)、[監査report](../../CV_data_artifacts/reports/strawberry_ds-v1-audit.json)、[source manifest](../../CV_data_artifacts/manifests/sources/strawberry_ds-v1.json)。


### 2026-11-08：HGM-4 Hand Gesturesの固定版・アーカイブ目録監査

- Mendeley Data v8のCC BY 4.0表示、DOI、固定RARのファイルID・228,825,330 bytes・SHA-256を確認した。SHA照合後にRAR目録を読み取り専用で確認し、4,270項目、相対パスのみ、symlink・パス逸脱なしを確認した。
- macOS `bsdtar`がアーカイブ内フィルターを処理できず完全展開に失敗した。部分展開物は信頼せず、画像検査・変換・配布に使用していない。画像数・画質・参加者プライバシーの実体確認は未完了。
- 公式論文は5名、4カメラ視点、26種の手形を説明する。人物または撮影系列単位の評価分割が必要で、一般的な手話翻訳・人物識別用途には適さない。
- 固定source manifestと監査reportを`CV_data_artifacts`に追加。再配布・教材化・API掲載は保留。
- 詳細：[HGM-4](datasets/hgm_4_hand_gestures.md)、[監査report](../../CV_data_artifacts/reports/hgm_4_hand_gestures-v8-audit.json)。


### 2026-11-08：FruitSeg30 v3の全量監査と29クラスartifact準備

- 公式固定v3の全3,938ファイル（計224,579,761 bytes）を取得し、ファイル単位のサイズ・SHA-256を全件照合した。1,969 JPEGと1,969 PNGを全件デコードし、マスクPNGのCRCエラーと完全一致重複は0件。
- Guava 55組はすべて非512サイズで、そのうち52組は同名画像とマスクの寸法が不一致。向き・対応を推測せずクラス全体を除外した。残り29クラスの1,914組は512×512で対応し、8-bit grayscaleのマスクを画素変更せず保持。
- クラス内seed 42でtrain/val/testへ分け、共通artifact v0.1.0（1,914画像・1,914マスク、3,833ファイル）をローカル生成。artifact manifest照合成功。ZIPは68,242,354 bytes、SHA-256 `129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5`。
- MendeleyページのCC BY 4.0と論文の撮影説明を確認。第三者由来素材の全画像独立審査、領域分割API、公開Releaseは未完了のため、候補・APIは公開保留。
- 領域分割artifactの固定Release SHA検証、画像・マスク対応検査、DataFrame、遅延読み込みPyTorch Datasetをライブラリに実装。固定Release assetが未作成のため、正式課題一覧からは隠している。
- 詳細：[FruitSeg30](datasets/fruitseg30.md)、[監査JSON](../reports/fruitseg30-sample-audit.json)、source manifestとartifact manifestは`CV_data_artifacts`に保存。


### 2026-11-08：Recyclable Waste v1全量監査と教材artifact準備

- Mendeley Data v1の公開989画像（1,707,541,468 bytes）すべてを既知サイズ・SHA-256に照合し、ImageIOで全件デコード。掲載件数1,000との差11枚は補完しない。
- 完全一致重複12ファイルを除いた一意977画像、クラス別件数、画像寸法を記録。104画像にGPSを含むEXIFを検出。
- 一意画像977枚の共通artifact v0.1.0を作成。EXIF方向を適用、長辺512pxへ縮小、EXIF/GPS等を除去、seed 42でクラス層化split。ZIPは93,671,127 bytes、SHA-256 `99e80d8c0a083b65f7c5550afc87ec2db985b612762d55475a425b8f6db784ed`。
- 代表5枚を目視しブランド・商品文字を確認。全画像の人手によるプライバシー確認が未完了のため、正式API・Releaseは保留。
- Fruits-360公式repoのCC BY-SA 4.0表示を確認したが、GitHub Releasesが空で固定タグReleaseがないため、画像取得・実体検査は保留。
- 詳細：[Recyclable Waste](datasets/recyclable_waste.md)、[Fruits-360](datasets/fruits_360.md)、[監査JSON](../reports/recyclable_waste-v1-full-audit.json)。


### 2026-11-08：Pistachio Image Dataset v1監査・artifact準備

- 固定ZIP（27,859,492 bytes、SHA-256 `140760707018b7f53d91a86a1d7be96d92b1a0d26a75690ab9280ed1170df895`）を再取得・照合し、安全なパスとsymlinkなしを確認。
- 画像以外の特徴量表・引用文書10ファイルを除き、2,148 JPEG（600×600 RGB）全件デコード成功、完全一致重複0。
- 画像画素を変更せず、共通formatとseed 42のクラス層化splitを追加。train 1,503、val 322、test 323。artifact manifest検証成功。
- Mendeley v1はCC BY 4.0表示。掲載者の撮影説明、関連2論文の引用条件を記録。2021論文本文のCC BY-NC表示とdataset licenseを分けて記録。画像権利者・第三者権利の確認が残るためRelease/APIは保留。
- 詳細：[Pistachio](datasets/pistachio_image_dataset.md)、[監査report](../reports/pistachio_image_dataset-v1-full-audit.json)。

## 2026-11-09：整形済み3データの権利・成果物再確認

- FruitSeg30 v0.1.0、Pistachio Image Dataset v0.1.0、Recyclable Waste v0.1.0のZIPを一時領域で再検査。CRCとファイル一覧・全ファイルのSHA-256/サイズがartifact manifestに一致しました。ZIPはGitに追加していません。
- 各公式配布ページのCC BY 4.0表示と提供者の出典説明を確認し、帰属・改変通知（ピスタチオは指定論文引用）を条件に再配布審査を記録しました。
- FruitSeg30は29クラス1,914画像・マスク組、ピスタチオは2,148画像、Recyclable Wasteは977画像。教材課題と注意事項をデータ別ページへ記載しました。
- GitHub Release assetが未作成のため、3件ともライブラリからはまだ取得できません。食品廃棄・E-Wasteは人物／印刷肖像等の権利・プライバシー確認を保留しています。

## 2026-11-09：FruitSeg30 固定Release公開

- FruitSeg30 v0.1.0をGitHub Release `fruitseg30-v0.1.0` に公開。assetは68,242,354 bytes、GitHub APIのSHA-256はmanifest一致（`129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5`）。
- 画像・マスクのバイナリはGit履歴に含めず、Release assetだけで配布。固定タグURLのHTTP応答を確認。
- ライブラリ一覧をstudent-enabledへ切り替える設定と説明の更新をPRに準備中。

- FruitSeg30取得APIを含むPR #25をmainへマージ。固定Release assetとmainブランチのAPI設定が揃いました。PyPI配布版への反映はパッケージ更新時です。


## 2026-11-09：SmallFishBD v0.1.1 Release公開

- artifact準備PR #14をCV_data_artifacts mainへマージ後、固定タグReleaseを作成しました。
- ZIPは29,799,609 bytes。GitHub APIのSHA-256 `367b332bc0da479e9a708449f45cf7aa10eb190267a6bc1f1a87e5a38ce8f547`がローカル成果物と一致し、固定URLはHTTP 200を返しました。
- CC BY 4.0の帰属・変更表示、全画像視覚レビューを踏まえた再配布審査を記録。ライブラリの固定URL・ハッシュ・公開状態、データ説明、候補台帳を更新する内容をCV_data PR #27に提出しました。
