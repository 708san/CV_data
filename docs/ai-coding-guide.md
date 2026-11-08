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
| `datasets.get("トマトの葉")` | 登録済みの日本語名で取得する（曖昧検索はしない） |
| `datasets.cache_info()` | checkout外にあるデータキャッシュの容量を確認する |
| `datasets.clear_cache("tomato_leaves")` | 指定データのキャッシュを削除する。引数なしなら登録済みデータをまとめて削除 |
| `data.to_df()` | 画像パス・ラベル・分割をDataFrameにする |
| `data.to_torch_dataset(split="train", image_size=(64, 64))` | 遅延読み込みのPyTorch Datasetにする |
| `data.show_examples(9)` | 画像例を表示する |
| `data.masks_dir` | 領域分割のマスク保存先を参照する |
| `datasets.get("festival_icons")` | LoRA用画像と説明文を取得する |

Fashion-MNISTは教師向けプレビューです。権利確認中なので、生徒向けコードでは使わず、開発者が必要な場合だけ `datasets.get("fashion_mnist", allow_preview=True)` を使います。Kuzushiji-MNISTは固定版未確定のため、まだ取得APIを提供していません。

`list_available()`の`task`は`classification`、`detection`、`segmentation`、`lora`のいずれかです。正式APIに表示されない候補は、台帳上の調査候補であり、取得可能・教材利用可能とは限りません。`include_preview=True`は教師が確認するときだけ指定します。

物体検出用の候補データは全量監査と共通形式への変換まで終えましたが、固定Release assetが公開されるまでは正式一覧・取得APIに掲載しません。候補ページには監査結果とpolygonから外接矩形への変換内容を記録しています。

FruitSeg30は領域分割向けの29クラスartifactと取得検証を準備しています。固定Releaseが公開された後は、`data.to_df()`で画像とマスクの組を確認し、`data.to_torch_dataset()`から画像テンソルと濃淡マスクを読み込めます。現在はRelease待ちのため`datasets.get("fruitseg30")`では取得できません。マスクは元の0〜255階調を保ち、PyTorch変換時も閾値で二値化しません。

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
