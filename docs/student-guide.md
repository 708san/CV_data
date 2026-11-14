# 画像AIの使い方ガイド

このライブラリでは、課題に合う画像やモデルを選び、入力を渡し、結果を画像や数値で確かめられます。`cv-data-lesson`はpipで使う配布名、`cvlesson`はPythonで読み込む名前、表示名は「CV教材ライブラリ」です。[PyPIで公開中の0.1.0](https://pypi.org/project/cv-data-lesson/0.1.0/)には生徒向けデータ23件と学習済みLoRA 4件があります。LoRA学習素材は現在登録されていません。使用例は出発点です。テーマ、入力画像、出力の見せ方は自分の課題に合わせて考えられます。

基本導入だけでデータ一覧、表、画像例を使えます。モデル機能は使いたいものだけ追加します。分類・回帰は`torch`、検出・領域分割は`vision`、SDXL画像生成は`diffusion`です。CPUのOCRは`ocr` extraだけでPaddlePaddleも入ります。複数機能を使う場合はextrasをまとめて指定できます。GPU版PaddlePaddleだけは環境に合う公式wheelを選びます。コマンドは[インストール案内](installation.md)を確認してください。

Colabでは、最初は新しいランタイムで使う機能の行だけを実行してください。通常の導入では`--upgrade`を付けません。今入っている版を意図して更新する場合だけ、[インストール案内](installation.md)を確認してから更新してください。

```python
%pip install 'cv-data-lesson[torch]'       # 分類・回帰
%pip install 'cv-data-lesson[vision]'      # 検出・領域分割
%pip install 'cv-data-lesson[diffusion]'   # SDXL画像生成
```

CPU OCRは`%pip install 'cv-data-lesson[ocr]'`だけで準備できます。モデル重みやデータはこのコマンドでは入りません。初回の`datasets.get()`またはモデルの`load()`時に取得します。

OCR・検出・画像生成を同じ新規環境で使う場合は、まとめて導入できます。

```python
%pip install 'cv-data-lesson[ocr,vision,diffusion]'
```

メソッドの引数、既定値、戻り値、入力の条件は[公開APIリファレンス](api-reference.md)を確認してください。

## 1. データを選ぶ

まず生徒向けに利用できるタスクとデータを確認します。

```python
from cvlesson import datasets

print(datasets.list_tasks(audience="student"))
print(datasets.list_available(audience="student"))
```

`task`を指定すると候補を絞れます。データの説明・形式・ライセンスを読んでからIDを選びます。

```python
choices = datasets.list_available(task="classification", audience="student")
print(choices)
print(datasets.info("tomato_leaves"))
```

データを取る操作は`datasets.get()`です。初回はデータ本体をダウンロードして、リポジトリ外のキャッシュに保存します。

```python
data = datasets.get("tomato_leaves")
frame = data.to_df()       # 画像パス・ラベル・分割などを表で見る
print(frame.head())
data.show_examples(6)      # 画像例を表示
```

データごとに列や注釈が違います。何が入っているかは`data.to_df().columns`、画像の場所は`data.root`やデータ別ガイドで確認してください。[データとモデルの対応表](data-model-compatibility.md)には登録データの形式と対応するAPIをまとめています。

## 2. 分類・数値予測

### 分類

分類は、画像から決められたラベルのどれに近いか予測します。`ResNetClassifier`はResNet18の画像特徴を固定し、データのクラス数に合わせた出力層を学習します。

```python
from cvlesson.models import ResNetClassifier

frame = data.to_df()
train_data = frame[frame["split"] == "train"]
test_data = frame[frame["split"] == "test"]

model = ResNetClassifier(epochs=3, batch_size=16, device="cpu")
model.fit(train_data["image_path"], train_data["label"])
predicted = model.predict(test_data["image_path"])
print("正解率:", model.score(test_data["image_path"], test_data["label"]))
probability_目安 = model.predict_proba(test_data["image_path"])
```

ここでの`train_data`と`test_data`は、データセットの`to_df()`から分割で選んだ表を想定しています。クラス名は自動で扱います。`predict_proba()`はクラスごとのモデル出力を確率に変換した目安で、正しさの保証ではありません。学習時とテスト時に同じ画像が混ざらないよう、データにあるsplitを使います。

### 回帰

回帰は画像1枚または画像ペアから数値を予測します。数値は1個でも複数でも指定できます。ResNet18の特徴は固定し、出力層を学習します。

```python
from cvlesson import datasets
from cvlesson.models import ResNetRegressor

data = datasets.get("lefood_set")
frame = data.to_df()
train_data = frame[frame["split"] == "train"]
test_data = frame[frame["split"] == "test"]
image_pair = ["image_before_path", "image_after_path"]
target = "consumed_weight_g"

model = ResNetRegressor(epochs=3, batch_size=16, device="cpu")
model.fit(train_data[image_pair], train_data[target])
prediction = model.predict(test_data[image_pair])
print("R²:", model.score(test_data[image_pair], test_data[target]))
```

画像ペアのデータは、対応表にある2枚の画像入力列を使います。`score()`は決定係数R²です。値が低い・負の場合もあり、データが少ない場合の予測結果を一般化しないでください。

両方ともscikit-learnに似た`fit()`、`predict()`、`score()`の流れです。画像パスまたはPillow Imageを渡せます。GPUを使う場合は`available_devices()`を確認して`device="cuda:0"`を指定します。

## 自分の画像を準備する

Colab左側の「ファイル」欄から画像をアップロードし、表示されたパスを`image_path`または`SOURCE_IMAGE_PATH`へ設定してください。`files.upload()`のポップアップは使いません。Safariなどでアップロードに失敗する場合は、画像をGoogle Driveへ置き、Driveをマウントしてそのファイルパスを指定してください。 ローカルでは`image_path = "./自分の画像.jpg"`のようにファイルパスを指定します。

```python
from pathlib import Path

image_path = "/content/your-image.jpg"  # Colab左側の「ファイル」欄からアップロードしたパス
if not Path(image_path).is_file():
    raise FileNotFoundError("Colab左側の「ファイル」欄から画像をアップロードし、image_pathをそのファイル名に合わせてください。")
```

Colabへアップロードした画像は現在のランタイムで処理され、ライブラリが外部サービスへ自動送信することはありません。第三者の写真を使う場合は利用許可や写っている人の同意を確認してください。

## 3. OCR（画像の文字を読む）

OCRは学習済みPP-OCRv5を使う**推論機能**です。このライブラリからOCRモデルを追加学習する機能ではありません。既定は日本語・CPUです。CPU版PaddlePaddleは`ocr` extraに含まれます。GPUを使う場合だけ環境に合う公式wheelを選びます。利用者が`import paddle`を書く必要はありません。

```python
from cvlesson import ocr

reader = ocr.load(device="cpu")
result = reader.predict(image_path)
print(result)  # result.textと同じ読み取った文字を簡潔に表示
for line in result.lines:
    print(line.text, line.confidence, line.polygon)
```

`cvlesson.display`を使うと文字位置を画像上で確認できます。文字が多く重なる場合は、文字ラベルを消して枠だけ表示します。

```python
from cvlesson import display

display.show(image_path, result, show_labels=False)
```

結果には文字、信頼度、画像上の位置が含まれます。信頼度は読み取り正解の保証ではありません。金額や日付など大事な部分は元画像と照合してください。正解文字列がないデータでは、文字認識精度を数値評価できません。導入条件は[インストール案内](installation.md#日本語ocr)を確認してください。

## 4. 物体検出・領域分割

### 物体検出

物体検出は画像内の対象の名前と四角い位置を返します。既定DETRはCOCOの80カテゴリから検出します。好きな物体名を文章で指定する方式ではありません。

```python
from cvlesson import vision

print(vision.available_devices())
detector = vision.load_detector(device="cpu")
objects = detector.predict(image_path, threshold=0.5)
for item in objects:
    print(item.label, item.score, item.box)
```

### 領域分割

領域分割は画像内の指定対象を画素単位のマスクにします。既定SAMは点または四角い枠を受け取り、対象名やクラス名は付けません。

```python
segmenter = vision.load_segmenter(device="cpu")
mask = segmenter.predict(image_path, box=(40, 30, 240, 220))
print(mask.mask.shape, mask.mask.dtype)
```

検出結果の枠をSAMへ渡すこともできます。DETRのラベルは検出モデルの予測、マスクはSAMが枠をもとに作った予測です。どちらも正解の保証ではありません。SAMの`score`は確率や実測IoUではなくモデルの予測品質値です。検出・領域分割モデル自体をデータで学習する機能はありません。実行環境とモデルの限界は[検出・領域分割ガイド](vision.md)を確認してください。

## 5. 画像生成・画像からの変換

SDXLは文章から画像を作る`text-to-image`と、画像を文章に沿って描き変える`image-to-image`に対応します。登録LoRAは4種類です。既定LoRAは`fluent_emoji_3d`です。LoRAの絵柄・利用条件・学習元の注意は[画像生成ガイド](image-generation.md)を確認してください。

```python
from cvlesson import generation, display

print(generation.available_devices())
creator = generation.load(task="text-to-image", lora="fluent_emoji_3d", device="cuda")
image = creator.generate(
    "青い自転車とヘルメットの、丸みのあるアイコン",
    num_inference_steps=25,
    guidance_scale=7.0,
    seed=42,
)
display.show(image)
```

入力写真の雰囲気を変える場合は`task="image-to-image"`と`image=`を使います。`strength`が小さいほど元画像を保ちやすく、大きいほど変化が強くなります。生成結果はPillow Imageです。steps、guidance、seed、画像サイズ、negative prompt、strength、LoRA triggerを調整できます。標準値と変更の意味は画像生成ガイドにあります。

SDXLとLoRAは大きなモデル重みを使います。初回ダウンロードとGPUメモリが必要です。GPUは勝手に選択せず、使う前に確認して明示指定します。生成画像内の文字や事実は正確とは限らず、入力画像の構図や内容も変わることがあります。

各モデルには画像パスまたはPillow Imageを渡せます。

## 結果を考える

- テスト用画像で結果を確かめ、学習用と同じ画像で評価しない。
- 誤った例も画像と一緒に見て、撮影条件、背景、ラベルの偏りを考える。
- 結果は補助情報や試作品として扱い、食品安全・医療・防災・交通安全などの重大な判断をモデルだけに任せない。
- 使用するデータ・モデルの利用条件、出典表示、地域や撮影条件の偏りを確認する。
