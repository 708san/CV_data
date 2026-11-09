# Pistachio Image Dataset（artifact準備・公開保留）

## 出典と権利確認

[Mendeley Data v1](https://data.mendeley.com/datasets/h7pf57cgg9/1)、DOI `10.17632/h7pf57cgg9.1`。公式ページはCC BY 4.0と表示し、KirmiziとSiirtのピスタチオ試料を高解像度カメラで撮影した2,148枚と説明します。MendeleyのcontributorはMurat Kokluです。

出典が引用を求める論文は、Ozkan・Koklu・Saracoglu (2021, DOI `10.23751/pn.v23i2.9686`) と Singhほか (2022, DOI `10.3390/electronics11070981`) です。2021年論文ページは論文自体をCC BY-NC 4.0と表示し、画像取得方法を説明しています。論文ライセンスとデータセットページのCC BY 4.0表示を同一の許諾として扱わず、論文PDFや図表はartifactに含めません。画像権利者・第三者権利について公開前の追加確認が必要なため、正式配布は保留しています。

## 全量技術監査

- 固定v1のZIPは27,859,492 bytes、SHA-256 `140760707018b7f53d91a86a1d7be96d92b1a0d26a75690ab9280ed1170df895`。照合後に安全展開しました。
- ZIPは2,164エントリ、2,158ファイルです。画像2,148枚のほか、特徴量表と引用文書など非画像ファイル10件を含みます。artifactへは画像のみを収録しました。
- 2,148枚すべてJPEG、600×600、RGBとしてデコード成功。完全一致重複0件。
- クラスはKirmizi_Pistachio 1,232枚、Siirt_Pistachio 916枚です。代表4枚を目視し、黒い背景上にピスタチオ試料を1つずつ写した画像でした。全画像の人手確認ではありません。

## 共通artifact v0.1.0

固定画像の画素は変更せず、`images/<split>/<class>/`に配置し、`labels.csv`・`metadata.jsonl`・クラス別seed 42のtrain/val/test分割を追加しました。train 1,503、val 322、test 323。artifact manifestの検証に成功しています。

ローカルZIPは25,875,554 bytes、SHA-256 `32bc15c4788052207e3dd52d4450cc15fec9efade3df169d59bb94556d715f24`。2,153ファイル（2,148画像とラベル・説明類）です。Gitには画像を収録せず、Releaseも作成していません。

## 高校生向け課題

「似た見た目のピスタチオ2種類を画像から分類できるか」を試し、クラス不均衡、画像数、背景が固定された条件の影響を比較できます。正解率だけでなく、混同行列とクラス別再現率を見ます。品質・鮮度・安全性・販売価格を判断する用途ではありません。

## 記録

source manifest、artifact manifest、監査report、帰属・引用記録は`CV_data_artifacts`に保存しています。第三者権利の追加確認と最終配布承認が済むまでAPI・Releaseへ追加しません。

## 2026-11-09 権利・成果物再確認

Mendeley Data v1はCC BY 4.0を表示し、投稿者Murat Kokluと高解像度カメラで撮影した試料画像であることを示しています。帰属表示に加え、元ページが求める2論文を引用する条件で再配布を確認済みにしました。論文PDFや図表はartifactに含めず、論文自体に表示されたCC BY-NC条件を画像のライセンスと混同しません。

ZIPを再照合し、2,153ファイルすべてのmanifestサイズ・SHA-256一致、CRC成功を確認しました。ZIP SHA-256は `32bc15c4788052207e3dd52d4450cc15fec9efade3df169d59bb94556d715f24`。Release assetがないため、ライブラリからはまだ取得できません。
