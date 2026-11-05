# CV_data — 高校生向け画像データの取得

画像分類や画像生成の演習で使うデータを、Google ColabやPythonから取得するためのライブラリです。

**現在は開発初期版です。PyPIにはまだ公開していません。** まず、既存の[CV_sample_data](https://github.com/708san/CV_sample_data)にある2つの固定Releaseからの取得に対応します。元のリポジトリ・タグ・Releaseは変更しません。

## まず使う

ローカル環境では、このリポジトリのフォルダで次を実行します。

```bash
python -m pip install -e .
```

PythonまたはGoogle Colabで、次のように操作します。

```python
from cvlesson import datasets

print(datasets.list_available())
print(datasets.info("tomato_leaves"))

# 初回は約124MBのZIPをダウンロードします。
data = datasets.get("tomato_leaves")
print(data.root)          # 保存先
print(data.labels_csv)    # 正解ラベル
print(data.train_dir)     # 学習用画像
print(data.test_dir)      # テスト用画像
```

文化祭アイコンの画像も同じ方法で取得できます。

```python
icons = datasets.get("festival_icons")
print(icons.images_dir)
print(icons.metadata_jsonl)  # LoRA学習用の画像説明文
```

`datasets.get()`は固定Releaseを取得してZIPを検証し、ローカルに展開します。保存先の変更は`cache_dir`で指定できます。画像の学習処理やLoRAの学習処理は、この初期版にはまだ含まれません。

## データの説明

| データ | 内容 | 取得元 | 利用条件 |
| --- | --- | --- | --- |
| [トマトの葉](docs/datasets/tomato_leaves.md) | トマトの葉7,209枚、5種類のラベル | `tomato-v1.2.0` | 元データ：CC0 1.0 |
| [文化祭アイコン](docs/datasets/festival_icons.md) | アイコン168枚、画像と説明文 | `festival-v1.0.0` | 公開許可あり。改変・商用利用・再配布は要確認 |

上記の数値は**元のReleaseの公表情報**です。個々の画像の破損・重複をすべて実測して確認したものではありません。

外部の画像データセット50件は引き続き候補を審査中で、まだダウンロード用APIとして公開していません。

## AIにプログラムを改造してもらうとき

[AIに相談してコードを変更する方法](docs/ai-coding-guide.md)をご覧ください。使える関数名、データの形、依頼文の例を記載しています。

## 開発・テスト

```bash
python -m unittest discover -s tests -v
```

開発計画は[こちら](docs/development-plan.md)です。実際のデータ取得はネットワークと容量を必要とするため、通常の自動テストでは行いません。

## 出典と注意

- 元の公開データ：<https://github.com/708san/CV_sample_data>
- 使用するタグ・SHA-256はライブラリ内で固定しています。
- **コードのライセンスとデータのライセンスは別です。** 本ライブラリが配布元の画像の権利を許諾するものではありません。
- 元画像の保管場所は配布元が正本です。`CV_data`は取得のみを担当します。
