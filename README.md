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
| [LeFood-Set](docs/datasets/lefood_set.md) | 食前・食後の料理画像524組、実測重量と見た目評価 | `lefood-set-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [Fresh and Rotten Fruits](docs/datasets/fresh_rotten_fruits.md) | 果物8種類のfresh／rotten画像3,193枚、16クラス | `fresh-rotten-fruits-v0.1.0` | CC BY 4.0、出典・変更表示が必要。食品安全の判定には使わない |
| [RDD2020 Japan](docs/datasets/rdd2020_japan.md) | 道路損傷4種類、画像7,900枚・bbox 16,469個 | `rdd2020-japan-v0.1.0` | CC BY-NC 3.0、非商用教育利用のみ。出典・変更表示が必要 |
| [観葉植物の種類](docs/datasets/indoor_plant_varieties.md) | 観葉植物7種類、重複除外後1,162枚 | `indoor-plant-varieties-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [廃棄物品](docs/datasets/bangladeshi_ewaste_image.md) | 廃棄物品12種類、画像2,157枚・位置注釈 | `bangladeshi-ewaste-v0.1.0` | CC BY 4.0、実際の分別判断には使わない |
| [GeoSetEnnea](docs/datasets/geoset_ennea.md) | 製図用具9種類、画像136枚・位置注釈1,188件 | `geoset-ennea-v0.1.0` | CC BY 4.0、出典・変更表示が必要 |
| [FabricSpotDefect](docs/datasets/fabricspotdefect.md) | 衣類の汚れなど1クラス、元画像1,014枚・位置注釈3,288件 | `fabricspotdefect-v0.1.0` | CC BY 4.0、出典・変更表示が必要。着用可否・安全性の判定には使わない |
| [Orange Fruit](docs/datasets/orange_fruit.md) | オレンジの見た目5カテゴリ、画像15,000枚 | `orange-fruit-v0.1.0` | CC BY 4.0、出典・変更表示が必要。鮮度・食用可否・食品安全・病気の判定には使わない |
| [日本語レシートOCR（詳細版）](docs/datasets/japanese_receipts_detailed.md) | レシート画像100枚、領域ラベル2,005件・文字転記1,802件 | `japanese_receipts_detailed-v0.1.0` | CC BY-NC 4.0、非商用のみ。個人情報の黒塗りは一部 |
| [屋内に残ったごみの位置](docs/datasets/indoor_waste_image.md) | 屋内ごみ4種類、4,000画像・6,968枠 | `indoor-waste-image-v0.1.0` | CC BY 4.0、地域の分別は別に確認 |
| [水辺のごみ位置](docs/datasets/wastesegcluster.md) | 水辺ごみ4種類、1,947画像・3,900枠 | `wastesegcluster-v0.1.0` | CC BY 4.0、ダッカ周辺の画像 |
| [火・煙の教材画像](docs/datasets/fire_recognition_image.md) | 4カテゴリ、元画像1,112枚 | `fire-recognition-image-v0.1.0` | CC BY 4.0、「安全」判断には使わない |
| [青果の見た目の段階](docs/datasets/agrifreshnet.md) | 24カテゴリ、重複除外後14,084枚 | `agrifreshnet-v0.1.0` | CC BY 4.0、食用可否の判定には使わない |
| [道路の穴の領域分割](docs/datasets/brazil_road_potholes.md) | ブラジルの道路画像2,235枚・穴マスク2,235枚 | `brazil-road-potholes-v0.1.0` | CC BY 4.0、現地・現在の道路安全性は判定しない |
| [CLICK Trash Dataset](docs/datasets/click_trash.md) | 屋外ごみ1,126枚・位置注釈2,213件 | `click-trash-v0.1.0` | CC BY 4.0、インド撮影。日本の地域や分別ルールを代表しない |
| [歩道上の物体候補](docs/datasets/obstacles_assistance.md) | 4種類、画像1,250枚・bbox 1,627件 | `obstacles-assistance-v0.1.0` | CC BY 4.0。歩道の通行障害や安全の判定には使わない |
| [文化祭アイコン](docs/datasets/festival_icons.md) | アイコン168枚、画像と説明文 | `festival-v1.0.0` | 公開許可あり。改変・商用利用・再配布は要確認 |

