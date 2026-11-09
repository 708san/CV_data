# Fashion-MNIST（教師向けプレビュー）

Fashion-MNISTは、衣類画像を10種類に分類するための28×28画素・グレースケールのデータです。公式の学習用60,000枚とテスト用10,000枚があります。

## 現在の状態

固定コミットの4つのIDX gzipを検証し、ライブラリのキャッシュ内でPGM画像へ変換できることを確認しました。標準化後の分割は次のとおりです。

| split | 枚数 |
| --- | ---: |
| train | 54,000 |
| val | 6,000 |
| test | 10,000 |

固定コミットのREADMEは、データをZalandoの商品画像からなる70,000枚の画像と説明しています。一方、同じREADMEのMIT条項は「software and associated documentation files」を対象としており、画像データの個別ライセンスや再配布許可は明記していません。リポジトリのMIT表記だけでは画像の権利を確定できないため、画像の教材公開・再配布は保留し、正式な`list_available()`には掲載していません。

## 開発者・教員向けの取得

```python
from cvlesson import datasets

data = datasets.get("fashion_mnist", allow_preview=True)
df = data.to_df()  # pip install -e '.[dataframe]'
print(df[["label", "label_ja", "split"]].head())
```

`allow_preview=True`は権利確認中のデータを明示的に使うための指定です。生徒向けNotebookや正式API例では使いません。

## ラベル

0：Tシャツ・トップス、1：ズボン、2：プルオーバー、3：ワンピース、4：コート、5：サンダル、6：シャツ、7：スニーカー、8：バッグ、9：アンクルブーツ。

## 出典・ライセンス

- 公式リポジトリ：[zalandoresearch/fashion-mnist](https://github.com/zalandoresearch/fashion-mnist/tree/b2617bb6d3ffa2e429640350f613e3291e10b141)
- 固定コミット：`b2617bb6d3ffa2e429640350f613e3291e10b141`
- リポジトリのライセンス：[MIT License](https://github.com/zalandoresearch/fashion-mnist/blob/b2617bb6d3ffa2e429640350f613e3291e10b141/LICENSE)。READMEではMITの対象をソフトウェアと付属文書と記載。画像データへの適用範囲・再配布許可は未確認。
- 実測レポート：[fashion-mnist-github-b2617bb6.json](../../reports/fashion-mnist-github-b2617bb6.json)

このページのプレビュー状態は、教材公開の承認を意味しません。
