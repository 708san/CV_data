# 観葉植物の種類を画像で分類する

## どんな課題に使える？

家や学校で見かける観葉植物を、画像から7種類に分類するデータです。植物を観察して名前を調べる活動や、撮影する角度・明るさ・背景を変えたときに予測がどう変わるかを調べる課題に使えます。

モデルの予測は学習用の参考です。有毒性、食用、病気、育て方、人やペットの安全を判断する用途には使わないでください。このデータはバングラデシュの農業機関や近隣の苗圃で集められた植物を撮影したもので、日本の家庭や学校にある植物全体を代表するものではありません。

## データの内容

- 7種類、1,162枚
- train 813枚、validation 174枚、test 175枚
- 各クラス内でseed 42を使い、およそ70/15/15に分割
- 元画像から完全一致重複10枚を除外し、長辺512px以下へ縮小
- GPSを含むEXIF等の画像メタデータを除去

## 取得

```python
from cvlesson import datasets

data = datasets.get("indoor_plant_varieties")
print(data.classes)
print(data.class_names_ja)
print(data.splits)
data.show_examples(8)
```

最初の取得では約71MBをダウンロードします。データはリポジトリの外にあるキャッシュへ保存されます。

## 出典とライセンス

Mamun, Sajib Bin; Nirob, Md Asraful Sharker; Ahad, Md Taimur; Akter, Mashreka; Saha, Pranta; Assaduzzaman, Md (2024), “Indoor Plant Varieties for Computer Vision Applications: A Diverse Image Dataset,” Mendeley Data v1, DOI: [10.17632/ct79299k27.1](https://doi.org/10.17632/ct79299k27.1).

配布元はCC BY 4.0を表示しています。作者・出典・変更内容を表示してください。配布画像は重複を除外し、縮小・再保存し、画像メタデータを取り除いています。

元画像1,172枚を全量デコードしました。56枚（各クラス8枚）の見本を一覧で確認しましたが、全画像を人手で目視したわけではありません。詳細は[監査レポート](../../reports/indoor_plant_varieties-v0.1.0-audit.json)を参照してください。
