# まず試す

## 1. インストール

Python 3.11〜3.13で使えます。現在はalpha版なので、pipに開発版も選ばせる`--pre`が必要です。表や画像例の表示も含めて、最初はこの1行だけ実行します。

```bash
python -m pip install --pre cv-data-lesson
```

Colabでは先頭に`%`を付けます。

```python
%pip install --pre cv-data-lesson
```

## 2. データを探して取得

```python
from cvlesson import datasets

print(datasets.list_tasks(audience="student"))
for item in datasets.list_available(audience="student")[:8]:
    print(item["id"], item["name_ja"], "—", item["task"])
print(datasets.info("tomato_leaves"))

data = datasets.get("tomato_leaves")
print(data.to_df().head())
data.show_examples(6)
```

一覧表示や`import`では画像データをダウンロードしません。`get()`を呼ぶと固定版データを取得し、既定ではホームフォルダ内のキャッシュへ保存します。利用条件や他のデータは[使い方ガイド](student-guide.md)と[データ別説明](datasets/)を確認してください。

## 3. 分類モデルを学習

ResNetを使う前に、分類・回帰用の依存を入れます。Colabでは次のセルを実行してください。ローカルでは`python -m pip install --pre --upgrade 'cv-data-lesson[torch]'`を実行します。

```python
%pip install --pre --upgrade 'cv-data-lesson[torch]'
```

`to_df()`の`split`列から学習用とテスト用を分けます。列名は実データで確認してください。

```python
from cvlesson.models import ResNetClassifier

frame = data.to_df()
train_data = frame[frame["split"] == "train"]
test_data = frame[frame["split"] == "test"]

model = ResNetClassifier(epochs=3, batch_size=16, device="cpu")
model.fit(train_data["image_path"], train_data["label"])
print(model.predict(test_data["image_path"].iloc[:3].tolist()))
print("正解率:", model.score(test_data["image_path"], test_data["label"]))
```

最初に扱う画像数や学習回数を小さくし、動作と結果を確認してから調整します。CPUでは時間がかかることがあります。ResNetは初回に学習済み重みを取得します。

## 4. 次に読む

- [高校生向け機能・使い方ガイド](student-guide.md)
- [AIに改造を相談する](ai-coding-guide.md)
- [機能別インストール](installation.md)
- [データとモデルの対応表](data-model-compatibility.md)
- [分類・回帰](resnet-model.md)、[OCR](ocr.md)、[検出・領域分割](vision.md)、[画像生成・LoRA](image-generation.md)
- [公開版をColabで機能別に確認する](colab-verification.md)
