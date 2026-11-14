# 公開APIリファレンス

このページは、配布中の`cv-data-lesson`から利用できる`cvlesson`の公開APIを説明します。配布名とPythonのimport名は異なります。機能別の導入方法は[インストール案内](installation.md)、高校生向けの短い例は[使い方ガイド](student-guide.md)と[生徒向けデータ・処理索引](student-data-index.md)、AIへコード作成・変更を頼む際の前提は[AI向けプロジェクト実装コンテキスト](ai-project-context.md)を参照してください。

このリファレンスは現在の実装を記述します。AIが作ったコードを使う場合も、ここにないメソッドや引数、データ列を仮定せず、実際のデータ情報と`help()`で確認してください。

## 共通の約束

- 画像入力は画像ファイルのパス、またはPillowの`Image`です。NumPy配列を画像として渡すAPIには対応していません。
- データやモデルの取得は、`datasets.get()`や各`load()`などを明示的に呼んだ時だけ始まります。基本のimportやカタログ表示では大容量ファイルを取得しません。
- GPUは自動選択されません。各機能の`available_devices()`を見てから`device`を指定します。
- データとモデルのライセンスは個別に適用されます。パッケージコードのMITライセンスとは別です。
- 型表記はPythonの型を簡潔に示したものです。基本インストールに含まれない機能別依存が必要な場合は、[インストール案内](installation.md)のextraを導入します。

## データを探す・取得する

```python
from cvlesson import datasets

datasets.list_tasks(audience="student", include_preview=False)
datasets.list_available(task="ocr", audience="student")
datasets.info("tomato_leaves")
datasets.get("tomato_leaves", cache_dir=None, allow_download=True)
datasets.cache_info(dataset_id="tomato_leaves")
```

以下の表で`*`より後ろに示す引数はキーワードで指定します。例えば`datasets.get("tomato_leaves", cache_dir="/content/cache")`です。

| API | 入力・既定値 | 戻り値と動作 |
|---|---|---|
| `list_tasks` | `audience`: `"student"`または`"teacher"`、既定`"student"`; `include_preview=False` | タスク名・説明・該当データIDの辞書のリスト。ダウンロードしません。 |
| `list_available` | `task`: `ocr`、`classification`、`regression`、`detection`、`segmentation`、`lora`または`None`; `audience`: `student`、`teacher`または`None`; `include_preview=False` | データID、名前、形式、課題例、画像数、サイズ、ライセンス上の注意、固定版、公開状態などの辞書のリスト。プレビューは`include_preview=True`で教師確認用に表示されます。 |
| `info` | `dataset_id=None` | ID省略時は一覧、指定時は1件の詳細辞書。出典の公表情報と実体監査状態を含みます。 |
| `list_preview` | なし | 権利・公開確認中の教師向け候補一覧。正式な生徒向けデータではありません。 |
| `get` | データID必須。`cache_dir=None`、`allow_download=True`、`allow_preview=False` | 固定版ReleaseをSHA-256検証して展開し、`DatasetBundle`を返します。既定キャッシュはリポジトリ外です。キャッシュ済みなら再利用します。`allow_download=False`ではキャッシュがない時に停止します。 |
| `cache_info` | `dataset_id=None`、`cache_dir=None` | キャッシュ済みデータの場所・容量などを返します。 |
| `clear_cache` | `dataset_id=None`、`cache_dir=None` | 対象キャッシュを削除し、削除結果を返します。ID省略時は全登録データのキャッシュが対象です。読み込み中の処理を止めてから実行してください。 |

`cache_info()`は`cache_dir`、`total_bytes`、`datasets`を含む辞書を返します。各データ項目には`dataset_id`、`versions`、`bytes`、`files`が入ります。`clear_cache()`は`cache_dir`、`removed_bytes`、`removed_datasets`を返します。これらの操作は登録済みデータキャッシュだけが対象で、Hugging Faceのモデルキャッシュは削除しません。

データID、列、ライセンス、サイズは固定とは限りません。使う前に`list_available()`、`info(id)`、[データ別説明](datasets/)を確認します。

### `DatasetBundle`

`datasets.get()`が返すデータ参照です。主要な属性は`id`、`kind`、`root`、`manifest`、`source_url`、`version`、`rights_note`、`classes`、`task`、`audiences`、`class_names_ja`、`license_info`、`source_info`、`images_dir`、`masks_dir`、`labels_csv`、`metadata_csv`、`annotations_jsonl`、`metadata_jsonl`、`train_dir`、`test_dir`です。各path属性はローカルキャッシュ内の`pathlib.Path`です。`train_dir`と`test_dir`は該当する分割フォルダがない場合`None`を返します。

