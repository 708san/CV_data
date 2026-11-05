# Kuzushiji-MNIST（採用保留）

Kuzushiji-MNISTは、28×28画素のグレースケール画像70,000枚、10クラスのくずし字データです。公式READMEではCC BY-SA 4.0と説明されています。

## 保留理由

- 公式リポジトリの説明とライセンス表記は確認済みです。
- 公式ダウンロードは`codh.rois.ac.jp`のデータエンドポイントですが、今回の調査ではデータファイル自体の固定版とSHA-256を確定できませんでした。
- 固定版と既知SHA-256を確認できるまで、`datasets.list_available()`と生徒向けNotebookには追加しません。

## 出典

- 公式リポジトリ：[rois-codh/kmnist](https://github.com/rois-codh/kmnist/tree/eb78dc13345cb00a9ced461e9be277f845534dff)
- ライセンス表記：[READMEのLicense節](https://github.com/rois-codh/kmnist/blob/eb78dc13345cb00a9ced461e9be277f845534dff/README.md#license)
- 公式データURLは、固定版とSHA-256を確認できるまで取得処理へ組み込まない。

これはライセンス不許可の判定ではなく、取得物の固定・整合性確認が不足しているための技術的な採用保留です。
