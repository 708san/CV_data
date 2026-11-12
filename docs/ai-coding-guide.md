# AIに相談して画像データを使う

このページは、ChatGPTやCodexにプログラムの改造を依頼するときのガイドです。

## 使える関数

| 書き方 | できること |
| --- | --- |
| `datasets.list_available()` | 取得できるデータを一覧表示する |
| `datasets.list_tasks(audience="student")` | 生徒が選べる課題タイプとデータIDを表示する |
| `datasets.list_available(task="classification", audience="student")` | 課題タイプと対象者でデータを絞り込む |
| `datasets.list_preview()` | 権利確認中の教師向けプレビューを一覧表示する。正式提供ではない |
| `datasets.info("tomato_leaves")` | データの内容と出典を調べる。引数なしなら一覧を返す |
| `datasets.get("tomato_leaves")` | 固定Releaseを取得し、検証して展開する |
| `datasets.get("indoor_plant_varieties")` | CC BY 4.0の観葉植物7種類・1,162枚を取得する。出典・変更内容を表示する |
| `datasets.get("geoset_ennea")` | CC BY 4.0の製図用具画像と物体位置注釈を取得する |
| `datasets.get("fabricspotdefect")` | CC BY 4.0の布画像と汚れなどの位置注釈1,014枚を取得する |
| `datasets.get("trashnet")` | MITのTrashNet 2,527枚を使い、6素材クラスと生活空間写真の違いを比べる |
| `datasets.get("vifoodlabel")` | CC BY-NC 4.0の食品包装画像600枚から、9項目のOCR整理結果を評価する。非商用のみ |
| `datasets.get("energy_meter_digits")` | CC0の数字切り出し977枚で0〜9分類を試す。メーター全体の値は読まない |
| `datasets.get("トマトの葉")` | 登録済みの日本語名で取得する（曖昧検索はしない） |
| `datasets.cache_info()` | checkout外にあるデータキャッシュの容量を確認する |
| `datasets.clear_cache("tomato_leaves")` | 指定データのキャッシュを削除する。引数なしなら登録済みデータをまとめて削除 |
| `data.to_df()` | 画像パス・ラベル・分割をDataFrameにする |
| `data.to_torch_dataset(split="train", image_size=(64, 64))` | 遅延読み込みのPyTorch Datasetにする |
| `data.show_examples(9)` | 画像例を表示する |
| `data.masks_dir` | 領域分割のマスク保存先を参照する |
| `datasets.get("festival_icons")` | LoRA用画像と説明文を取得する |

`list_available()`の`task`は`ocr`、`classification`、`detection`、`regression`、`segmentation`、`lora`のいずれかです。正式APIに表示されない候補は、台帳上の調査候補であり、取得可能・教材利用可能とは限りません。`include_preview=True`は教師が確認するときだけ指定します。OCRの合成レシート候補は準備中で、Release公開までは一覧にも取得例にも出ません。

RDD2020 Japanは`datasets.get("rdd2020_japan")`で取得できます。日本の道路画像7,900枚を使い、縦ひび・横ひび・亀甲ひび・ポットホールを囲みます。約642 MBのダウンロードが必要です。CC BY-NC 3.0に従って非商用の教育目的で使い、出典・変更内容を表示してください。2020年頃の画像なので、現在の道路状態・安全性・修繕順位の判断には使いません。

TrashNet（2,527枚、MIT）は`datasets.get("trashnet")`で取得できます。6種類は素材の見た目のラベルです。白背景で撮影されたデータなので、自宅で撮った画像を追加して撮影環境の差を調べてください。日本の自治体の分別ルールは自治体の公式情報で別に確認します。

ViFoodLabelは食品包装の文字をOCRで整理する課題候補です（600枚、CC BY-NC 4.0、非商用のみ）。`datasets.get("vifoodlabel")`で取得できます。JSONは9項目の構造化正解で、文字単位の全文正解ではありません。期限や注意書きはモデルだけで判断しません。

電力量計データは数字枠だけを切り出した分類データ（977枚、CC0）として整形済みです。Release公開後に取得APIへ追加します。最初に0〜9を分類する課題向けで、桁・小数点を含む検針値の読み取りには追加の設計と検証が必要です。

LeFood-Setは`datasets.get("lefood_set")`で食前・食後画像524組を取得できます。`to_df()`に実測重量、見た目評価、残量比とpair単位のsplitが含まれます。出典と変更を表示し、日本の給食や健康判断へ一般化しません。

FruitSeg30は領域分割向けの29クラスartifactを固定Releaseで公開済みです。GitHub mainブランチのコードでは`datasets.get("fruitseg30")`で取得できます。PyPI配布版への反映はパッケージ更新時です。`data.to_df()`で画像とマスクの組を確認し、`data.to_torch_dataset()`から画像テンソルと濃淡マスクを読み込めます。マスクは元の0〜255階調を保ち、PyTorch変換時も閾値で二値化しません。

Road Traversing Knowledgeは多クラス領域分割です。`data.classes`の13クラス（背景を含む）に対応し、`to_torch_dataset()`はクラスIDを保った`torch.long`マスクを返します。各画素のIDをクラス番号として扱い、二値マスク用の損失関数へそのまま渡さないでください。クラス8は一覧にはありますが、元の全マスクで未出現です。データは公式train/validationのみで、test splitはありません。

観葉植物の画像1,162枚は`datasets.get("indoor_plant_varieties")`で取得できます。`data.to_df()`でクラスと分割を見たり、`data.show_examples(8)`で画像を確認したりできます。完全一致重複を10枚除き、長辺512px以下へ縮小し、GPS等のEXIFを取り除いています。植物名を調べる学習用であり、有毒性・食用・病気・育て方・安全性は判断しません。

