# Indoor Plant Varieties（共通artifact準備済み・公開待ち）

## 出典と権利

[Indoor Plant Varieties for Computer Vision Applications, Mendeley Data v1](https://data.mendeley.com/datasets/ct79299k27/1)、DOI `10.17632/ct79299k27.1`。公式ページはCC BY 4.0を表示しています。提供者はSajib Bin Mamun、Md Asraful Sharker Nirob、Dr. Md Taimur Ahad、Mashreka Akter、Pranta Saha、Md Assaduzzamanです。固定ファイル`Orginal Data.zip`（file ID `be73f0a3-d478-4df1-b9d5-513e5879a8ef`）は765,167,460 bytes、SHA-256 `c6e3839666e344ca4bb72fa9b09f36605fe8f972c088f0bba72c5dbe06bde2df`です。

公式説明では2023年にバングラデシュ農業開発公社と近隣苗圃で撮影し、農学者がラベルを確認したとしています。元画像1,172枚、7クラスです。7,000枚の拡張版は取得・収録していません。

## 実画像・プライバシー監査

固定ZIPのSHA-256照合後、安全な展開検査を行い、元画像1,172枚をすべてデコードしました。14枚のクラス別コンタクトシートで全画像を確認し、明らかなクラス違い、人物、個人情報、目立つ第三者表示は見当たりませんでした。これは一覧画像による確認で、全画像を個別に拡大した権利審査ではありません。

完全一致の重複10組を確認し、重複ファイル10枚を除外しました。元画像1,172枚中1,159枚にGPSを含むEXIFがあったため、配布用コピーではEXIFおよびPhotoshop/IPTCメタデータを削除しました。原画像を変更せず、派生コピーを最大512×512に縮小・再エンコードしています。

| クラス | 元画像数 | 配布画像数 |
|---|---:|---:|
| Aglaonema | 187 | 187 |
| Cryptanthus | 150 | 150 |
| Devil’s Ivy | 172 | 172 |
| Heartleaf Philodendron | 158 | 158 |
| N-Joy Pothos | 172 | 162 |
| Rhaphidophora | 166 | 166 |
| ZZ Plant | 167 | 167 |

## 共通形式と利用案

1,162枚を`images/<split>/<class>/`へ配置し、`labels.csv`、`metadata.jsonl`、`classes.json`、`manifest.json`、CC BY 4.0帰属・変更表示を含むライセンス記録を整えました。各クラス内で撮影時刻順に並べ、同一時刻の画像をまとめてtrain 813 / val 175 / test 174に分けています。連続撮影の隣接画像がsplitをまたぐ可能性を減らす意図です。別の株・家庭・カメラへの汎化を測る分割とは限りません。

高校生は「観葉植物の写真から種類を見分ける補助ツールを作れるか」を試せます。クラス間の混同や、撮影場所・背景に頼る予測を調べる題材です。植物名の予測は毒性、病気、健康状態、育て方、安全性の判断には使わないでください。

## 公開状態

共通artifact v0.1.0は124,438,327 bytes、SHA-256 `4f3a83c5eab2e82da95bab64b6de703e31912d03142131285f9fdc3eef73d6e9`です。アーカイブCRC、ファイルmanifest、ライブラリの固定形式・安全展開検証を通過しました。artifactのライセンス記録と全量監査reportは[`CV_data_artifacts`](https://github.com/708san/CV_data_artifacts)の準備PR #21にあります。

GitHub Release assetのアップロードと固定URLの検証が済むまで、正式カタログ・取得APIには登録せず、利用可能なデータとして表示しません。
