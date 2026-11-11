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

文化祭アイコンは教師向けの権利確認中プレビューです。通常の一覧には出ず、明示指定した場合だけ取得できます。改変・商用利用・再配布の許可は確認できていません。

```python
icons = datasets.get("festival_icons", allow_preview=True)
print(icons.images_dir)
print(icons.metadata_jsonl)  # LoRA学習用の画像説明文
```

`datasets.get()`は固定Releaseを取得してZIPを検証し、ローカルに展開します。保存先の変更は`cache_dir`で指定できます。元の公式testは変更せず、DataFrameではtrainから再現可能なvalを作ります。画像表示には `pip install -e '.[display]'` が必要です。LoRA学習そのものやモデル重みの再配布は、このライブラリの対象外です。

## データの説明

| データ | 内容 | 取得元 | 利用条件 |
| --- | --- | --- | --- |
| [トマトの葉](docs/datasets/tomato_leaves.md) | トマトの葉7,209枚、5種類のラベル | `tomato-v1.2.0` | 元データ：CC0 1.0 |
| [FruitSeg30](docs/datasets/fruitseg30.md) | 果物29クラス、画像・マスク1,914組 | `fruitseg30-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [Road Traversing Knowledge](docs/datasets/road_traversing_knowledge.md) | 道路環境の13画素クラス、画像・マスク701組 | `road-traversing-knowledge-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [SmallFishBD](docs/datasets/smallfishbd.md) | 魚10種類、画像1,697枚 | `smallfishbd-v0.1.1` | CC BY 4.0、出典・変更表示が必要 |
| [ピスタチオ2品種](docs/datasets/pistachio_image_dataset.md) | Kirmizi種・Siirt種、画像2,148枚 | `pistachio_image_dataset-v0.1.0` | CC BY 4.0、出典・変更・指定論文の表示が必要 |
| [Food Waste Bangladesh](docs/datasets/food_waste_bangladesh.md) | 食品廃棄の撮影場面5カテゴリ、画像633枚 | `food-waste-bangladesh-v0.1.1` | CC BY 4.0、出典・変更表示が必要 |
| [LeFood-Set](docs/datasets/lefood_set.md) | 食前・食後の料理画像524組、実測重量と見た目評価 | `lefood-set-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [Fresh and Rotten Fruits](docs/datasets/fresh_rotten_fruits.md) | 果物8種類のfresh／rotten画像3,193枚、16クラス | `fresh-rotten-fruits-v0.1.0` | CC BY 4.0、出典・変更表示が必要。食品安全の判定には使わない |
| [RDD2020 Japan](docs/datasets/rdd2020_japan.md) | 道路損傷4種類、画像7,900枚・bbox 16,469個 | `rdd2020-japan-v0.1.0` | CC BY-NC 3.0、非商用教育利用のみ。出典・変更表示が必要 |
| [観葉植物の種類](docs/datasets/indoor_plant_varieties.md) | 観葉植物7種類、重複除外後1,162枚 | `indoor-plant-varieties-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [GeoSetEnnea](docs/datasets/geoset_ennea.md) | 製図用具9種類、画像136枚・位置注釈1,188件 | `geoset-ennea-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [文化祭アイコン](docs/datasets/festival_icons.md) | アイコン168枚、画像と説明文 | `festival-v1.0.0` | 公開許可あり。改変・商用利用・再配布は要確認 |

トマトの葉と文化祭アイコンは固定Releaseを全量監査済みです。実測値は[トマトの監査レポート](reports/tomato-leaves-v1.2.0.json)と[文化祭アイコンの監査レポート](reports/festival-icons-v1.0.0.json)に保存しています。これは権利の承認を意味しません。

SmallFishBDは全画像レビューと帰属・変更表示条件を確認し、固定Release v0.1.1を公開済みです。ピスタチオ画像はMendeleyのCC BY 4.0表示と、研究者自身が画像を作成したという論文記載を照合し、指定論文2件の引用条件付きで固定Release v0.1.0を公開しています。電子ごみ・食品廃棄など未解決の候補は正式APIに掲載していません。

観葉植物データは元画像1,172枚を全量デコードし、完全一致重複10枚を除外しました。GPSを含むEXIF情報を取り除き、長辺512px以下にそろえた1,162枚を取得できます。家庭や学校で見かける植物の分類を試せますが、有毒性・食用・病気・育て方の判定には使えません。

FruitSeg30は全量監査後、寸法が一致しないGuavaクラスを除いた29クラス1,914組を整備し、固定Releaseを公開しました。GitHub mainブランチでは取得APIを利用できます。PyPI配布版への反映はパッケージ更新時に行います。`to_torch_dataset()`は画像と濃淡マスクを返します。

Road Traversing Knowledgeは701組の画像・画素IDマスクを含む領域分割データです。`data.to_torch_dataset()`は各画素を0〜12の整数クラスIDとして保持し、マスクを`torch.long`の高さ×幅テンソルで返します。背景を含め13クラスの出力を使います。公式test splitはありません。ブラジルの道路画像を日本の通学路や安全性の判定に使わないでください。

許諾済みデータの原本・派生データ・manifestは、コードとは分離した[CV_data_artifacts](https://github.com/708san/CV_data_artifacts)で管理します。PyPIとこのリポジトリには画像・LoRA・学習済み重みを収録しません。データを追加する際は、出典・ライセンス・固定版・SHA-256・変換履歴・監査結果をそろえてから、データ専用リポジトリのRelease assetとして公開します。

Fashion-MNISTは固定コミットとファイル整合性を確認した教師向けプレビューですが、教材公開・再配布の最終確認中です。正式一覧には含めず、開発者が明示した場合だけ`datasets.get("fashion_mnist", allow_preview=True)`で取得できます。Kuzushiji-MNISTは公式データファイルの固定版が確定していないため保留中です。

`datasets.list_tasks(audience="student")`は、生徒が選べる課題タイプとデータIDを返します。画像分類にはFresh and Rotten Fruitsが含まれ、物体検出ではRDD2020 Japanを固定Releaseから取得できます。RDD2020 Japanは約642 MBで、展開後は約646 MBのキャッシュ容量が必要です。CC BY-NC 3.0のため非商用の教育利用に限られます。モデルだけで道路の安全性や修繕順位を決めないでください。教師がプレビューを含めて確認する場合は`datasets.list_tasks(audience="teacher", include_preview=True)`を使います。未審査または未公開の候補は一覧に出しません。

LeFood-Setは`datasets.get("lefood_set")`で食前・食後画像524組を取得し、`to_df()`で実測重量や見た目評価を確認できます。日本の学校給食を代表するデータではなく、健康・栄養判断には使いません。

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
- **このライブラリのコードはMITライセンスです。データはデータごとに利用条件が異なります。** コードのライセンスは配布元画像の利用を許可するものではありません。詳しくは[LICENSE](LICENSE)と各データの説明をご覧ください。
- 元画像の保管場所は配布元が正本です。`CV_data`は取得のみを担当します。

## 配布データの検査

公開済みの固定Releaseから画像を取得し、ラベル・画像ファイルの整合を検査できます。通常のテストではダウンロードしません。

```bash
python -m pip install -e '.[display]'
python -m cvlesson.audit festival_icons --check-images --check-similar --report report.json
```

トマトの葉は `festival_icons` を `tomato_leaves` に変更します。GitHub Actionsの手動ワークフローからも実行できます。[詳しい手順](docs/phase1-release-audit.md)をご覧ください。画像の検査は権利の審査とは別です。
