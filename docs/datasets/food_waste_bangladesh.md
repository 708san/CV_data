# Food Waste Bangladesh

## 現在の状態

候補ID：`DS-021`（Mendeley Data v1）  
状態：教材用artifact v0.1.1を固定Releaseで公開し、取得APIに登録しました。633枚・5カテゴリです。CC BY 4.0の帰属・変更表示を同梱しています。

- Release：https://github.com/708san/CV_data_artifacts/releases/tag/food-waste-bangladesh-v0.1.1
- ZIP：30,760,217 bytes
- SHA-256：`bcbd7fe1f2b8d37a1b86952d59987b1067cdc55c0099199eee0217a4f805c57d`
- 固定ダウンロードURL：https://github.com/708san/CV_data_artifacts/releases/download/food-waste-bangladesh-v0.1.1/food_waste_bangladesh-v0.1.1.zip

## データと整形内容

公式ページは645枚のJPGを5つの撮影場面フォルダに分け、飲食店、ビュッフェ、結婚式などで撮影したと説明しています。Mendeley Data v1はCC BY 4.0を表示しています。[公式データページ](https://data.mendeley.com/datasets/w68f9w6jmm/1)。

元ZIP（31,426,593 bytes、SHA-256 `10e7a106a1f4570f404f93f8fa5c523c53f837f5e3f70981c8a06c02b7080e14`）を照合後に安全展開し、645枚すべてのデコードと全画像コンタクトシート確認を行いました。人物の一部が写る11枚とQRコード風表示のある1枚を除外し、残る633枚をseed 42でtrain 442 / validation 95 / test 96に分割しました。画像の画素は変更していません。商品名やロゴが一部の食器・容器に残っていますが、ブランドや会場の推薦を意味しません。

| 撮影カテゴリ | 枚数 |
| --- | ---: |
| ビュッフェ | 90 |
| 一般 | 146 |
| レストラン | 72 |
| 野菜 | 16 |
| 婚礼 | 309 |

## 教材として考えられる使い方

写真を撮影カテゴリへ分類し、クラス数の偏りや、背景・容器・撮影場面への依存を調べる演習に使えます。ラベルは撮影フォルダ名であり、食品廃棄量、費用、発生率や店舗の実績を表しません。連続撮影が同じ分割に入る可能性もあるため、現実の廃棄傾向を推定する用途には使えません。

## ライセンスと確認範囲

Mendeley Data v1のCC BY 4.0表示、提供者の撮影説明、全645枚のコンタクトシート確認を記録しました。部分的に人物が写る画像は除外しました。ブランド表示が残る画像は撮影場面を示す文脈であり、推奨・承認を示すものではありません。帰属表示と変更内容はZIP内の`LICENSE.md`を参照してください。

監査記録：[全量監査レポート](../../reports/food_waste_bangladesh-v0.1.1-full-audit.json)、[成果物側の利用条件とmanifest](https://github.com/708san/CV_data_artifacts/tree/main/licenses)