| メソッド | 引数・既定値 | 戻り値・対応範囲 |
|---|---|---|
| `to_df(*, val_fraction=0.1, seed=42)` | 検証分割率と乱数seed | pandas DataFrame。画像パス、ラベル・測定値・分割などをタスクに応じて返します。列はデータごとに異なるので、`frame.columns`と`frame.head()`を確認してください。分類では公式test分割を保持し、必要な場合にtrainを決定的にtrain/validationへ分けます。 |
| `splits` | なし | 標準分割ごとの件数を持つ辞書。検証用分割名はデータにより`val`、`valid`、`validation`の場合があります。 |
| `show_examples(n=9, *, split=None, seed=42)` | 表示数、分割名、seed | Notebook等に画像と注釈例を表示し、Matplotlib Figureを返します。実データを取得済みの時に使います。 |
| `to_torch_dataset(*, split="train", image_size=(64, 64), val_fraction=0.1, seed=42)` | 分割、`(高さ, 幅)`、分類の検証分割設定 | 画像を遅延読み込みするPyTorch Dataset。要素は`(画像Tensor, label_id)`、領域分割では`(画像Tensor, マスクTensor)`です。画像分類と領域分割のみ対応し、PyTorchを含む`[torch]`が必要です。 |
| `quality_summary(*, seed=42, val_fraction=0.1)` | split用seedと割合 | 件数・クラス別内訳・分割などの辞書。診断補助で、モデル性能の評価値ではありません。 |

## 分類・回帰（ResNet）

```python
from cvlesson import models

models.available_devices()
models.ResNetClassifier(device="cpu", epochs=5, batch_size=16,
                        learning_rate=1e-3, image_size=224,
                        weights="IMAGENET1K_V1", random_state=42)
models.ResNetRegressor(device="cpu", epochs=5, batch_size=16,
                       learning_rate=1e-3, image_size=224,
                       weights="IMAGENET1K_V1", random_state=42)
```

| 引数 | 意味と条件 |
|---|---|
| `device` | `"cpu"`、`"cuda"`、`"mps"`。既定はCPU。GPU等を使う前に`models.available_devices()`で確認します。 |
| `epochs` | 出力層を学習する回数。1以上の整数、既定5。 |
| `batch_size` | 一度に処理する画像数。1以上の整数、既定16。 |
| `learning_rate` | 学習率。0より大きい有限数、既定0.001。 |
| `image_size` | 正方形に揃える画像サイズ。32以上の整数、既定224。 |
| `weights` | 既定`"IMAGENET1K_V1"`。`"DEFAULT"`、`None`、TorchvisionのResNet18重みも指定できます。 |
| `random_state` | 学習時のseed、既定42。 |

ResNet18の特徴抽出部分は固定し、分類・回帰に応じた出力層だけを学習します。各推定器はscikit-learnに似た`fit(X, y)`、`predict(X)`、`score(X, y)`を持ち、`fit`は学習後の推定器を返します。`X`は画像パスまたはPillow Imageの列です。回帰は画像1枚または画像2枚の組を入力にできます。単一の回帰目標は1次元配列、複数目標は`(画像数, 目標数)`の配列で予測します。これらはすべてキーワード引数で指定します。PyTorchが必要で、`models.available_devices()`にもPyTorchが必要です。

分類の`predict()`は予測ラベル列、`predict_proba()`は`(画像数, クラス数)`のNumPy配列を返します。確率列の順は`model.classes_`です。`score()`は分類では正解率、回帰では決定係数R²を返します。学習用データと評価用データを分け、評価に学習画像を使わないでください。

## OCR

```python
from cvlesson import ocr

ocr.available_devices()
ocr.load(device="cpu", language="japan", cache_dir=None,
         local_files_only=False, detection_model_dir=None,
         recognition_model_dir=None)
reader.predict(image)  # imageはパスまたはPillow Image
```

`load()`はPP-OCRv5 mobileを既定で使い、初回は固定revisionからモデルを取得します。`device`は`"cpu"`または`"gpu:0"`形式です。戻り値の`OCRResult`は`lines`と`source`を持ちます。`text`は検出行を改行でつないだ文字列、`to_dict()`は`source`、`text`、各行の`text`・`confidence`・`polygon`を含む標準Python辞書です。`polygon`は元画像上の4点座標です。confidenceはモデルの目安で、正解確率ではありません。OCRは推論専用で、追加学習はできません。読み取りは元画像と照合してください。

## 物体検出・領域分割

```python
from cvlesson import vision

vision.available_devices()
vision.load_detector(device="cpu", model_id=None, revision=None,
                     cache_dir=None, local_files_only=False)
vision.load_segmenter(device="cpu", model_id=None, revision=None,
                      cache_dir=None, local_files_only=False)
detector.predict(image, threshold=0.5)
segmenter.predict(image, box=None, point=None)
segmenter.segment_detections(image, detections)
```

