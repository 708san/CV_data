# AIに相談して画像データを使う

このページは、ChatGPTやCodexにプログラムの改造を依頼するときのガイドです。

## 使える関数

| 書き方 | できること |
| --- | --- |
| `datasets.list_available()` | 取得できるデータを一覧表示する |
| `datasets.info("tomato_leaves")` | データの内容と出典を調べる |
| `datasets.get("tomato_leaves")` | 固定Releaseを取得し、検証して展開する |
| `datasets.get("festival_icons")` | LoRA用画像と説明文を取得する |

`get()`は`DatasetBundle`を返します。`root`、`images_dir`、`labels_csv`、`metadata_jsonl`、`kind`、`manifest`、`version`を参照できます。トマトの葉では`train_dir`と`test_dir`も使えます。

## AIに伝えること

目的、使うデータID、変えたい処理、実行環境、成功条件を伝えると、AIがコードを提案しやすくなります。

> Google Colabで、`cvlesson.datasets.get("tomato_leaves")`で取得した画像から5種類を分類するPythonコードを書いてください。`data.train_dir`と`data.test_dir`を使い、CPUでも動く小さな畳み込みニューラルネットワークを使ってください。データの読み込みから評価までをセルごとに分け、画像や正解ラベルは書き換えないでください。

> `cvlesson.datasets.get("festival_icons")`で取得した`labels.csv`の`image,caption`を読み、最初の5行を表にするコードを書いてください。元データは変更しないでください。

**注意：** このパッケージは取得機能のみを提供します。CNN学習、画像生成、LoRA学習のAPIはまだ実装していません。AIに依頼する場合は、必要な学習処理を別のコードで作るよう指定してください。