GeoSetEnneaは`datasets.get("geoset_ennea")`で136枚の画像と9クラスの物体位置注釈を取得できます。撮影場所はバングラデシュで、日本の文具や教室を代表しません。文具の商品名・ロゴは付随的に写ります。

LoRA素材は`from cvlesson import loras`から管理します。`loras.list_available()`は生徒向けに承認された素材だけを返し、権利確認中の文化祭アイコンは`loras.list_preview()`で確認できます。重みは配布せず、必要な場合は`loras.get("festival_icon_style", allow_preview=True).get_data(allow_preview=True)`で画像・キャプション素材だけを取得します。

`get()`は`DatasetBundle`を返します。`root`、`images_dir`、`labels_csv`、`metadata_jsonl`、`kind`、`task`、`manifest`、`version`、`classes`、`class_names_ja`、`splits`、`license_info`、`source_info`を参照できます。トマトの葉では`train_dir`と`test_dir`も使えます。監査状態とレポートは`datasets.info("tomato_leaves")`で確認します。

データは`get()`を呼んだときだけダウンロードし、既定ではリポジトリ外の`XDG_CACHE_HOME/cvlesson`（未設定なら`~/.cache/cvlesson`）に保存します。`cache_info()`は登録済みデータの保存量を返し、`clear_cache()`はそのキャッシュだけを削除します。学習や読み込みが終わってから削除してください。削除後は、再取得時にネットワーク接続が必要です。

## 最近追加したデータ

- `datasets.get("recyclable_waste")`：リサイクル素材の画像分類。ポルトガルで撮影され、現地の分別規則を示すものではありません。
- `datasets.get("bangladeshi_ewaste_image")`：12種類の廃棄物品の物体検出。緑色の布上で撮影され、polygon注釈の一部を外接矩形に変換しています。現実のごみ分別や医療廃棄物の処理には使いません。
- `datasets.get("orange_fruit")`：オレンジの見た目5カテゴリを使った分類。背景・照明の影響を調べる食品ロス課題の試作に使えますが、鮮度・食用可否・食品安全・病気の判定には使えません。

いずれも初回取得時に固定版ZIPをダウンロードし、サイズとSHA-256を照合します。利用条件と変換内容は各データの説明を確認してください。

## AIに伝えること

目的、使うデータID、変えたい処理、実行環境、成功条件を伝えると、AIがコードを提案しやすくなります。

> Google Colabで、`cvlesson.datasets.get("tomato_leaves")`で取得した画像から5種類を分類するPythonコードを書いてください。`data.train_dir`と`data.test_dir`を使い、CPUでも動く小さな畳み込みニューラルネットワークを使ってください。データの読み込みから評価までをセルごとに分け、画像や正解ラベルは書き換えないでください。

> `cvlesson.datasets.get("festival_icons", allow_preview=True)`で教師向けプレビューとして取得した`labels.csv`の`image,caption`を読み、最初の5行を表にするコードを書いてください。権利確認中の素材なので、画像・説明文は変更・再配布しないでください。

**注意：** このパッケージはデータの取得・標準化とPyTorch Dataset変換までを提供します。CNN学習、画像生成、LoRA学習のAPIは実装していません。AIに依頼する場合は、必要な学習処理を別のコードで作るよう指定してください。

## AIにデータの検査結果を説明してもらう

開発者・教員は `python -m cvlesson.audit festival_icons --check-images --check-similar --report report.json` で検査できます。生成された `report.json` をAIに渡し、「検査に失敗した項目と、類似画像候補を説明して」と依頼できます。類似候補は目視確認用で、自動削除や重複確定は行いません。画像や配布元の変更、権利上の利用判断はこの操作に含まれません。

FabricSpotDefectは`datasets.get("fabricspotdefect")`で布の画像1,014枚とspot位置注釈を取得できます。洗濯前に汚れを見つける補助を試作し、柄や照明による見え方を比べる課題に使えます。衣類の清潔さ、着用可否、安全性や汚れ落ちを判定するものではありません。

Orange Fruitは`datasets.get("orange_fruit")`でオレンジの見た目5カテゴリを取得できます。分類の試作や、背景・照明で結果がどう変わるかの比較に使えます。ラベルは画像カテゴリであり、食べられるかや食品の安全を決めるものではありません。


## 新しく追加した課題データ

- `datasets.get("indoor_waste_image")`：屋内の紙・プラスチック・キャップ等を検出し、清掃箇所の確認を補助します。地域の分別ルールは別に確認します。
- `datasets.get("wastesegcluster")`：ダッカ周辺の水辺ごみを検出します。日本の水辺の状態や水質には一般化しません。
- `datasets.get("fire_recognition_image")`：火・煙の教材画像を分類します。元ラベルは実場面の安全を示さず、警報・避難判断には使いません。
- `datasets.get("agrifreshnet")`：青果の見た目を24カテゴリに分類します。元ラベルの日数は期限ではなく、可食性・食品安全を判断しません。
- `datasets.get("brazil_road_potholes")`：ブラジルの道路画像2,235枚と穴マスクを取得します。二値マスクを重ねて道路の穴の位置を伝える試作に使えます。日本の通学路の安全性や修繕の必要性は判定しません。
- `datasets.get("click_trash")`：屋外のごみ画像1,126枚と位置を示すbboxを取得します。清掃活動の記録や、清掃場所を共有する試作に使えます。画像はインドで撮影され、日本の街を代表しません。現地画像でも確認し、分別・危険性の判断には使わないでください。
- `datasets.get("obstacles_assistance")`：歩道画像1,250枚から段差・柵・穴・ポール候補のbboxを取得します。通りにくさを記録する地図の試作に使えます。物体が通行を妨げるか、移動できるかはモデルだけで判断せず、地域の人・当事者が現地で確認してください。
