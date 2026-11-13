# Kuzushiji-MNIST（固定取得・実体監査待ち）

## 何に使うデータか

28×28の白黒文字画像70,000枚を、くずし字10種類に分類するデータです。古典籍などに書かれた文字の形を扱いますが、古文の文章や意味・文法を学ぶデータではありません。地域の古い記録や本をデジタルで整理するとき、切り出した一字を機械で仮分類し、人が確認する補助機能を考える教材に向いています。

このデータだけで古文書のページや文章を読むOCRは作れません。画像は一字ずつで、全文や文字列の正解はありません。まずResNet18などの画像分類モデルで一字分類を試し、予測の間違いを確認する課題として扱います。ページOCRを実現するには、文字の位置を見つけるデータと文章単位の正解を持つ別データが必要です。

## 権利・出典

- 公式固定コミット：[`rois-codh/kmnist` `eb78dc13345cb00a9ced461e9be277f845534dff`](https://github.com/rois-codh/kmnist/tree/eb78dc13345cb00a9ced461e9be277f845534dff)
- ライセンス：CC BY-SA 4.0。公式READMEはデータセット自体にもこのライセンスを示しています。再配布・改変物には指定の帰属表示とShareAlike条件を適用します。
- 指定帰属表示：`"KMNIST Dataset" (created by CODH), adapted from "Kuzushiji Dataset" (created by NIJL and others), doi:10.20676/00000341`
- 参考文献：Tarin Clanuwat et al., “Deep Learning for Classical Japanese Literature,” arXiv:1812.01718.

## 公開状態

ライセンス表記と教材用途は一次情報で確認済みです。一方、公式のデータ取得先は固定Releaseではなく、配布ファイルのSHA-256と実画像の監査も未取得です。固定された整形済みartifactとそのSHA-256を用意するまで、`student_enabled`・取得API・生徒向けNotebookには登録しません。

### 確認済みの公式情報

- [固定コミットのREADME](https://github.com/rois-codh/kmnist/blob/eb78dc13345cb00a9ced461e9be277f845534dff/README.md)：データ規模、タスク、引用方法、ライセンス、帰属表示。
- [公式リポジトリ](https://github.com/rois-codh/kmnist)：Kuzushiji-MNIST、Kuzushiji-49、Kuzushiji-Kanjiの説明。

ページ全体のくずし字OCRに進む場合は、CODHの「日本古典籍くずし字データセット」など、文字位置やページとの対応情報を持つ候補を別件として権利・実体審査します。KMNISTをその代用とはしません。
