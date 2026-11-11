# PUST Cafeteria Food Image Dataset（大学食堂の料理検出）

バングラデシュのPabna University of Science and Technology（PUST）中央食堂で撮影した料理画像から、料理の位置とラベルを見つける物体検出教材です。共通artifactは16クラス、画像691枚を収録しています。元データは複数の料理が盛られた皿を含み、単品写真だけではありません。

## 出典・利用条件

- [Mendeley Data v2](https://data.mendeley.com/datasets/fn6yhzjz83/2)、DOI `10.17632/fn6yhzjz83.2`
- 著者：Marufa Yeasmin、Md. Razu Ahmed、Protiva Rani Kundu、Jannatul Mauya、Md. Shamim Reza
- ライセンス：CC BY 4.0。作者・データ名・出典・ライセンスへのリンクを示し、変更点を記載してください。
- [整形済みartifact Release v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/pust-cafeteria-food-v0.1.0)
- ZIP：36,085,147 bytes、SHA-256 `97def37fae5a2368f4d0ea7bc4cffc0d299173b7581f49ad97bb43d08f496b4f`

## 授業で試せること

画像に写る料理を囲み、ラベルを付ける物体検出を試せます。料理が重なる写真や、複数品が盛られた皿で検出の難しさを比べられます。元データは大学食堂で撮影され、今回のartifactは授業利用に合わせて画像・ラベルを共通形式に整理しています。一部のpolygon注釈は外接矩形へ変換したため、輪郭の細かな形は保持しません。

## クラス

`chaa`、`chola`、`chop`、`daal`、`egg`、`fish`、`mashed_potato`、`matha`、`meat`、`puri`、`rice`、`ruti`、`salad`、`singara`、`vegetable`、`vegetable_roll`。一部は地域の料理名です。日本の料理分類にそのまま当てはまるとは限りません。

## 注意

このデータから、料理の栄養、アレルギー、衛生状態、価格、食べ残し量を判断することはできません。撮影場所は一つの大学食堂で、日本の学校や地域の食堂を代表するデータでもありません。
