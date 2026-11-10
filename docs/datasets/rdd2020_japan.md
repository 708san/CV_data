# RDD2020: Japan road damage subset（artifact準備済み・Release待ち）

- **固定版**：[Mendeley Data Version 2](https://data.mendeley.com/datasets/5ty2wb6gvg/2)（DOI: 10.17632/5ty2wb6gvg.2）
- **公式challenge説明**：[GRDDC 2020 dataset and privacy](https://github.com/556-wangbiao/rddc)
- **データ論文**：[RDD2020 Data in Brief](https://doi.org/10.1016/j.dib.2021.107133)
- **データライセンス**：CC BY-NC 3.0。非商用教育用途に限定。商用利用不可。
- **元ZIP**：1,848,075,315 bytes、SHA-256 `678fb0cd72baa214accf54d44611fffbc348055b0d65fbc0e9744b02d5fa084a`
- **整形artifact**：7,900画像・16,469 bbox、641,514,873 bytes、SHA-256 `f787feead7fd3b0d63f42c7cfb8e3db6f114e57c83b3b928d5f7c58bcb411955`
- **状態**：共通検出形式とmanifestを準備・照合済み。GitHub Release asset未登録、公開API未登録。

## 高校生が取り組める課題

通学路や地域道路のひび・穴を画像から探し、根拠の画像を添えて道路管理者へ相談する課題に使えます。画像は2020年頃に日本で車載スマートフォンを使って撮影されたもので、現在の道路状態や特定地域の代表性を示しません。モデルだけで安全性や修繕順位を決めず、現地確認や管理者の情報と照合します。

## 収録内容と整形

固定版の日本train 10,506画像・XMLをすべて監査しました。画像10,506枚はすべてデコードでき、同名XMLとの画像サイズは全件一致しました。完全一致画像重複とGPSメタデータは0件です。

日本trainのXMLには7コードが含まれていました。元データ論文が道路損傷として説明するD00、D10、D20、D40だけを残し、D43、D44、D50等の追加ラベルだけを持つ画像など2,606枚を対象外にしました。幅0のD20 bbox 1個も除外しました。

| クラスコード | 意味 | bbox数 |
|---|---|---:|
| D00 | 縦ひび | 4,049 |
| D10 | 横ひび | 3,979 |
| D20 | 亀甲ひび | 6,198 |
| D40 | ポットホール | 2,243 |

元JPEGの画素・バイト列は変更していません。Pascal VOC座標を正規化YOLO bboxへ変換しました。train 6,299、valid 802、test 799に画像単位で分割し、分割方法とseedをmanifestに記録しました。撮影系列情報がないため、近接フレームが別splitになる可能性があります。

## プライバシーと利用上の注意

公開元は、明瞭に写った顔や車両ナンバーをぼかしたと説明しています。36枚の接触シートと原寸画像を標本確認しました。公道、住宅、車両、歩行者が写りますが、標本中に明瞭な個人識別情報は見つかりませんでした。全画像を1枚ずつ目視したわけではありません。人物・車・住所を特定する用途に使わないでください。

## 帰属・ライセンス・改変

出典：Deeksha Arya, Hiroya Maeda, Sanjay Kumar Ghosh, Durga Toshniwal, Hiroshi Omata, Takehiro Kashiyama, Toshikazu Seto, Alexander Mraz, Yoshihide Sekimoto (2021), “RDD2020: An Image Dataset for Smartphone-based Road Damage Detection and Classification,” Mendeley Data v2, DOI: 10.17632/5ty2wb6gvg.2.

Mendeley Version 2の表示に従い、**CC BY-NC 3.0**の帰属・非商用条件を適用します。派生artifactは日本trainの選択、4クラスへの絞り込み、対象外画像と幅0 bboxの除外、bbox座標変換、画像splitを行いました。画像の改変はありません。コードのMITライセンスはデータの条件を変えません。

## 配布状況

Release assetとAPI登録はまだ行っていません。Release asset作成後にURL・SHAを固定し、検出APIで明示取得できる状態を確認してから生徒向け一覧へ加えます。