既定検出器はDETRで、COCOカテゴリを検出します。`predict()`は`Detection`のリストを返し、各要素は`label`、`score`、元画像座標の`box=(x_min,y_min,x_max,y_max)`、`source_size=(width,height)`を持ちます。`threshold`は0〜1です。既定SAMの`predict()`は四角形`box`か点`point=(x,y)`のどちらか一方を受け、`Segmentation`を返します。`mask`は元画像と同じ高さ・幅のNumPy bool配列、`score`はSAMの範囲保証がないマスク品質予測値、`prompt_type`と`prompt`は入力条件です。`segment_detections()`はDETRの枠ごとにSAMを実行し、`DetectedSegment`のリストを返します。visionでは`device="cpu"`、`"cuda:0"`等、`vision.available_devices()`が利用可能と示すGPU、または`"mps"`を指定します。検出・分割モデルの追加学習はありません。

別モデルを指定する場合は`model_id`と固定した40桁`revision`を両方指定します。ライセンス・互換性は利用者が確認します。

## 生成・表示

```python
from cvlesson import generation, display

generation.available_devices()
generation.load(task="text-to-image", lora="fluent_emoji_3d",
                base_model=None, base_revision=None, device="cpu",
                cache_dir=None, local_files_only=False)
generator.generate(prompt, image=None, strength=0.65,
                    negative_prompt=None, num_inference_steps=25,
                    guidance_scale=7.0, seed=None, width=None,
                    height=None, use_trigger=True)
```

`task`は`text-to-image`または`image-to-image`です。既定では登録LoRAと固定版SDXLを読み込み、モデル重みは`load()`時に外部キャッシュへ取得します。`lora=None`ならLoRAを使いません。独自基盤モデルは`base_model`と固定`base_revision`を指定します。生成時の`prompt`は空でない文字列です。image-to-imageでは入力`image`が必要で、text-to-imageに`image`を渡せません。`strength`は0〜1、`num_inference_steps`は1以上の整数、`guidance_scale`は0以上の有限数、指定する`width`/`height`は8以上の8の倍数です。`seed`は整数、`negative_prompt`は文字列、`use_trigger`はboolです。生成結果はPillow Imageです。その他のパラメータと負荷の目安は[画像生成ガイド](image-generation.md)にあります。

```python
display.render(image, result=None, mask_alpha=110, show_labels=True)
display.show(image, result=None, mask_alpha=110, show_labels=True)
display.save(image, path, result=None, mask_alpha=110, show_labels=True)
display.render_ocr_report(image, result, crop_padding=8)
display.show_ocr(image, result, crop_padding=8)
```

`render()`は結果を重ねたRGB Pillow Image、`show()`はNotebook表示後に同じ画像、`save()`は保存した`Path`を返します。Colabでは`show()`の戻り値がセル末尾に残ると同じ画像が再表示されるため、戻り値が不要なら`_ = display.show(...)`と書きます。`mask_alpha`は0〜255、`show_labels`はboolです。OCRレポートは全文と行別詳細をまとめた自己完結HTML文字列、`show_ocr()`はNotebook上で表示します。`save()`は保存先フォルダも作成します。画像の入力・結果オブジェクトは変更しません。対応する結果型や表示例は[検出ガイド](vision.md)と[OCRガイド](ocr.md)を確認してください。

## LoRAの一覧・権利情報

```python
from cvlesson import loras

loras.list_models()                 # 利用できる学習済みLoRA
loras.model_info("fluent_emoji_3d")
loras.get_model("fluent_emoji_3d")  # メタデータのみ。重みを取得しない
loras.list_available(audience="student")  # 学習素材一覧。現在は空
loras.list_preview()                # 権利確認中の素材
loras.info(material_id)
loras.get(material_id, cache_dir=None, allow_download=True, allow_preview=False)
loras.get(material_id).get_data(cache_dir=None,
                                allow_download=True, allow_preview=False)
```

学習済みLoRAの4件は`list_models()`にあります。`list_available()`は学習済みモデルではなく、利用条件を確認したLoRA学習素材の一覧です。現在は0件です。`list_preview()`には正式公開していない確認中素材が含まれます。`loras.get()`は素材の説明を返し、重みや画像は取得しません。`cache_dir`と`allow_download`はこの情報取得では作用せず、素材の実取得は`loras.get(id).get_data()`を明示的に呼んだ時に行われます。学習済みLoRAの重みは`generation.load()`時に配布元から取得し、ライブラリは再配布しません。

## エラーと確認

不正なID、引数、画像形式、座標、未取得のオフラインキャッシュなどは、機能固有の`DatasetError`、`OCRError`、`VisionError`、`GenerationError`等、または`ValueError`/`FileNotFoundError`で通知されます。解決時はエラー全文、Colabランタイム、実行セル、データIDを記録し、利用中の環境からパッケージを無計画に削除しないでください。機能ごとの既知制限は各ガイドに記載します。
