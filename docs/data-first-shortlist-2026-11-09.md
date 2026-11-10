# データ優先候補の確認表（2026-11-10）

この表は追加データの作業順を決めるための確認記録です。表にある候補は正式カタログ掲載やRelease公開の承認済みではありません。現在、正式な生徒向けデータは5件（トマトの葉、FruitSeg30、SmallFishBD、Pistachio、Food Waste Bangladesh）です。Food Waste v0.1.1は固定Release済みで、API登録をこの変更で反映します。準備済みartifact、権利判断、Release/API公開を別々に扱います。

## 先に残件を解消する候補

| 候補 | 固定元と規模 | 既存作業 | 次に解消すること | 判断 |
|---|---|---|---|---|
| Food Waste Bangladesh | [Mendeley v1](https://data.mendeley.com/datasets/w68f9w6jmm/1)、CC BY 4.0、artifact 633枚。元ZIP 31,426,593 bytes | 人物の一部が写る11枚とQR風表示1枚を除外。5カテゴリ・638ファイルのmanifestとCRCを検証し、固定Release v0.1.1を公開 | ブランド・商品表示は文脈表示で推薦を意味しないこと、撮影カテゴリは廃棄量ではないことを明示。ライブラリAPI登録を反映 | 完了：Release済み、API登録中 |
| Bangladeshi E-Waste Image | [Mendeley v1](https://data.mendeley.com/datasets/77383kmdnw/1)、CC BY 4.0、2,157枚。公式ページのZIPは69.6 MB | 固定ZIP SHA-256、全画像のデコードとコンタクトシート確認、注釈監査、共通artifact v0.1.0の記録あり。polygon注釈は外接矩形へ変換済み | 全体は電子廃棄物だけでなく一般廃棄物も含むため名称・課題説明を調整。画像のブランド名・製品文字の第三者権利を含むため、帰属記録だけで公開承認とせず処理方針を確定する | 技術準備度は高いが、第三者権利 sign-off 待ち |
| Pistachio Image Dataset | [Mendeley v1](https://data.mendeley.com/datasets/h7pf57cgg9/1)、CC BY 4.0、2,148枚 | 画像作成者を述べる関連論文を照合。artifact全2,153ファイルのmanifest・SHA・サイズとCRC検証済み。Release v0.1.0を公開し取得APIへ登録 | 出典・変更・指定論文2件を表示。代表4枚の目視確認で全画像レビューではない点を明記 | 完了：生徒向け固定取得で利用可能 |

## 次の調査候補

| 候補 | 公式情報で確認した内容 | 未完了項目 | 優先度 |
|---|---|---|---|
| GeoSetEnnea | [Mendeley v1](https://data.mendeley.com/datasets/fg97mhsdbr/1)、CC BY 4.0表示、966枚・9クラス・8,253注釈。著者が文具店・図書館などで撮影したと説明。train/valid/testに加えraw・augmented画像を含む | 登録済み技術監査は公開メタデータと6サンプルの確認まで。全量ファイル固定、画像・注釈の全量検査、増強元と分割漏洩、第三者権利、再配布条件を確認する | 検出課題の有力候補 |
| Recyclable Waste Image Dataset | [Mendeley v1](https://data.mendeley.com/datasets/h5pxbsdz4m/1)、CC BY 4.0表示。公開版は作者撮影画像1,000枚との説明。監査記録上、利用可能な画像は989枚 | 既存の縮小全件レビューで包装のブランド表示と包装上の肖像らしきものを確認。別権利の確認がないため保留。元件数との差11件を補完しない | 権利残件が重いため後回し |

## 追加確認候補

| ConMetal-6 subset | [Mendeley v1](https://data.mendeley.com/datasets/ch34f38kz5/1)、CC BY 4.0表示。公開版は全体のtest split 232枚、6種類の金属合金、4,620個のYOLO矩形注釈。著者説明ではメルボルンで撮影し、ラベルは磁石・scratch test・専門家確認で作成 | 公開ファイルの一覧・サイズ・SHA-256、画像・YOLO注釈の実物、第三者権利は未確認。公開版はtest splitのみでtrain/validationは含まれないと説明されているため、訓練用データとしては扱えない | 条件付き候補。学習済みモデルの評価用に限る可能性 |

## 追加確認候補

| Indoor Plant Varieties | [Mendeley v1](https://data.mendeley.com/datasets/ct79299k27/1)、CC BY 4.0表示。1,172枚、7クラス。 | 固定元SHAを照合し全量をデコード。全画像を14枚のクラス別コンタクトシートで確認、完全一致重複10枚を除外。1,159枚のGPS含有メタデータを削除し、512pxへ整形。共通artifact 1,162枚・manifest検証済み。 | 課題と整形完了。Release assetアップロード後にAPI登録 |

## 進行ルール

1. まずFood Waste、E-Waste、Pistachioの既存source manifest・artifact manifest・report・ライセンス記録を照合し、再生成できる資料を再利用する。
2. 画像を再配布する前に、CC BYの表示だけでなく、撮影由来、第三者権利、プライバシー、帰属、改変内容を確認する。
3. 公開保留が解消した候補だけを、CV_data_artifactsの固定Release assetとCV_dataの明示的な固定取得APIへ追加する。
4. 以降は分類・検出・領域分割のバランスを取り、公式固定版・ライセンス・授業で扱える課題を先に机上確認してから大容量取得する。
5. 既存の確認済みデータを優先し、候補50件すべてを全量取得・再監査しない。

## 取得容量の実務上の制約

追加の全量取得・変換を始める前に、一時作業領域の空き容量と必要容量を確認する。元ZIP、展開物、整形artifactを同時に置く余裕を確保し、空きが足りなければ作業前に調整する。
