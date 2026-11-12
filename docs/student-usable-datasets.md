# 生徒課題向け新規データ候補20件と初期採用6件

更新日：2026-11-13

この一覧は、新規の外部候補20件と初期採用データ6件をまとめた選定記録です。**20件は候補調査の目標で、26件すべてが取得APIに登録済みという意味ではありません。** 新規20件の目標に初期採用データは含めていません。CC BYは帰属表示、CC BY-NCは非商用条件を付けます。

現在の生徒向けAPIには、権利・課題適性・固定Releaseを確認して登録したデータが22件あります。正確な一覧は`datasets.list_available(audience="student")`と[README](../README.md)を参照してください。初期採用6件に加え、後日登録したデータはREADMEと開発進捗に記録しています。この候補表は実際の公開状態を置き換える台帳ではありません。

新規20件の候補では、Tokyo Hawkeye 2020は用途に合う一方、公式ZIPがAccessDeniedのため取得・整形をスキップしました。残る各候補の実体監査・権利状態は候補台帳と個別監査記録で確認し、課題適性と権利が揃ったものだけを正式APIへ登録します。候補の画像・注釈が確認できない場合は、別ソースの候補で目標数を補います。

| # | データセット・ライセンス | 生徒が扱う困りごとと画像モデルの役割 |
|---:|---|---|
| 1 | [Receipt Detection Dataset for YOLO v3](https://data.mendeley.com/datasets/3bgwtdmdjs/3) — CC BY 4.0 | 家庭・部活のレシートを自動で見つけて切り出し、家計簿入力の最初の手順を補助。金額読取は別OCRが必要 |
| 2 | [Japanese Receipt Image Dataset (Detailed)](https://huggingface.co/datasets/IngCrowd/japanese-receipts-detailed) — CC BY-NC 4.0、100枚 | 文化祭・部活動の会計で日付・合計などを候補入力し、会計係が原本と照合。PIIマスクは一部のみ、非商用 |
| 3 | [DIU-HandGesture31](https://data.mendeley.com/datasets/yby56bk2wm/1) — CC BY 4.0、31種・原画像5,389枚 | タッチ操作が難しい人や手が塞がる場面で、ジェスチャーによる簡単な機器操作を試作。手話翻訳ではない |
| 4 | [Fire Recognition Image Dataset v4](https://data.mendeley.com/datasets/7jk6xh7h6w/4) — CC BY 4.0、火・煙など4分類 | 火・煙の候補を知らせ、周囲の人が警報・避難手順を確認する補助 |
| 5 | [Plant Leaf Freshness and Disease Detection v3](https://data.mendeley.com/datasets/n67gctmjyj/3) — CC BY 4.0、6作物12,643枚 | 学校・地域菜園で葉の異常候補を知らせ、担当者が葉や栽培環境を点検 |
| 6 | [AgriFreshNET](https://data.mendeley.com/datasets/42m5tb7yv9/1) — CC BY 4.0、24クラス14,500枚 | 家庭や学食で先に使う青果の候補を考える。残存期間は目安として人が現物確認 |
| 7 | [Indoor Waste Image Dataset](https://data.mendeley.com/datasets/dy7smxr93r/1) — CC BY 4.0、4,000枚 | 学校行事後に床・室内に残ったごみの場所を示し、清掃箇所の確認を補助 |
| 8 | [WasteSegCluster v4](https://data.mendeley.com/datasets/3wnf3n242s/4) — CC BY 4.0、1,947枚・約3,900領域 | 水辺清掃でごみの位置・種類を記録し、回収活動を計画。日本の水辺では現地写真で確かめる |
| 9 | [E-Tadweer Image Dataset](https://data.mendeley.com/datasets/bndsgcspbx/1) — CC BY 4.0、6,269枚 | 学校の電子機器回収で品目を記録し、担当者が回収先を案内。日本の廃棄規則は別に確認 |
| 10 | [Fire Extinguisher](https://data.mendeley.com/datasets/bzhmmfymsb/1) — CC BY 4.0、668枚 | 防災学習で消火器を画像から見つけ、校内防災マップを点検。使用可能状態は人が確認 |
| 11 | [Navigation Assistance for the Visually Impaired using YOLOv11](https://data.mendeley.com/datasets/m68g3h7p87/1) — CC BY 4.0、8,114枚・22クラス | 歩道の障害物等を知らせる移動支援を試作。当事者の評価と人の支援を前提にする |
| 12 | [Tokyo Hawkeye 2020 Pedestrian Dataset](https://github.com/sekilab/TokyoHawkeye2020) — データ自身がCC BY-SA 4.0と表示、東京の高所撮影画像・歩行者頭部座標 | 渋谷などの混雑した交差点で歩行者数を推定し、通行の混み具合を共有する試作。学校行事への直接利用は未確認。公式アーカイブが403のため取得・整形をスキップし、ライブラリ未登録 |
| 13 | [Pothole Videos v3](https://data.mendeley.com/datasets/5bwfg4v4cd/3) — CC BY 4.0、619本・各48フレーム | 通学・生活道路の穴を領域分割し、場所と画像を添えて道路管理者へ報告 |
| 14 | [NNVN25](https://data.mendeley.com/datasets/x33jnyf5wh/1) — CC BY 4.0、17,165画像・136商品 | 学園祭の売店で缶・瓶の在庫を数え、販売後の容器回収を計画。商品名・ブランド判定は目的にしない |
| 15 | [Food Packaging OCR Dataset](https://data.mendeley.com/datasets/3cpx2fmn3r/1) — CC BY 4.0 | 家庭の食品管理で包装の期限表示を探して候補を記録し、使う順を考える補助 |
| 16 | [AgriShelf v4](https://data.mendeley.com/datasets/s3vc2552sf/4) — CC BY 4.0、16,592画像 | 学園祭・部活売店の棚を撮影し、品切れや陳列数の確認を補助 |
| 17 | [FPVCrosswalk2025](https://data.mendeley.com/datasets/mcr2jwk5bp/1) — CC BY 4.0、実写300枚＋合成3,000枚 | 視覚障害者向け歩行支援として横断歩道の位置を示す。合成・実写の差を分けて評価 |
| 18 | [FootpathVision](https://data.mendeley.com/datasets/szkhrh8dc8/1) — CC BY 4.0、1,238枚 | 歩道の露店・駐車等で通りにくい場所を記録し、地域の歩行環境改善を相談。YouTube由来フレームも含む |
| 19 | [Automatic Waste Management Dataset](https://data.mendeley.com/datasets/d4vsy9c9wk/1) — CC BY 4.0、909枚・5分類 | 学校行事のごみ回収で紙・生ごみ・革・プラスチック・ガラスの候補を表示し、担当者が分別 |
| 20 | [Meal images and carbohydrate content per meal](https://data.mendeley.com/datasets/98kpkwy698/1) — CC BY 4.0、240枚 | 糖尿病のある人の食事記録で炭水化物量の目安を画像から補助。食事画像のみの120枚を対象にし、医療判断や投薬量には使わない |

## 初期採用の6件

この6件は初期採用候補として選んだデータです。新規外部20件とは別枠で数えます。現行APIでの公開状態は上記の正式一覧で確認してください。

| # | データ・ライセンス | 生徒が扱う困りごとと行動 |
|---:|---|---|
| 21 | [RDD2020 Japan](datasets/rdd2020_japan.md) — CC BY-NC 3.0 | 通学・生活道路の損傷候補を検出し、場所と画像を道路管理者へ報告 |
| 22 | [LeFood-Set](datasets/lefood_set.md) — CC BY 4.0 | 学食・家庭の食べ残し量を比べ、盛付けや献立の改善を検討 |
| 23 | [Tomato leaves](datasets/tomato_leaves.md) — CC0 1.0 | 学校・地域菜園で異常候補を見つけ、栽培担当者が葉や環境を確認 |
| 24 | [FabricSpotDefect](datasets/fabricspotdefect.md) — CC BY 4.0 | 洗濯・補修前に汚れ候補を見つけ、本人が洗い方や補修を確認 |
| 25 | [Orange Fruit](datasets/orange_fruit.md) — CC BY 4.0 | 傷みの可能性がある果物を人に確認してもらい、先に使う候補を考える |
| 26 | [Fresh and Rotten Fruits](datasets/fresh_rotten_fruits.md) — CC BY 4.0 | 果物の状態候補を示し、保管・使用順を人が確認 |

## 追加候補の選定ルール

- 既存カタログのデータを新しい件数に混ぜない。
- 上表のライセンスは配布元に表示された条件。CC BYは出典・ライセンス・変更を記載し、CC BY-NCは非商用条件も明示する。
- 生活・地域の課題に結び付く利用者と次の行動を説明できるデータを選ぶ。
- 危険性がある題材も、確認・報告・案内など人の判断を助ける用途なら候補にする。モデル単独で避難・食用・服薬・決済を決めさせない。
- 次工程では、配布元の固定版、ダウンロードURL、SHA-256を先に確定し、候補の重複・容量・注釈形式を確認して取得する。
