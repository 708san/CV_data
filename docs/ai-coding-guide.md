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
| `datasets.get("pistachio_image_dataset")` | CC BY 4.0のピスタチオ画像2,148枚を取得する。出典・変更・指定論文2件を表示する |
| `datasets.get("トマトの葉")` | 登録済みの日本語名で取得する（曖昧検索はしない） |
| `datasets.cache_info()` | checkout外にあるデータキャッシュの容量を確認する |
| `datasets.clear_cache("tomato_leaves")` | 指定データのキャッシュを削除する。引数なしなら登録済みデータをまとめて削除 |
| `data.to_df()` | 画像パス・ラベル・分割をDataFrameにする |
| `data.to_torch_dataset(split="train", image_size=(64, 64))` | 遅延読み込みのPyTorch Datasetにする |
| `data.show_examples(9)` | 画像例を表示する |
| `data.masks_dir` | 領域分割のマスク保存先を参照する |
| `datasets.get("festival_icons")` | LoRA用画像と説明文を取得する |

Fashion-MNISTは教師向けプレビューです。権利確認中なので、生徒向けコードでは使わず、開発者が必要な場合だけ `datasets.get("fashion_mnist", allow_preview=True)` を使います。Kuzushiji-MNISTは固定版未確定のため、まだ取得APIを提供していません。

`list_available()`の`task`は`classification`、`detection`、`regression`、`segmentation`、`lora`のいずれかです。正式APIに表示されない候補は、台帳上の調査候補であり、取得可能・教材利用可能とは限りません。`include_preview=True`は教師が確認するときだけ指定します。

RDD2020 Japanは`datasets.get("rdd2020_japan")`で取得できます。日本の道路画像7,900枚を使い、縦ひび・横ひび・亀甲ひび・ポットホールを囲みます。約642 MBのダウンロードが必要です。CC BY-NC 3.0に従って非商用の教育目的で使い、出典・変更内容を表示してください。2020年頃の画像なので、現在の道路状態・安全性・修繕順位の判断には使いません。

LeFood-Setは`datasets.get("lefood_set")`で食前・食後画像524組を取得できます。`to_df()`に実測重量、見た目評価、残量比とpair単位のsplitが含まれます。出典と変更を表示し、日本の給食や健康判断へ一般化しません。

FruitSeg30は領域分割向けの29クラスartifactを固定Releaseで公開済みです。GitHub mainブランチのコードでは`datasets.get("fruitseg30")`で取得できます。PyPI配布版への反映はパッケージ更新時です。`data.to_df()`で画像とマスクの組を確認し、`data.to_torch_dataset()`から画像テンソルと濃淡マスクを読み込めます。マスクは元の0〜255階調を保ち、PyTorch変換時も閾値で二値化しません。

Road Traversing Knowledgeは多クラス領域分割です。`data.classes`の13クラス（背景を含む）に対応し、`to_torch_dataset()`はクラスIDを保った`torch.long`マスクを返します。各画素のIDをクラス番号として扱い、二値マスク用の損失関数へそのまま渡さないでください。クラス8は一覧にはありますが、元の全マスクで未出現です。データは公式train/validationのみで、test splitはありません。

ピスタチオ画像v0.1.0はKirmizi種・Siirt種の2,148枚です。Mendeley DataのCC BY 4.0表示と画像作成者に関する論文記載を確認し、指定された2論文も引用しています。`datasets.get("pistachio_image_dataset")`で取得し、`data.to_df()`からクラス・分割を確認できます。撮影背景が黒に統一されているため、一般の食品写真での識別性能を保証しません。食品の品質・鮮度・安全性は判定しません。

SmallFishBD v0.1.1は魚10種類、1,697枚の分類データです。固定ReleaseとSHA-256を確認済みで、`datasets.get("smallfishbd")`で取得できます。`data.to_df()`で画像・魚種ラベル・train/validation/test分割を確認できます。青系背景の画像に偏るため、自然環境の魚種判定には使わないでください。

LoRA素材は`from cvlesson import loras`から管理します。`loras.list_available()`は生徒向けに承認された素材だけを返し、権利確認中の文化祭アイコンは`loras.list_preview()`で確認できます。重みは配布せず、必要な場合は`loras.get("festival_icon_style", allow_preview=True).get_data(allow_preview=True)`で画像・キャプション素材だけを取得します。

`get()`は`DatasetBundle`を返します。`root`、`images_dir`、`labels_csv`、`metadata_jsonl`、`kind`、`task`、`manifest`、`version`、`classes`、`class_names_ja`、`splits`、`license_info`、`source_info`を参照できます。トマトの葉では`train_dir`と`test_dir`も使えます。監査状態とレポートは`datasets.info("tomato_leaves")`で確認します。

データは`get()`を呼んだときだけダウンロードし、既定ではリポジトリ外の`XDG_CACHE_HOME/cvlesson`（未設定なら`~/.cache/cvlesson`）に保存します。`cache_info()`は登録済みデータの保存量を返し、`clear_cache()`はそのキャッシュだけを削除します。学習や読み込みが終わってから削除してください。削除後は、再取得時にネットワーク接続が必要です。

## AIに伝えること

目的、使うデータID、変えたい処理、実行環境、成功条件を伝えると、AIがコードを提案しやすくなります。

> Google Colabで、`cvlesson.datasets.get("tomato_leaves")`で取得した画像から5種類を分類するPythonコードを書いてください。`data.train_dir`と`data.test_dir`を使い、CPUでも動く小さな畳み込みニューラルネットワークを使ってください。データの読み込みから評価までをセルごとに分け、画像や正解ラベルは書き換えないでください。

> `cvlesson.datasets.get("festival_icons", allow_preview=True)`で教師向けプレビューとして取得した`labels.csv`の`image,caption`を読み、最初の5行を表にするコードを書いてください。権利確認中の素材なので、画像・説明文は変更・再配布しないでください。

**注意：** このパッケージはデータの取得・標準化とPyTorch Dataset変換までを提供します。CNN学習、画像生成、LoRA学習のAPIは実装していません。AIに依頼する場合は、必要な学習処理を別のコードで作るよう指定してください。

## AIにデータの検査結果を説明してもらう

開発者・教員は `python -m cvlesson.audit festival_icons --check-images --check-similar --report report.json` で検査できます。生成された `report.json` をAIに渡し、「検査に失敗した項目と、類似画像候補を説明して」と依頼できます。類似候補は目視確認用で、自動削除や重複確定は行いません。画像や配布元の変更、権利上の利用判断はこの操作に含まれません。
