# CV_data — 高校生向け画像データの取得

画像分類・物体検出・領域分割・画像生成の演習で使うデータを、Google ColabやPythonから取得するためのライブラリです。

**現在は開発初期版です。PyPIにはまだ公開していません。** データ本体はコードから分離し、元の出典または許諾済みartifactの固定Releaseから取得します。既存の[CV_sample_data](https://github.com/708san/CV_sample_data)は読み取り専用です。

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

# 課題と対象者から選ぶ（生徒向けには承認済みデータだけ）
print(datasets.list_tasks(audience="student"))
print(datasets.list_available(task="classification", audience="student"))

# 初回は約124MBのZIPをダウンロードします。
data = datasets.get("tomato_leaves")
print(data.root)          # 保存先
print(data.labels_csv)    # 正解ラベル
print(data.train_dir)     # 学習用画像
print(data.test_dir)      # テスト用画像
```

日本語名も、登録済みの完全一致なら使えます。

```python
data = datasets.get("トマトの葉")
df = data.to_df()         # pip install -e '.[dataframe]'
print(df[["label_ja", "split"]].head())
print(data.splits)        # train / val / test
```

分類データはPyTorchのDatasetにも変換できます。画像は必要なときだけ読み込むため、全画像を最初からメモリへ載せません。

```python
train_data = data.to_torch_dataset(split="train", image_size=(64, 64))  # pip install -e '.[torch]'
画像, ラベル番号 = train_data[0]
```

キャッシュの容量は確認でき、使い終わったデータは削除できます。既定の保存先はリポジトリの外です。削除後は次回の取得時に再ダウンロードします。

```python
print(datasets.cache_info())  # 登録済みデータの保存量を確認
result = datasets.clear_cache("tomato_leaves")  # 指定データだけ削除
print(result["removed_bytes"])
datasets.clear_cache()  # 登録済みデータのキャッシュをまとめて削除
```

文化祭アイコンの画像も同じ方法で取得できます。

```python
icons = datasets.get("festival_icons")
print(icons.images_dir)
print(icons.metadata_jsonl)  # LoRA学習用の画像説明文
```

`datasets.get()`は固定Releaseを取得してZIPを検証し、ローカルに展開します。保存先の変更は`cache_dir`で指定できます。元の公式testは変更せず、DataFrameではtrainから再現可能なvalを作ります。画像表示には `pip install -e '.[display]'` が必要です。LoRA学習そのものやモデル重みの再配布は、このライブラリの対象外です。

## データの説明

| データ | 内容 | 取得元 | 利用条件 |
| --- | --- | --- | --- |
| [トマトの葉](docs/datasets/tomato_leaves.md) | トマトの葉7,209枚、5種類のラベル | `tomato-v1.2.0` | 元データ：CC0 1.0 |
| [文化祭アイコン](docs/datasets/festival_icons.md) | アイコン168枚、画像と説明文 | `festival-v1.0.0` | 公開許可あり。改変・商用利用・再配布は要確認 |

トマトの葉と文化祭アイコンは固定Releaseを全量監査済みです。実測値は[トマトの監査レポート](reports/tomato-leaves-v1.2.0.json)と[文化祭アイコンの監査レポート](reports/festival-icons-v1.0.0.json)に保存しています。これは権利の承認を意味しません。

外部画像データセット候補は引き続き審査中です。バングラデシュの電子ごみ、食品廃棄、小魚データは全量監査と共通形式変換まで終えましたが、全画像の権利審査とデータ専用Release assetが未完了のため正式APIには掲載していません。審査を終え、固定ReleaseとSHA-256が用意できたデータだけを利用可能一覧に追加します。

FruitSeg30は全量監査後、寸法が一致しないGuavaクラスを除いた29クラス1,914組のartifactと領域分割用取得検証を準備しました。ZIPは固定SHA-256で検証します。データ専用Releaseがまだないため、取得APIと課題一覧には掲載していません。公開後の`to_torch_dataset()`は画像と濃淡マスクを返します。

許諾済みデータの原本・派生データ・manifestは、コードとは分離した[CV_data_artifacts](https://github.com/708san/CV_data_artifacts)で管理します。PyPIとこのリポジトリには画像・LoRA・学習済み重みを収録しません。データを追加する際は、出典・ライセンス・固定版・SHA-256・変換履歴・監査結果をそろえてから、データ専用リポジトリのRelease assetとして公開します。

Fashion-MNISTは固定コミットとファイル整合性を確認した教師向けプレビューですが、教材公開・再配布の最終確認中です。正式一覧には含めず、開発者が明示した場合だけ`datasets.get("fashion_mnist", allow_preview=True)`で取得できます。Kuzushiji-MNISTは公式データファイルの固定版が確定していないため保留中です。

`datasets.list_tasks(audience="student")`は、生徒が選べる課題タイプとデータIDを返します。現在の正式一覧には画像分類だけが表示されます。物体検出と領域分割の取得・形式検査は整備済みですが、固定データReleaseが未公開のため課題一覧にはまだ表示しません。教師がプレビューを含めて確認する場合は`datasets.list_tasks(audience="teacher", include_preview=True)`を使います。未審査または未公開の候補は一覧に出しません。

LoRA素材は画像・キャプション・トリガーワード・利用条件を管理します。モデル重みは再配布しません。生徒向けに承認された素材がない場合、`loras.list_available()`は空になります。

## AIにプログラムを改造してもらうとき

[AIに相談してコードを変更する方法](docs/ai-coding-guide.md)をご覧ください。使える関数名、データの形、依頼文の例を記載しています。

CV分類の生徒向けNotebookは、LLM講座の基準Notebookとは分けて[こちら](notebooks/cv/classification_v1.ipynb)に置いています。

## 開発・テスト

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

開発計画は[こちら](docs/development-plan.md)です。実際のデータ取得はネットワークと容量を必要とするため、通常の自動テストでは行いません。

## 出典と注意

- 元の公開データ：<https://github.com/708san/CV_sample_data>
- 使用するタグ・SHA-256はライブラリ内で固定しています。
- **コードのライセンスとデータのライセンスは別です。** 本ライブラリが配布元の画像の権利を許諾するものではありません。
- 元画像の保管場所は配布元が正本です。`CV_data`は取得のみを担当します。

## 配布データの検査

公開済みの固定Releaseから画像を取得し、ラベル・画像ファイルの整合を検査できます。通常のテストではダウンロードしません。

```bash
python -m pip install -e '.[display]'
python -m cvlesson.audit festival_icons --check-images --check-similar --report report.json
```

トマトの葉は `festival_icons` を `tomato_leaves` に変更します。GitHub Actionsの手動ワークフローからも実行できます。[詳しい手順](docs/phase1-release-audit.md)をご覧ください。画像の検査は権利の審査とは別です。
