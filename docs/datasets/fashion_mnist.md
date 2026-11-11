# Fashion-MNIST（衣類画像の分類）

Fashion-MNISTは、衣類・靴・バッグの28×28画素の白黒画像70,000枚を10種類に分類するデータです。低解像度の画像分類を学び、クラスごとの間違いを比較できます。

## データの分割

| split | 枚数 |
| --- | ---: |
| train | 54,000 |
| val | 6,000 |
| test | 10,000 |

公式train 60,000枚のうち6,000枚を、seed 42でクラスごとに分けてvalidationにしました。公式test 10,000枚は維持しています。画素値を変えず、IDX形式からPGM形式へ変換しています。

```python
from cvlesson import datasets

data = datasets.get("fashion_mnist")
df = data.to_df()  # pip install -e '.[dataframe]'
print(df[["label", "label_ja", "split"]].head())
data.show_examples(9)  # pip install -e '.[display]'
```

## クラス

Tシャツ・トップス、ズボン、プルオーバー、ワンピース、コート、サンダル、シャツ、スニーカー、バッグ、アンクルブーツ。

## 出典・ライセンス

- 公式リポジトリ：[zalandoresearch/fashion-mnist](https://github.com/zalandoresearch/fashion-mnist/tree/b2617bb6d3ffa2e429640350f613e3291e10b141)
- 固定コミット：`b2617bb6d3ffa2e429640350f613e3291e10b141`
- ライセンス：[MIT License](https://github.com/zalandoresearch/fashion-mnist/blob/b2617bb6d3ffa2e429640350f613e3291e10b141/LICENSE)
- 整形済みデータ：[固定Release v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/fashion-mnist-v0.1.0)
- Release ZIP：45,813,814 bytes、SHA-256 `7b62741950bb9784980c9703806df874a1f1c3930dcc8a84477e2c6b5c6e871f`

このベンチマークは実際の衣服写真を代表しません。商品の状態、サイズ、ブランド、再利用の可否を判定する用途には使わないでください。