トマトの葉と文化祭アイコンは固定Releaseを全量監査済みです。実測値は[トマトの監査レポート](reports/tomato-leaves-v1.2.0.json)と[文化祭アイコンの監査レポート](reports/festival-icons-v1.0.0.json)に保存しています。これは権利の承認を意味しません。

生徒向け一覧には、家庭・学校・地域の課題に使う道筋を説明できるデータだけを掲載しています。取り下げたデータの出典・監査記録・固定Releaseは履歴として保持します。

Recyclable Waste v0.1.1の整形済みRelease assetは公開されていますが、包装上の肖像写真や商品表示を含む第三者権利審査が未完了のため、生徒向けAPIから外しています（[審査記録](docs/datasets/recyclable_waste.md)）。

観葉植物データは元画像1,172枚を全量デコードし、完全一致重複10枚を除外しました。GPSを含むEXIF情報を取り除き、長辺512px以下にそろえた1,162枚を取得できます。家庭や学校で見かける植物の分類を試せますが、有毒性・食用・病気・育て方の判定には使えません。

FruitSeg30は全量監査後、寸法が一致しないGuavaクラスを除いた29クラス1,914組を整備し、固定Releaseを公開しました。GitHub mainブランチでは取得APIを利用できます。PyPI配布版への反映はパッケージ更新時に行います。`to_torch_dataset()`は画像と濃淡マスクを返します。

Road Traversing Knowledgeは701組の画像・画素IDマスクを含む領域分割データです。`data.to_torch_dataset()`は各画素を0〜12の整数クラスIDとして保持し、マスクを`torch.long`の高さ×幅テンソルで返します。背景を含め13クラスの出力を使います。公式test splitはありません。ブラジルの道路画像を日本の通学路や安全性の判定に使わないでください。

Brazil Road Potholesは2,235組の道路画像・二値マスクを含みます。`data.to_torch_dataset()`は元の穴領域を0〜1の濃淡マスクとして返します。同一区間の画像をsplit間で共有しないよう区間単位で分けています。ブラジルの古い道路画像で、現在の日本の道路や安全性には一般化できません。

CLICK Trashは屋外のごみ画像1,126枚と位置注釈2,213件を含みます。`datasets.get("click_trash")`で清掃活動の場所を画像上に示す試作へ使えます。インドの画像なので、日本の地域で使う前に現地画像でも確認してください。分別や危険性の判定には使いません。

Obstacles Avoidance Assistanceは段差・柵・穴・ポールを囲むbboxを収録します。`datasets.get("obstacles_assistance")`で歩道上の物体候補を記録する地図を試作できます。写った物体が通行の妨げかは、通路幅・経路・利用者の状況を含めて人が確認してください。実際の移動支援には単独で使わず、地域の画像と当事者の確認が必要です。

許諾済みデータの原本・派生データ・manifestは、コードとは分離した[CV_data_artifacts](https://github.com/708san/CV_data_artifacts)で管理します。PyPIとこのリポジトリには画像・LoRA・学習済み重みを収録しません。データを追加する際は、出典・ライセンス・固定版・SHA-256・変換履歴・監査結果をそろえてから、データ専用リポジトリのRelease assetとして公開します。

Kuzushiji-MNISTはCC BY-SA 4.0の表示を確認しましたが、公式配布物の固定版とSHA-256を確定できないため保留中です。取得元が動的な状態では固定版取得の安全条件を満たせません。

`datasets.list_tasks(audience="student")`は、生徒が選べる課題タイプとデータIDを返します。画像分類では家庭菜園の葉や青果など、身近な観察課題を扱えます。Orange Fruitは約113 MBで、外観カテゴリや背景・照明の影響を調べる食品ロス課題の試作に使えます。鮮度・食用可否・食品安全・病気の判定には使いません。物体検出では道路損傷、清掃活動、製図用具、洗濯前の衣類の汚れ探しを扱えます。FabricSpotDefectは約744 MBで、展開後は約744 MBのキャッシュ容量が必要です。衣類の清潔さ・着用可否・安全性や汚れ落ちは判定しません。RDD2020 Japanは約642 MBで、展開後は約646 MBのキャッシュ容量が必要です。CC BY-NC 3.0のため非商用の教育利用に限られます。モデルだけで道路の安全性や修繕順位を決めないでください。教師がプレビューを含めて確認する場合は`datasets.list_tasks(audience="teacher", include_preview=True)`を使います。未審査または未公開の候補は一覧に出しません。

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
