# SmallFishBD

## 現在の状態

候補ID：`DS-028`（Mendeley Data v2）  
状態：教材用artifact v0.1.1を固定Releaseで公開しました。10魚種、1,697枚を収録し、CC BY 4.0の帰属・変更表示条件を記録しています。ライブラリAPIへの登録もこの変更で反映します。

- Release：https://github.com/708san/CV_data_artifacts/releases/tag/smallfishbd-v0.1.1
- ZIP：29,799,609 bytes
- SHA-256：`367b332bc0da479e9a708449f45cf7aa10eb190267a6bc1f1a87e5a38ce8f547`
- 固定ダウンロードURL：https://github.com/708san/CV_data_artifacts/releases/download/smallfishbd-v0.1.1/smallfishbd-v0.1.1.zip

## データと整形内容

公式ページは元画像1,700枚（10魚種、320×320 JPEG）と増強画像20,400枚を別々に記載しています。元画像ZIPは29,802,305 bytes、SHA-256 `2d97368d351f4c5940b7b54f19eec2b771a7d76421dbe5ad66977cf3003eafbb`です。[公式データページ v2](https://data.mendeley.com/datasets/8jvxtvz52x/2)。

元画像を固定SHA-256照合後に安全展開し、1,700枚すべてのデコードとクラス枚数を確認しました。完全一致重複3枚を除いた1,697枚を、seed 42でtrain 1,188 / validation 254 / test 255に分割しました。画像の画素は変更していません。増強画像は収録していません。artifactにはCC BY 4.0の出典・変更内容を記した`LICENSE.md`を同梱しています。

## 教材として考えられる使い方

魚の画像を10クラスに分類し、似た魚種による誤分類を調べる課題に使えます。代表画像は青系の背景上に魚が置かれており、背景への依存を学ぶ材料にもなります。一方、背景の偏りや市場名の表記差があるため、自然環境の魚種判定、生物多様性の推定、食品安全性、価格判断には使えません。

増強画像と元画像の対応は全量照合していません。評価にはこのartifactの元画像だけを使い、増強画像を混ぜないでください。

## ライセンスと確認範囲

Mendeley Data v2はCC BY 4.0を表示しています。全画像の視覚レビューを含む再配布審査を行い、帰属・変更表示条件付きで公開しました。具体的な出典と変更表示はZIP内の`LICENSE.md`を参照してください。

確認の詳細：[SmallFishBD v0.1.1 preparation report](https://github.com/708san/CV_data_artifacts/blob/main/reports/smallfishbd-v0.1.1-preparation-2026-11-09.json)、[全画像視覚レビュー](https://github.com/708san/CV_data_artifacts/blob/main/reports/smallfishbd-visual-review-2026-11-08.json)
