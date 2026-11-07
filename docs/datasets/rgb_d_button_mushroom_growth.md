# RGB-D Time-Series Dataset of White Button Mushroom Growth（公開保留）

キノコの個体を画素単位で区別し、成長の時間変化を調べる領域分割課題の候補です。実データが公開APIから取得できないため、現在は教材データとして利用できません。

## 確認できたこと

- [公式Mendeley Data v1ページ](https://data.mendeley.com/datasets/8n6nr43gk3/1)にはCC BY 4.0と表示されています。ページ説明は129件のRGB・深度モザイクとCOCO形式のインスタンスマスクを記載しています。
- 固定版v1の公開APIのファイル一覧は`readme.txt` 1件のみです（4,712 bytes）。ファイルSHA-256は`a39f7231cdc51bc7fb103d3ff319830caa63f4b196f81593124d435b18dd032f`で、APIの値と一致しました。
- READMEにはRGB、Depth、Annotations各フォルダの説明がありますが、画像・深度・COCO注釈ファイルはAPI一覧にありません。
- 画像とマスクのペア、時系列ID、ラベル、画素値、実際のライセンス添付文書は検査できていません。CC BY 4.0のページ表記だけで実データの再配布権を確定しません。

## 判断

対象の境界を色分けして、成長や配置の変化を比べる課題に向く可能性があります。ただし、固定版に実画像と注釈がないため、共通形式変換、ダウンロードAPI、Notebookへの追加、再配布は保留です。公式APIにデータ本体が追加された場合、固定版・SHA-256・画像とマスクの対応・時系列分割・権利を改めて確認します。

詳細な確認記録：[監査JSON](../../reports/rgb-d-button-mushroom-growth-audit.json)。
