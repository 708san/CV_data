# ResNet18分類・回帰モデル

## 既定モデル

- 実装：Torchvision `resnet18`
- 重み：`ResNet18_Weights.IMAGENET1K_V1`（固定）
- 重みのファイル名：`resnet18-f37072fd.pth`（約45 MB）
- 入力前処理：重みに付属するTorchvisionのtransform情報を使う
- 学習方法：ResNet本体を固定し、新しい出力層だけを学習する
- 取得：`fit()`を呼び出したときにTorchvisionが取得し、PyTorchの外部キャッシュへ置く。CV_dataのwheelには含めない。

重みのrevisionやURLはTorchvision側で管理されます。対応するTorchvisionバージョンと重みを記録し、利用者が別のTorchvision ResNet18重みを指定した場合は、その重み固有の前処理を使います。

## 利用条件と出典

Torchvisionは`IMAGENET1K_V1`をImageNet-1Kで評価されたResNet18重みとして登録しています。[TorchvisionのResNet18重み定義](https://github.com/pytorch/vision/blob/main/torchvision/models/resnet.py)には重みファイルのURLと前処理が記載され、重み読込時にハッシュを検査する実装があります。

ImageNetの[公式アクセス条件](https://www.image-net.org/download.php)は、ImageNetデータベースを非商用の研究・教育目的で使う条件を掲げています。一方、Torchvisionの重み定義には重みファイル独自のライセンス文が見当たりません。そのため、このライブラリは重みを再配布せず、利用例を非商用の教育・研究目的に限って案内します。商用利用の許可があるとは表示しません。

利用時にはImageNetの公式条件と、導入するTorchvisionバージョンの重み情報を確認してください。分類・回帰の学習で使う画像データにも、データごとの利用条件が適用されます。

## 対応API

```python
from cvlesson import models

print(models.available_devices())
model = models.ResNetClassifier(epochs=3, device="cpu")
model.fit(image_paths, labels)
predictions = model.predict(image_paths)
accuracy = model.score(image_paths, labels)
```

分類は`ResNetClassifier`、数値予測は`ResNetRegressor`を使います。回帰では単画像と画像ペアを受け取れます。必要な依存は`pip install cv-data-lesson[torch]`です。初回利用には重み取得のためネットワーク接続が必要です。

学習・予測の`X`には画像パス列またはPillow Image列を指定できます。回帰のペアでは各画像をパスまたはPillow Imageにできます。DataFrameの`image_path`列も利用できます。

```python
from PIL import Image

with Image.open("my_image.jpg") as opened:
    image = opened.convert("RGB")
prediction = model.predict(image)
print(prediction)
```

## 動作確認

PyTorch 2.2.2、Torchvision 0.17.2のCPU環境で、公式のImageNet重み取得と小さな合成画像による分類の`fit`・`predict`・`score`を確認しました。回帰はランダム初期化重みで画像ペア入力の一連のAPIを確認しました。採用データでの学習、Colab T4、GPU実行は未確認です。

実データを使う確認手順：[トマト葉のResNet分類Notebook](../notebooks/cv/classification_v1.ipynb)、[LeFood-SetのResNet回帰Notebook](../notebooks/colab/resnet_regression_smoke_test.ipynb)。両Notebookはtrain/validation/testを分けて評価します。Colabで実行するまでは、これらのデータとGPUでの動作を検証済みとは扱いません。
