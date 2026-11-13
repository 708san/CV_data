# GeoSetEnnea（製図用具の物体検出）

製図用具の位置と種類を示す物体検出データです。物体を数える、机や棚の配置を比べるなどに応用できます。ここに挙げた題材以外にも、注釈付き画像で検出方法を試せます。

## 収録内容

- 画像136枚、9クラス、物体位置の注釈1,188件
- train 84枚、validation 22枚、test 30枚
- クラス：コンパス、ディバイダー、消しゴム、鉛筆、分度器、15cm定規、45度・60度三角定規、鉛筆削り
- 固定版：[geoset-ennea-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/geoset-ennea-v0.1.0)
- ZIP SHA-256：`6185c0f8e631ec36913b6c229d4fbd51463d2a4fea1084f3c3e8021244ecd6e3`
- ZIPサイズ：7,531,941 bytes

## 出典・ライセンス

Sakhawat Hossain; Md Sadman Haque; Sadia Islam (2025), “GeoSetEnnea: A Multi-Class Image Dataset for Object Detection of Geometric Tools,” Mendeley Data v1, DOI: [10.17632/fg97mhsdbr.1](https://doi.org/10.17632/fg97mhsdbr.1). Mendeley Dataの公開ページはCC BY 4.0を表示しています。再利用時は作者・出典・変更内容を表示してください。

画像は著者がDhakaの文具店や図書館で撮影したと説明されています。固定版の画像・注釈を照合し、拡張画像、画面キャプチャ、同じ写真の別表現を除いて、撮影元グループ単位で分割し直しました。写真の画素とYOLO矩形は変更していません。詳細は[監査レポート](../../reports/geoset_ennea-v1-audit.json)を参照してください。

文具の商品名・ロゴが一部に写ります。これらはクラスや推薦を示すものではなく、第三者商標の権利は各権利者に属します。

## 使い方

```python
from cvlesson import datasets

data = datasets.get("geoset_ennea")
records = data.to_df()
records[["image_path", "boxes", "split"]].head()
```

## 注意点

撮影場所はバングラデシュで、日本の教室・文具・机を代表しません。机上整理の試作や画像認識の学習に使い、実在する備品の所在・数量を確定する用途には使わないでください。
