# Indian Origin Flowers（公開保留）

花の画像を10種類に分類する課題候補です。花壇や地域の植物を自分で撮影し、学習データとの違いを考える導入に使えます。ただし、データセット内の花名を自然環境の植物同定や安全判断に使わないでください。

## 現時点で確認したこと

- 公式Mendeley Dataの固定版1を確認しました。
- 公式ページのライセンス表記はCC BY 4.0です。
- 公開APIのフォルダは10クラスです：Bougainvillea、Bright Eyes、Cape Jasmine、Chandni、Dhalia、Hibiscus、Marigold、Pink Oleander、Rose、Tecoma。
- 公開APIから取得できる画像は8,098枚、合計約1.62GBでした。ページの説明にある15,044枚とは一致しないため、件数差を明記して保留しています。
- 8,098ファイルすべてにAPI記載のファイルSHA-256があり、各クラスから1枚ずつ取得した10枚はSHA-256一致、JPEGデコード成功でした。
- ファイル単位の固定source manifestを`CV_data_artifacts`に保存しました。これは再配布用artifactではなく、公式元データを検証付きで再取得するための台帳です。

## 公開保留の理由

CC BY 4.0の表示だけでは、元画像に含まれる第三者の権利や、8,098枚とページ記載件数の差の理由まで確定しません。また、現時点では本ライブラリ用の固定・整形済みartifactを作成していません。

そのため、現在の正式APIや生徒向けNotebookには追加していません。再配布可能なartifactを作る場合は、クレジット、元画像の権利、クラス名、件数差、全量デコード、固定アーカイブSHA-256を追加確認します。

出典：[公式Mendeley Dataページ](https://data.mendeley.com/datasets/ffysgft2ns/1)
