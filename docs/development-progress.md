## 2026-11-11：Fresh and Rotten Fruits 全量監査・整形

- Mendeley Data v1のCC BY 4.0表記、著者撮影の説明、農業機関の専門家によるラベル確認の説明を一次情報で確認。
- 固定Original Image.zip（2,794,170,228 bytes、SHA-256 `f89d67d4c4b24810bcd8406db877db6b1ac9834cea0b0cb56d65acebe59e66ff`）のみを取得。ZIP安全性・CRCを確認し、3,200枚を全件デコード。
- 7枚の完全一致重複を除外。残る3,193枚を最大辺512pxのJPEGへ再符号化し、メタデータを削除。16クラスごとにseed 42で分割。
- 64枚の代表画像を目視し、人物・ロゴ・無関係な写り込みは見つからなかった。全画像の目視レビューではないことを記録。
- 共通artifact v0.1.0は151MB、ZIP SHA-256 `1ca92043fbb0ebbf86ddac5fec2c264e39151ab0d9def1b618002772d9b182eb`。manifest・全ファイルSHA・cvlesson分類形式を検証済み。
- 食品ロスを考える題材として登録案を作成。研究ラベルは食用可否・健康・食品安全を示さないと説明。Release assetを公開URLから再取得し、サイズ・SHA-256一致を確認。CV_data PR #44に取得API登録を追加。
- 詳細：[Fresh and Rotten Fruits](datasets/fresh_rotten_fruits.md)、[全量監査JSON](../reports/fresh_rotten_fruits-v1-full-audit.json)。

# 開発進捗

## 2026-11-13：空画像と翌日の天気データの準備

- ユーザー提供ZIP（10,014,296 bytes、SHA-256 `c30cf675819fea9b0bad62e0d0c8cb77890b808253e92c604b39d6c97a6f5280`）を固定し、安全なZIP構造・CRC・全1,000 JPEGの224×224デコード・ラベルと画像参照を確認。5枚を代表目視。
- 晴れ664・曇り184・雨152、train 656 / validation 161 / test 183。日付単位でsplitをまたがないこと、翌日ラベル規則、split比率の大きな差を確認。
- データカードとOpen-Meteoのデータライセンス・サービス利用条件を区別し、CC BY 4.0帰属・変更表示と無料APIの非商用条件を記録。上流画像データの完全な固定revisionは提供ZIPに記録されていない。
- 画像を改変せず、`images/<split>/<class>/`、`labels.csv`、`metadata.jsonl`、manifestへ整形。ZIPは10,014,277 bytes、SHA-256 `c438ca3444bf72773d4a7bb430ed3f20885db8fbb0fd5d3f00ee7727149564e0`。
- `datasets.to_df()`に型付き追加列を出す実装と、`datasets.info/list_available`で型を表示する実装を追加。日本語データ説明・カタログ・モデル対応表を更新。
- Colorado州Goldenの1地点・ERA5再解析値で日本の地域予報に使えないこと、固定MST、test側の雨比率が高いことを記載。
- CV_data_artifacts PR #49をmainへマージ済み。Release assetの再取得でサイズとSHA-256が一致。CV_data PR #64のAPI・説明・一覧変更はPR #63のhead branchへマージ済み。取得可能件数23件となる変更はPR #63でmainへマージ済み。データのColab実取得は未確認。


## 2026-11-13：LoRA生成Notebookのモデル情報エラー

- Colabで`model["capabilities_ja"]`がKeyErrorになった原因は、Notebookがその項目を返さない旧commit `635fa30db261ae5b3d43ab87c9e5f9e66a78bd1a`をインストールしていたことでした。
- PR #63の固定commit `940ae09babebc698563b7cf3a35bd842840388f5`では`loras.list_models()`が`capabilities_ja`を返すことを確認し、Notebookの固定参照を更新しました。
- Notebookのコード実行とSDXL生成はColab T4で未再確認です。


## 2026-11-13：分類Estimatorのpredict_proba型エラーを修正

- Colabの`predict_proba()`がNumPy配列を`torch.softmax()`へ渡してTypeErrorになったため、softmax前にTensorへ変換する修正を追加。
- モデル重みを取得しないテストで、Tensor変換とクラス軸ごとの確率正規化を確認。
- ResNet分類・回帰はscikit-learn風Estimator、OCR・検出・領域分割・画像生成は用途別のload/predict/generate APIであることをクイックスタート等へ追記。PyTorchはResNet等の内部で利用し、標準の学習導線では利用者が学習ループを書く必要はありません。
- Python 3.13で全85テスト成功（16件skip）、`git diff --check`成功。ユーザーが修正版の分類NotebookをColabで実行し、`predict_proba()`を含む分類フローを確認済み。回帰Notebookも正常に動作したと確認済み。他機能のColab再確認は未完了。

## 2026-11-13：Colabの日本語Glyph警告に対応

- Colabで`japanize-matplotlib`の導入は成功したものの、`show_examples()`のタイトルが豆腐表示になり、Glyph警告が出ることを確認。
- 日本語フォント名のrcParams設定だけに依存しないよう、IPAexGothicのフォントファイルを取得し、Matplotlibの`FontProperties`として各タイトル・検出注釈へ明示的に渡す修正を追加。フォントファイルの欠落時は理由が分かるエラーを返す。
- フォント設定の呼び出しとフォントパス・ファミリー指定をmock testで確認。Notebook関連を含む10テスト成功。Colab上での描画再確認はこれから。

## 2026-11-13：Notebook変数の静的点検と日本語Matplotlib表示

- 全配布Notebookを横断点検し、分類Notebookで`frame = data.to_df()`を作っている一方、次セルが未定義の`df`を参照する問題を見つけて修正。
- 標準ライブラリだけを使うNotebook検査を追加。JSON/Python構文、セルをまたぐグローバル変数、pip行の引用符、固定Git commit SHA、`cvlesson` importより前のインストールを検査します。アーカイブ用の`notebooks/reference`は授業用CV Notebookではないため対象外。
- `display` extraに`japanize-matplotlib`を加え、`DatasetBundle.show_examples()`実行時に日本語フォントを自動設定。コアimport時は読み込まず、表示に必要なpandasも`display`へ含めて導入を一つにしました。
- Python 3.13で全84テスト成功（16件skip）。Notebook検査、`git diff --check`成功。japanize-matplotlibとMatplotlibが環境にないため、実描画・日本語字形・Colabでの表示確認は未実施です。ruff/pyflakesはネットワークDNS制限で取得できなかったため、標準ライブラリの静的検査を使用。

## 2026-11-13：分類Colabインストール行の引用符を修正

- Colab実行ログで`classification_v1.ipynb`の`%pip install`行末に閉じ引用符がないことを確認。シェルがEOFで失敗し、続く`cvlesson` importも失敗していました。
- PEP 508直接参照を二重引用符で囲み、全Notebookのpip install行で引用符の対を検査しました。Notebook JSON・Pythonセル構文・`git diff --check`は成功。
- 修正をPR #63へ反映します。NotebookのセルはColabで再読み込みし、インストールから再実行してください。

## 2026-11-13：分類・回帰・推論Notebookを実データ対応に更新

- `notebooks/cv/classification_v1.ipynb`は独自CNNから`ResNetClassifier`に変更。固定Releaseのトマト画像でtrain/validation/testを分離し、`fit`、`score`、`predict`、`predict_proba`を実行する流れを追加。見出し・授業順・記入欄は維持。
- `notebooks/colab/resnet_regression_smoke_test.ipynb`を追加。LeFood-Setの食前・食後画像ペアで`ResNetRegressor`を学習し、validation/testのR²と実測/予測を表示。研究データの限界、CC BY 4.0、単位を記載。
- OCR NotebookにCC BY-NC 4.0の公開実レシート1枚の推論を追加。残存情報の可能性と非商用条件を明記し、部分注釈のため全文精度を自動計算しません。
- DETR/SAM NotebookにFruitSeg30の固定test画像・マスクを追加。GT maskから作る矩形をSAMへ渡して1画像IoUを表示します。promptに正解情報を使うことと、全体性能評価ではないことを明記。
- SDXL/LoRA NotebookでImage-to-Image入力を合成画像か利用者のColabアップロード画像から選べるようにしました。ライブラリが画像を別サービスへ自動送信しない旨も記載。
- [クイックスタート](quickstart.md)に実行Notebook一覧、環境、実データ、権利・注意点を追加。
- 全NotebookのJSONとコードセル構文を確認。Python 3.13で79テスト成功（Pillow、pandas、表示extra不足により16件skip）、`git diff --check`成功。Colabでのデータ取得、学習、モデル推論、実データIoUは未実施。

## 2026-11-13：Colabで利用者自身の画像を試す手順を追加

- 仕様0.12に、利用者がColabへ明示アップロードした画像をローカルパスで使う要件を追加。ライブラリは画像を外部へ自動送信せず、リポジトリにも複製しません。
- [クイックスタート](quickstart.md)にローカルファイルとColabアップロードの両方を追加しました。以降は同じモデルAPIを使います。
- [DETR/SAM Colab Notebook](../notebooks/colab/vision_smoke_test.ipynb)で、自分の画像をアップロードする方法と合成画像を使う方法を選べるようにしました。SAMの入力矩形は画像サイズに合わせます。
- Notebook JSONと8コードセルのPython構文、`git diff --check`、`compileall`を確認。Python 3.13の79テストは成功し、16件はPillow/pandasがない環境のためskip。Colab上の新しいアップロード・表示API・Pillow入力での実モデル推論は未実行です。

## 2026-11-13：データ形式・画像入力・汎用利用例を整理

- 生徒向けデータ22件を5タスクに再集計し、`to_df()`、`to_torch_dataset()`、ResNet/OCR/DETR/SAM/SDXLの入出力を実装と照合。`docs/data-model-compatibility.md`に全ID、列形式、接続例、未対応範囲を整理しました。
- 仕様0.10で結果描画の入出力と動作契約を追加し、`cvlesson.display.render/show/save`を実装。OCR文字枠、検出枠とラベル、SAM半透明マスク、検出＋SAMの組を合成画像にできます。Pillow Imageを返し、指定先へ保存できます。モデル本体の入力形式は変更していません。
- 仕様0.11で画像パスとPillow Imageを共通入力に定義。ResNet、OCR、DETR、SAMにPillow Image入力を追加。OCRは内部一時PNGを推論後に削除し、OCR extraへPillow依存を追加。NumPy配列は入力対象外。
- 課題を固定しない[クイックスタート](quickstart.md)と、目的別インストール表を追加。READMEとデータ・OCR・vision・ResNet案内を更新。
- Python 3.13でネットワーク不要テスト79件成功（5件skip）。Pillow 13.0・NumPy 2.5.4を`/tmp/cvlesson-image-input-test-deps`だけに入れ、画像型、変換、OCR一時ファイル削除、描画・保存を確認。`git diff --check`成功。テスト後に一時依存を削除。
- Colab上でのPillow直接入力・新しい表示API、実モデルを使った入力確認、各OSの日本語フォント表示は未確認。日本語フォントがない環境では文字列を枠に描けない場合があります。

## 2026-11-13：Colab T4でDETR成功、SAM品質スコア確認を修正

- ユーザーのColab T4でDETRが`kite`を0.706で検出。SAMの重み取得と読込、マスクshape・bool型の検査も通過しました。
- SAMの品質ヘッド値に対するNotebookの0〜1範囲assertionのみ失敗。仕様0.9.1で値は実IoU・確率ではなく範囲保証のない予測値と明記し、API説明も更新。Notebookは有限値のみ確認するよう修正しました。
- ネットワーク不要テスト69件成功（7件skip）。0〜1を超えるSAMスコアをAPIがそのまま保持するテスト、Notebook JSON/Python構文を確認しました。
- ユーザーが更新したSAMセルをColab T4で実行し、マスクの重ね合わせ画像を確認しました。DETR検出とSAMマスク生成の主要フローは確認済みです。実データの精度評価、CPU・他OS・他GPUは未確認です。

## 2026-11-13：OCR依存競合を修正し、Colab CPUで実モデル推論を確認

- Colabの導入ログで、PaddleX 3.1.4がLangChain 1.xと非互換な旧APIを参照して`langchain.docstore`で失敗することを確認。OCR extraをLangChain `<1`、Hugging Face Hub `<3`、Requests `<2.33`に制約し、Colab既存依存との競合を抑えました。
- OCRライブラリ欠落とPaddleOCR内部依存のimport失敗を異なるエラー案内にしました。Notebookと導入文書も更新しました。
- Colab Python 3.13 CPUで実モデルを読み込み、合成英数字画像から`TOTAL 1280 JPY`を1行として認識。信頼度0.993、四点ポリゴンを含む共通結果を返すことをユーザー環境で確認しました。
- Python 3.13のネットワーク不要テスト69件成功（7件skip）。日本語実画像の認識品質、GPU、他OSでの動作は未確認です。
- 詳細：[OCRの使い方](ocr.md)、[インストール](installation.md)、[Colab Notebook](../notebooks/colab/ocr_smoke_test.ipynb)。

## 2026-11-13：Colab実モデル確認Notebookを準備

- DETR/SAM用GPU Notebookと、日本語OCR用CPU Notebookを別々に作成しました。どちらもテスト画像をNotebook内で合成し、データや個人写真を取得しません。
- ライブラリのインストール元は固定コードcommit `a7bc2c524c3ed944fdc1901b3968479dfffe1f28`です。OCR用はCPU版PaddlePaddleを別ランタイムへ導入します。
- Notebook JSON、Pythonセル構文、固定Git依存表記を確認しました。Colabでモデル取得・推論を実行した状態ではありません。
- [DETR・SAM Notebook](../notebooks/colab/vision_smoke_test.ipynb)、[OCR Notebook](../notebooks/colab/ocr_smoke_test.ipynb)。

## 2026-11-13：DETR検出・SAM領域分割APIを追加

- 仕様0.6で既定モデルをDETR ResNet-50とSAM ViT-Bに固定し、モデルカードのApache-2.0表示、完全なrevision、容量、入力・出力範囲を記録しました。別モデルは完全な40桁revisionを必須にして指定できます。
- `cvlesson.vision.load_detector()`と`load_segmenter()`を実装。CPUが既定で、GPUは明示指定・事前確認します。COCO英語ラベル付きbbox、元画像サイズの真偽値マスク、品質スコアを共通型で返し、DETR枠をSAMへ渡すメソッドも追加しました。
- `vision` extra、インストール手順、初心者向けガイドを追加。モデル取得はload時のみで、重みはGit/PyPIに含めません。
- vision APIのテストを8件追加。Python 3.11/3.12/3.13でネットワーク不要テスト66件が成功（各7件skip）。wheelを構築・一時領域へインストールし、optional依存を読み込まない軽量importとバイナリ非同梱を確認しました。
- DETR/SAM重みの取得・CPU/GPU推論とColab T4は未実施です。PR #63のコミット`56bd58f`とSAM互換修正`a7bc2c5`に対するGitHub Actionsは成功しました。実環境検証待ちとして公開準備完了とは扱いません。
- 仕様・説明：[仕様書](specification.md)、[検出と領域分割](vision.md)、[インストール](installation.md)。

## 2026-11-13：PP-OCRv5日本語OCR APIを追加

- 仕様0.4でOCRの既定モデル、固定取得revision、日本語設定、CPU既定・GPU明示選択、共通結果形式、PaddlePaddle別導入を決定しました。
- `cvlesson.ocr.load()`がPP-OCRv5 mobile検出・認識モデルをHugging Faceの固定revisionから明示取得し、`OCR.predict()`が行テキスト・信頼度・四点座標を返す実装を追加しました。別モデルはローカルディレクトリを指定します。
- OCR用optional extra、CPU/GPU導入案内、初心者向け利用例とモデルカード・ライセンス情報を記載しました。モデル重みはGit/PyPIへ含めません。
- fake backendによる固定revision・結果変換・GPU拒否・基本importのテストを追加。Python 3.11、3.12、3.13で58テスト成功、各7件は未導入optional依存が理由でskipです。
- Python 3.11でwheelを構築して一時targetへインストールし、データ一覧の表示とOCR/Paddle/Hugging Face依存を読まない基本importを確認しました。wheelにモデル・画像バイナリがなく、古い`build/`から混入した未追跡`weights.py`もクリーンビルドで除外されることを確認しました。
- OCR実モデルのダウンロード・CPU推論・Colab T4/GPU推論は未実施です。PaddleOCR/PaddlePaddleの各OS・Python・CUDA組み合わせも実機未確認です。
- 仕様・使い方：[仕様書](specification.md)、[OCRの使い方](ocr.md)、[依存関係と導入](installation.md)。

## 2026-11-11：合成日本語レシートOCR候補を整形

- 取得前にAlpha10限定CC BY 4.0の許諾、合成データであること、文化祭・部活動の支出整理への適合を確認。日本の高校生の課題に結び付かないインド硬貨は採用対象外と台帳に記録。
- 固定revision `c82efda5b823494424e6bc6e9ae7577396ded908`の画像10枚と公開source JSON10件をSHA-256照合し、全画像を視覚確認。元画像の画素は保持。品目・数量・金額・合計額を共通CSV/JSONLへ整理。
- OCR全文の正解文字列はないため、文字誤り率の評価データとは呼ばず、構造化項目の照合見本として記録。個人情報相当のsource metadataは共通artifactへ含めない。
- 整形artifactは860,275 bytes、SHA-256 `0c9739f12f11ea22c44afa5f2a5a151bf389badb9bc6ce4534dc956b9a8b8f4d`。manifest・source inventory・権利記録・変換スクリプトを準備。Release asset未公開のため、生徒向けAPIは18件のまま。
- 詳細：[候補説明](datasets/japan_ocr_receipts.md)。artifact側はPR準備中。

## 2026-11-11：Orange Fruitを権利確認・整形・公開

- 取得前にMendeley Data v2のCC BY 4.0と、外観カテゴリを使った分類・食品ロス課題の試作への適合を確認。鮮度・食用可否・食品安全・病気の判定には使わない条件を設定。
- 固定元ZIP（110,185,722 bytes、SHA-256 `b486ee40af7316c4603d3d8354a636a7bc859c500beb126b3577ef79bf3f75e7`）と内側ZIP（112,489,867 bytes、SHA-256 `03d43104a0c6eda6681c23415bec8fe404ff6c919d44de35b247bb9b72105251`）を記録。全15,000画像をデコードし、224×224、完全一致重複0を確認。
- 各クラスの代表画像を確認。背景・照明・角度の違いは課題に活かし、些細な写り込みだけを理由に除外しない。
- 画素を変えず、5クラス各3,000枚をseed 42でtrain/validation/test（各2,100/450/450）に分割。
- CC BY 4.0の出典・変更表示と用途上の注意を同梱し、固定Release `orange-fruit-v0.1.0`を公開。artifact台帳PR #39をCI成功後に統合し、サイズ・SHA-256をGitHub側で照合。
- 生徒向けAPIは18件、目標20件まであと2件。詳細は[データ説明](datasets/orange_fruit.md)と[監査JSON](../reports/orange-fruit-v2-audit.json)。

## 2026-11-11：BDRoadSignsを権利・課題確認後に追加

- 取得前にMendeley Data v1のCC BY 4.0と、標識の見分けやすさを調べるクイズ課題への適合を確認。
- `Compress Dataset`の5,136枚を共通形式へ整備。元画像画素を保ち、18クラス別seed 42でtrain 3,592 / validation 766 / test 778に分割。
- バングラデシュの標識は日本の交通規則と同一とは限らず、安全判断には使わないと明記。背景の道路風景は除外条件にせず、課題上の注意として記載。
- 固定Release `bdroadsigns-v0.1.0`を公開し、assetのサイズ・SHA-256を照合。CV_data_artifacts PR #38でmanifest・ファイルハッシュ・ライセンス・監査報告を登録済み。
- 生徒向けAPIを17件に更新。目標20件まであと3件。詳細は[データ説明](datasets/bdroadsigns.md)と[監査JSON](../reports/bdroadsigns-v1-audit.json)。

## 2026-11-11：FabricSpotDefectを権利確認・整形・公開

- Mendeley Data v1のCC BY 4.0表示と、著者が日常の家庭用布をスマートフォン撮影したという説明を先に確認。洗濯前に衣類の目立つ汚れを探す補助という生徒課題に適合するため採用しました。柄布も含むデータで、柄の存在は除外理由にしていません。
- 固定元ZIP（941,581,889 bytes、SHA-256 `2e4fd58488734fe3b888c0c3633ca4d68da76f3a96f1e9bba08ec710645d6ab2`）を取得し、危険パス・symlinkなし、CRC正常、画像1,014枚のデコード成功、完全一致重複0を確認。
- 元のsplit（643/219/152）と画像画素・寸法を維持し、増強画像を除外。COCO bbox 3,288件を正規化し、0.5px以下の端のはみ出し29件をクリップ。掲載ページの3,286件とアーカイブ・論文の3,288件の差も記録しました。
- 共通artifact `fabricspotdefect-v0.1.0`（744,311,786 bytes、SHA-256 `b40dca04e3879e92533face725d4e12bbfe9ba85e41b1c7ef59e290f1421943d`）を公開。Releaseの掲載サイズ・GitHub SHA-256を照合し、共通形式validatorとZIP CRC検査を通過。
- 生徒向けAPIを16件へ更新。衣類の清潔さ、着用可否、安全性、汚れ落ちを判定する用途ではないと記載。
- 詳細：[データ説明](datasets/fabricspotdefect.md)、[全量監査JSON](../reports/fabricspotdefect-v1-audit.json)。

## 2026-11-11：ChakmaLipīを審査・共通形式化

- Mendeley Data v6のCC BY 4.0表示を確認。関連論文に参加同意と倫理審査の説明があり、書き手IDはデータに含まれません。
- 固定ZIP（103,184,395 bytes、SHA-256 `187b7294c7d4720981022d14d4ae3edccae642c7471a195a27a580a55d6fee52`）を全量検査。37,708枚をデコードし、完全一致重複1,450枚を除外。
- 残る36,258枚を48クラス、seed 42のクラス別70/15/15に分割。画素値は変更せず、全クラスから代表画像を確認。書き手単位の分割・評価はできないと記録。
- 整形ZIPは99,131,569 bytes、SHA-256 `d9ef73e59c084492939b1d7b23d3ffde0fa865f76f132a29c5cba7c12cb19759`。manifest、画像ハッシュ、ラベル、CRCを検証。
- `CV_data_artifacts` PR #36をマージし、固定Release asset `chakmalipi-v0.1.0`を公開。公開URLから再取得した99,131,569 bytesのSHA-256が成果ZIPと一致しました。CV_data PR #49で取得API登録を審査中です。
- 詳細：[ChakmaLipī説明](datasets/chakmalipi.md)、[候補精査状況](catalog-review.md)。

## 2026-11-11：Recyclable Wasteを生徒APIから除外

- 整形済みの`recyclable-waste-v0.1.1` Release assetは公開済みですが、包装上の肖像写真らしき画像と商品・ブランド表示の第三者権利審査が未完了です。
- 候補台帳では公開保留だった一方、実装では生徒向けAPIに表示されていたため、`published=False`へ戻し、一覧・取得API・READMEから外す変更をPR化します。
- APIの生徒向け件数は、ChakmaLipī追加後16件から本変更後15件になります。目標20件まであと5件です。

## 2026-11-11：GeoSetEnneaを整備・固定Release公開

- Mendeley Data v1の固定source manifestに対し、966枚・8,253注釈を全量技術監査。拡張画像、画面キャプチャ、未対応画像、同じ撮影元の別表現を除外し、136枚・1,188矩形注釈を共通形式化しました。
- 80撮影元グループをtrain 84 / validation 22 / test 30へ分け、近似重複が分割をまたがないことを記録。選定画像は全件デコードし、代表27枚でクラス・写り込みを目視確認しました。
- CC BY 4.0表示、著者撮影の説明、指定出典・変更表示を確認。一部の文具ブランド表示は付随的に写り、推薦を意味しないことを明記しました。
- `CV_data_artifacts` Release `geoset-ennea-v0.1.0`を公開。asset 7,531,941 bytes、SHA-256 `6185c0f8e631ec36913b6c229d4fbd51463d2a4fea1084f3c3e8021244ecd6e3`を再取得して照合しました。manifest・source transform・監査資料はartifacts PR #28、ライブラリ登録はCV_data PR #46で反映します。
- 新規候補の一次情報を並行調査。CLICK Trashは課題価値が高い一方、掲載説明の引用がVersion 1を指し「GitHub and license: to be added」と記すため公開条件の整合を確認するまで保留。DeepWeedsは豪州固有種中心で高校生の身近な課題との接続が弱いため採用しません。


## 2026-11-10：Indoor Plant Varieties v0.1.0をライブラリへ統合

- Mendeley Data v1（CC BY 4.0）の1,172画像を全量デコードし、10枚の完全一致重複を除外。残る1,162枚からEXIF/GPSを除去し、長辺512px以下の分類データを整備しました。
- 成果物Release `indoor-plant-varieties-v0.1.0` を固定URLで公開。1,167ファイル、74,718,549 bytes、SHA-256 `0194a3631ecaf0293cc0271d938ffe6933b61ce58e58e648f8ca346bd1dbe714`。Release assetとartifact manifestを照合しました。
- `cvlesson.get("indoor_plant_varieties")`の取得、ZIP安全展開、manifest検証、DataFrame化を実データで確認。1,162行・7クラスと全画像パスの存在を確認しました。
- 成果物リポジトリPR #25とライブラリPRを作成中。いずれもmainへは未マージ。

## 2026-11-08：Recyclable Waste 全画像の目視確認

- 整形済みの一意画像977枚を10枚の縮小一覧で確認。素材クラスと画像内容に明らかな不一致は見当たらなかった。
- 縮小一覧では明瞭な人物は確認されず、包装上の肖像写真らしきもの1件と、複数画像のブランド・商品文字を記録。これは法的な肖像・商標審査ではない。
- dataset説明と候補台帳を更新。第三者権利・肖像・商標の再配布審査は未完了のため、正式API・公開Releaseの保留を継続。
- 詳細：[目視監査記録](https://github.com/708san/CV_data_artifacts/blob/main/reports/recyclable-waste-visual-review-2026-11-08.json)、[データ説明](datasets/recyclable_waste.md)。

## 2026-11-08：リモート専用保管・artifact inventory・キャッシュ管理

- データ本体を`CV_data`・`CV_data_artifacts`のGit履歴やPyPIへ入れず、許諾済み整形データは`CV_data_artifacts`の固定Release assetで管理する方針に更新した。大容量LoRA原本は固定した公式配布元から直接取得し、重みは配布しない。
- `cvlesson`の取得時キャッシュはcheckout外（`XDG_CACHE_HOME`または`~/.cache`配下）に置き、明示的な取得API呼び出しまでダウンロードしない運用を明記した。
- 50候補の状態を再集計：candidate 32、hold 15、整形artifact準備済み・Release待ち2、artifact/asset待ち1。holdは公開承認を意味せず、技術監査の進み具合も異なる。
- `CV_data_artifacts`のPR #7を最新`main`へ合わせてマージし、15 source manifest、6 artifact manifest、監査report・ライセンス記録・変換ツールをmainに追加した。GitHub Actionsは成功。画像バイナリとRelease assetは追加していない。
- `datasets.cache_info()`で登録済みデータのキャッシュ容量・版・ファイル数を確認でき、`datasets.clear_cache(dataset_id=None)`で指定データまたは登録済みIDのキャッシュを削除できるようにした。symlinkや通常ファイル以外は事前検出し、登録外ディレクトリは削除対象にしない。
- 容量計測、指定IDだけの削除、登録外フォルダの保持、一括削除、symlink・不正なcache rootの拒否をオフラインテストで確認。`PYTHONPATH=src python -m unittest discover -s tests -v`は32件成功、Pillow未導入の2件をスキップ。
- 一次情報の並行確認、権利ゲート後の取得、調査範囲の事前決定、既存manifest・監査結果の再利用、候補単位のPRを標準手順にし、権利審査は省略しない。

### 次の作業

- 再配布候補の元画像権利・プライバシー審査を進め、許諾済みの整形データをどの固定Release assetで保持するか決める。Release作成は明示許可が済むまで行わない。
- 承認済みデータが現れたら、取得APIの固定URL・サイズ・SHA-256・外部キャッシュを実データなしのテストで先に検証する。

## 2026-11-05：共通APIと分割・監査の土台

### 変更目的

- 固定Release取得を、英語IDと登録済み日本語名の完全一致で呼び出せるようにする。
- 分類データのパス・ラベル・日本語ラベル・クラス番号・分割を共通DataFrameへそろえる。
- 公式testを保持し、trainから再現可能なvalを作る。
- CPUで利用できる遅延読み込みのPyTorch Datasetと、機械可読な品質監査項目を用意する。

### 実装結果

- `DatasetBundle.to_df()`、`show_examples()`、`to_torch_dataset()`を追加。
- `classes`、`class_names_ja`、`splits`、`license_info`、`source_info`を追加。
- 日本語名は登録済み別名の完全一致だけを受け付け、曖昧な推測はしない。
- train/val分割はseed `42`、クラス別、公式test保持で固定。
- 取得失敗時は最大3回まで再試行し、既存のSHA-256・サイズ・安全なZIP展開を維持。
- 監査JSONに、元画像数・使用可能数・クラス数・分割数・破損数・完全一致重複候補・ラベル不一致・除外理由・分割方法・漏洩リスク・検証日時を追加。
- `CV_sample_data`、Release、既存Notebookは変更していない。

### festival_iconsの実体監査結果

- 固定ZIP：2,838,163 bytes、SHA-256一致。
- 画像168枚を全量デコードし、破損0枚、キャプション欠損0件。
- 完全一致重複候補0件、ラベル不一致0件。
- 8×8平均ハッシュで類似候補417組を抽出したが、レビュー用であり重複確定・自動削除はしていない。権利審査は未実施。LoRA素材のため分類用splitは作成していない。
- 詳細：[festival-icons-v1.0.0.json](../reports/festival-icons-v1.0.0.json)

### tomato_leavesの実体監査結果

- 固定ZIP：124,334,101 bytes、SHA-256一致。
- 画像7,209枚を全量デコードし、破損0枚、完全一致重複候補0件、ラベル不一致0件。
- 元の分割はtrain 5,768枚・test 1,441枚。標準化後はtrain 5,191枚・val 577枚・test 1,441枚。
- 8×8平均ハッシュで類似候補14,571組を抽出したが、レビュー用であり重複確定・自動削除はしていない。同一個体・撮影系列のグループ分離と権利審査は未実施。
- 詳細：[tomato-leaves-v1.2.0.json](../reports/tomato-leaves-v1.2.0.json)

### Fashion-MNISTのプレビュー整備

- 公式GitHubの固定コミット`b2617bb6d3ffa2e429640350f613e3291e10b141`を使用。
- 4つのIDX gzipをSHA-256・ヘッダー・件数まで検査し、PGMキャッシュへの変換を確認。
- 標準化後はtrain 54,000 / val 6,000 / test 10,000。
- MIT表記は確認済みだが、教材公開・再配布の最終確認中。正式一覧には未掲載。
- 詳細：[fashion-mnist-github-b2617bb6.json](../reports/fashion-mnist-github-b2617bb6.json)

### CV分類Notebookの新設

- LLM講座の基準Notebookは変更せず、CV分類用の[新Notebook](../notebooks/cv/classification_v1.ipynb)を追加。
- トマトの葉の出典確認、DataFrame、画像例、train/val/test、CPU向け小型CNN、テスト記録、振り返りを含めた。
- Fashion-MNISTとKuzushiji-MNISTは権利・公開状態の理由から生徒向けNotebookには含めていない。

### 検証条件と結果

- オフラインの標準テスト：Python 3.9環境で19件中19件成功（Pillow未導入による2件のskip）。
- Python 3.10環境で19件中19件成功（pandas未導入による1件のskip）。
- `compileall`で`src`と`tests`を検査済み。
- 固定Releaseの全量画像監査を実施済み。取得と画像検査は通常のネットワーク不要テストから分離している。

### 未完了・保留

- `registry/candidates_50_unreviewed.json`は未承認候補のまま。Fashion-MNISTのプレビュー以外は正式APIへ追加していない。
- Kuzushiji-MNISTはライセンス表記を確認したが、公式データファイルの固定版とSHA-256が不足するため保留中。
- 詳細：[kuzushiji_mnist.md](datasets/kuzushiji_mnist.md)
- `festival_icons`はLoRA学習素材としてのみ扱い、分類データや一般的なオープンライセンスとして扱わない。
- CV分類Notebookは新規作成済み。PyTorchを含む実Colab検証と、次の検出・分割Notebookは次の課題。

### データ・LoRA選択基盤

- `datasets.list_preview()`で権利確認中の教師向けデータを正式一覧から分離。
- Fashion-MNISTは固定IDXファイルを検証済みのプレビューとして管理。
- `cvlesson.loras`を追加し、素材・キャプション・トリガーワード・基盤モデル・権利状態を管理。
- 承認済みLoRAがないため、`loras.list_available()`は空。文化祭アイコンは明示的なプレビュー取得のみ。

### 2026-11-05：課題選択カタログと候補精査

- `datasets.list_available(task=..., audience=..., include_preview=...)`を追加し、課題タイプ・対象者・プレビュー状態で候補を絞れるようにした。
- `datasets.list_tasks()`を追加し、生徒が選べる課題タイプとデータIDを一覧化した。未承認の検出・分割候補は表示しない。
- `DatasetBundle`に課題タイプ、対象者、用途、入力・出力、概算取得サイズを追加した。
- `docs/catalog-review.md`に50候補を分類・検出・分割・素材の課題へ対応付け、全候補をAPIへ追加しない理由と次の実体検査順を記録した。
- `Fruits-360`、`Recyclable Waste`、`GeoSetEnnea`、`FruitSeg30`は公式ページでライセンス表記と概要を再確認した。GeoSetEnneaは公式APIのフォルダ別メタデータを追加確認し、画像966件・YOLOラベル966件と別置きのaugmented/rawを記録した。Recyclable Wasteは9枚の代表画像でAPI SHA-256照合とJPEGデコードを実施したが、固定アーカイブSHA-256と全量監査が未完了のため、いずれも台帳は`under_review`・公開保留のままにした。
- `Fruits-360`、`Recyclable Waste`、`GeoSetEnnea`、`FruitSeg30`は公式ページでライセンス表記と概要を再確認した。GeoSetEnneaは全公開2,898ファイルのsource manifestを作成し、分割済み画像966件・YOLOラベル966件とaugmented/rawを記録、内容SHA重複1グループを確認した。Recyclable Wasteは989画像のsource manifestと12重複グループ、9枚の代表画像検査を記録した。FruitSeg30は当初、全30クラスのメタデータと代表画像のみを検査し、詳細は本ページ後半の2026-11-08監査記録で更新した。
- PyPI向けのパッケージビルドを行うが、本番公開・Release作成・mainへのマージは行わない。

### 2026-11-06：Indian Origin Flowersの一次監査

- 公式Mendeley Data v1のCC BY 4.0表記と公開APIを確認した。
- APIの10フォルダ、8,098枚、約1.62GBをファイル単位のsource manifestへ固定した。全ファイルにAPI記載SHA-256がある。
- 各クラスから1枚ずつ、合計10枚を取得してSHA-256照合とJPEGデコードを実施し、すべて成功した。
- ページ説明の15,044枚とAPIの8,098枚が一致しないため、再配布用artifact・正式API・Notebookには追加せず、`under_review`・公開保留とした。
- 詳細：[Indian Origin Flowers](datasets/indian_origin_flowers.md)、[監査JSON](../reports/indian-origin-flowers-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/indian_origin_flowers-v1.json`に保存した。

### 2026-11-06：Pistachio Image Datasetの全量画像監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- SHA-256一致後に安全展開し、画像2,148枚を全量デコードした。JPEG・600×600・RGB、破損0、完全一致重複0だった。
- Kirmizi 1,232枚、Siirt 916枚をseed 42でtrain/val/testへ分け、共通classification artifactをローカル生成してmanifest照合に成功した。
- 元画像の第三者権利、クレジット、ZIP内の非画像ファイル、再配布条件が未完了のため、正式API・Notebook・PyPIには追加せず公開保留とした。
- 詳細：[Pistachio Image Dataset](datasets/pistachio_image_dataset.md)、[監査JSON](../reports/pistachio-image-dataset-full-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/pistachio_image_dataset-v1.json`に保存した。

### 2026-11-06：Fresh and Rotten Fruitsの構成・代表監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIP2本のサイズ・SHA-256を確認した。
- Original 3,200枚、Augmented 12,335枚、16クラスをZIP中央ディレクトリから確認した。Originalは各クラス200枚だった。
- Original各クラス1枚、合計16枚を範囲取得し、ZIP CRCとJPEGデコードに成功した。
- 元画像と拡張画像を混ぜた評価漏洩、全量デコード・重複・元画像権利が未完了のため、正式API・Notebook・PyPIには追加せず公開保留とした。
- 詳細：[Fresh and Rotten Fruits](datasets/fresh_rotten_fruits.md)、[監査JSON](../reports/fresh-rotten-fruits-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/fresh_rotten_fruits-v1.json`に保存した。

### 2026-11-06：Banana and Guava Qualityの構成・代表監査

- 公式Mendeley Data v2のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- ZIP中央ディレクトリからBanana/Guava × Class_A／Class_B／Defectの6グループ、画像1,748枚を確認した。
- 各グループ1枚、合計6枚を範囲取得し、ZIP CRCとJPEGデコードに成功した。代表画像は1024×1024 RGBだった。
- ページ説明の1,738枚とZIPの1,748枚が一致しないため、全量監査、ラベル定義、元画像権利、再配布条件が未完了のまま公開保留とした。
- 詳細：[Banana and Guava Quality](datasets/banana_guava_quality.md)、[監査JSON](../reports/banana-guava-quality-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/banana_guava_quality-v2.json`に保存した。

### 2026-11-06：Tangerines_Imagesの全量画像監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定RARのSHA-256を確認した。
- パスを検査してから340枚を展開し、全画像がJPEG・640×480・RGBとしてデコードできた。破損0、完全一致重複20グループだった。
- 公式ページはgood／poor condition分類を説明するが、アーカイブには画像との対応ラベル表が見つからなかった。連番や見た目からラベルを割り当てず、共通分類変換・正式API・Notebookへの追加は保留した。
- `mandarina_331.jpg`に手の写り込みがあることも記録した。
- 詳細：[Tangerines_Images](datasets/tangerines.md)、[監査JSON](../reports/tangerines-full-image-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/tangerines-v1.json`に保存した。

### 2026-11-06：Image Dataset of Indian Coinsの構成・代表監査

- 公式Mendeley Data v1のCC BY 4.0表記と固定ZIPのSHA-256を確認した。
- ZIP中央ディレクトリにJPEG6,680枚と7額面フォルダがあり、公式ページの総数と一致した。パス逸脱、symlink、非画像ファイルはなかった。
- 7額面から代表画像を1枚ずつ取得し、ZIP CRCとJPEGデコードを確認した。
- 額面フォルダの下に記念デザイン、表裏があり、同系列画像の分割漏洩対策が必要。全量画像検査、元画像の権利、グループ分割方法が未完了のため、共通artifact・正式API・Notebookへの追加は保留した。
- 詳細：[Image Dataset of Indian Coins](datasets/indian_coins.md)、[監査JSON](../reports/indian-coins-sample-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/indian_coins-v1.json`に保存した。

### 2026-11-06：RGB-D Mushroom Growthの固定版実体確認

- 公式Mendeley Data v1ページのCC BY 4.0表記と、129件のRGB・深度・COCO注釈という説明を確認した。
- 固定版v1の公式APIに登録されているのは`readme.txt` 1件（4,712 bytes）のみ。公式ダウンロードURLから取得したファイルのSHA-256は`a39f7231cdc51bc7fb103d3ff319830caa63f4b196f81593124d435b18dd032f`で、API記載値と一致した。
- READMEはRGB/Depth/Annotationsの構成と時系列撮影を説明するが、実際の画像・深度・注釈ファイルはAPI一覧に存在しない。マスクや対応関係を実体検査できないため、共通形式への変換、正式API、Notebookへの追加を保留した。
- 詳細：[RGB-D Mushroom Growth](datasets/rgb_d_button_mushroom_growth.md)、[監査JSON](../reports/rgb-d-button-mushroom-growth-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/rgb_d_button_mushroom_growth-v1.json`。

### 2026-11-06：Bangladeshi E-Wasteの全量画像・ラベル監査

- 公式Mendeley Data v1およびアーカイブ内READMEのCC BY 4.0表記、提供者、固定ダウンロードURLを確認した。
- 固定ZIP（72,987,704 bytes、SHA-256 `f73b30286225c208e98b34f81eb5ffef7baf79e883039d2087e8db53f6ee284e`）を検証後に安全展開した。パス逸脱・symlinkなし、CRC検査成功。
- 画像2,157枚すべてがJPEG 640×640でOS画像デコーダーによる読み込みに成功。画像・ラベル2,157組は同名で全件対応し、完全一致画像重複0件だった。
- 12クラス、注釈2,159個を確認。通常のYOLO矩形752個とpolygon 1,407個が混在し、空ラベルは4件、クラスID・座標・形式エラーは0件だった。検出共通変換`detection_yolo_v1.1.0`を追加し、polygonを外接矩形へ変換、元の形式別件数をmanifestに記録するようにした。
- train/valid/test分割は画像1,500/330/327枚。testから各クラス1枚ずつ確認した12枚はすべて明るい緑背景だった。公式ページの「背景に変化がある」という説明と見本に差があるため、背景への依存を調べる教材候補とし、実環境の廃棄物分類器としては扱わない。
- artifact v0.1.0を一時領域へ作成し、画像2,157枚・ファイル4,319件のmanifest照合に成功。polygon由来のbboxは座標精度を維持する17桁で出力。ZIPは71,762,431 bytes、SHA-256 `fe06d5579e3a84010e0e6ccd7d90d8230ca72d5fcd39719d6d6d8731595007fa`。ライブラリの全2,157画像・2,159注釈の構造検査とDataFrame変換にも成功した。データ本体はGit履歴へ追加していない。
- ライブラリには検出bundle検証とDataFrame表示を実装したが、公開Releaseが未作成のためsourceを未公開状態に固定し、正式一覧から隠し、取得要求も拒否する。
- 詳細：[Bangladeshi E-Waste](datasets/bangladeshi_ewaste_image.md)、[監査JSON](../reports/bangladeshi-ewaste-full-audit.json)。source manifestは`CV_data_artifacts/manifests/sources/bangladeshi_ewaste-v1.json`。

### 2026-11-07：Food Waste Bangladesh・SmallFishBDの全量監査と共通化

- Mendeley公式v1/v2ページのCC BY 4.0表示、固定ファイル情報、SHA-256を照合してから安全展開した。
- Food Waste Bangladeshは645枚すべてJPEGデコード成功、重複0、危険パス・symlink 0、EXIF/GPS/XMPなし。5ラベルは撮影場面で、クラス数は91/146/72/16/320と偏る。廃棄量を表すデータではない。
- SmallFishBDは元画像1,700枚すべて320×320 JPEGとしてデコードし、公式クラス数に一致。完全一致重複3枚を除外し、1,697枚を収録。20,400枚の増強画像は取得・収録せず、評価時の分割漏洩を避ける。
- `CV_data_artifacts`にsource manifest、ライセンス記録、除外記録、共通classification artifact、検査reportを準備した。両artifactのサイズ・SHA-256・ZIP内manifest検証は済み。
- ライブラリへ両候補を`published=False`で登録。詳細情報は参照できるが、正式一覧と取得APIから隠れ、Release asset作成までは取得できない。
- サンプル目視ではFood Wasteに人物の顔、SmallFishBDに人物は見つからなかったが、全画像を人手で権利・プライバシー審査した結論ではない。全画像の権利審査とRelease asset作成を保留事項として明記した。
- 詳細：[Food Waste Bangladesh](datasets/food_waste_bangladesh.md)、[SmallFishBD](datasets/smallfishbd.md)、[候補精査状況](catalog-review.md)。

### 2026-11-08：Strawberry-DS v1の全量実体・注釈監査

- Mendeley公式v1のCC BY 4.0表示、固定ファイルID・サイズ・SHA-256を確認。SHA-256一致後にZIP検査を行い、505項目・CRC正常・危険パスとsymlinkなしを確認した。
- 247画像すべて3840×2160 JPEGとしてデコードし、247 YOLOラベルとの対応、完全一致重複0、EXIF/XMP APP1なしを確認した。分割はtrain 172、valid 49、test 26。
- 1,083注釈のクラス内訳はEarly-Turning 34、Green 450、Late-Turning 56、Red 225、Turning 42、White 276。2枠は正規化座標の丸めで上端を約0.005画素超え、現行の厳密な共通検査では失敗する。
- 同梱`data.yaml`はRoboflow v4の`license: Private`と記録。一方Mendeleyの掲載ライセンスはCC BY 4.0で、再許諾の権利関係が確認できないため、画像artifact・共通形式変換・APIへの登録を行わず保留した。
- 監査JSONとsource manifestは`CV_data_artifacts`に記録し、画像本体はartifact repositoryへ追加していない。
- 詳細：[Strawberry-DS](datasets/strawberry_ds.md)、[監査report](../../CV_data_artifacts/reports/strawberry_ds-v1-audit.json)、[source manifest](../../CV_data_artifacts/manifests/sources/strawberry_ds-v1.json)。


### 2026-11-08：HGM-4 Hand Gesturesの固定版・アーカイブ目録監査

- Mendeley Data v8のCC BY 4.0表示、DOI、固定RARのファイルID・228,825,330 bytes・SHA-256を確認した。SHA照合後にRAR目録を読み取り専用で確認し、4,270項目、相対パスのみ、symlink・パス逸脱なしを確認した。
- macOS `bsdtar`がアーカイブ内フィルターを処理できず完全展開に失敗した。部分展開物は信頼せず、画像検査・変換・配布に使用していない。画像数・画質・参加者プライバシーの実体確認は未完了。
- 公式論文は5名、4カメラ視点、26種の手形を説明する。人物または撮影系列単位の評価分割が必要で、一般的な手話翻訳・人物識別用途には適さない。
- 固定source manifestと監査reportを`CV_data_artifacts`に追加。再配布・教材化・API掲載は保留。
- 詳細：[HGM-4](datasets/hgm_4_hand_gestures.md)、[監査report](../../CV_data_artifacts/reports/hgm_4_hand_gestures-v8-audit.json)。


### 2026-11-08：FruitSeg30 v3の全量監査と29クラスartifact準備

- 公式固定v3の全3,938ファイル（計224,579,761 bytes）を取得し、ファイル単位のサイズ・SHA-256を全件照合した。1,969 JPEGと1,969 PNGを全件デコードし、マスクPNGのCRCエラーと完全一致重複は0件。
- Guava 55組はすべて非512サイズで、そのうち52組は同名画像とマスクの寸法が不一致。向き・対応を推測せずクラス全体を除外した。残り29クラスの1,914組は512×512で対応し、8-bit grayscaleのマスクを画素変更せず保持。
- クラス内seed 42でtrain/val/testへ分け、共通artifact v0.1.0（1,914画像・1,914マスク、3,833ファイル）をローカル生成。artifact manifest照合成功。ZIPは68,242,354 bytes、SHA-256 `129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5`。
- MendeleyページのCC BY 4.0と論文の撮影説明を確認。第三者由来素材の全画像独立審査、領域分割API、公開Releaseは未完了のため、候補・APIは公開保留。
- 領域分割artifactの固定Release SHA検証、画像・マスク対応検査、DataFrame、遅延読み込みPyTorch Datasetをライブラリに実装。固定Release assetが未作成のため、正式課題一覧からは隠している。
- 詳細：[FruitSeg30](datasets/fruitseg30.md)、[監査JSON](../reports/fruitseg30-sample-audit.json)、source manifestとartifact manifestは`CV_data_artifacts`に保存。


### 2026-11-08：Recyclable Waste v1全量監査と教材artifact準備

- Mendeley Data v1の公開989画像（1,707,541,468 bytes）すべてを既知サイズ・SHA-256に照合し、ImageIOで全件デコード。掲載件数1,000との差11枚は補完しない。
- 完全一致重複12ファイルを除いた一意977画像、クラス別件数、画像寸法を記録。104画像にGPSを含むEXIFを検出。
- 一意画像977枚の共通artifact v0.1.0を作成。EXIF方向を適用、長辺512pxへ縮小、EXIF/GPS等を除去、seed 42でクラス層化split。ZIPは93,671,127 bytes、SHA-256 `99e80d8c0a083b65f7c5550afc87ec2db985b612762d55475a425b8f6db784ed`。
- 代表5枚を目視しブランド・商品文字を確認。全画像の人手によるプライバシー確認が未完了のため、正式API・Releaseは保留。
- Fruits-360公式repoのCC BY-SA 4.0表示を確認したが、GitHub Releasesが空で固定タグReleaseがないため、画像取得・実体検査は保留。
- 詳細：[Recyclable Waste](datasets/recyclable_waste.md)、[Fruits-360](datasets/fruits_360.md)、[監査JSON](../reports/recyclable_waste-v1-full-audit.json)。


### 2026-11-08：Pistachio Image Dataset v1監査・artifact準備

- 固定ZIP（27,859,492 bytes、SHA-256 `140760707018b7f53d91a86a1d7be96d92b1a0d26a75690ab9280ed1170df895`）を再取得・照合し、安全なパスとsymlinkなしを確認。
- 画像以外の特徴量表・引用文書10ファイルを除き、2,148 JPEG（600×600 RGB）全件デコード成功、完全一致重複0。
- 画像画素を変更せず、共通formatとseed 42のクラス層化splitを追加。train 1,503、val 322、test 323。artifact manifest検証成功。
- Mendeley v1はCC BY 4.0表示。掲載者の撮影説明、関連2論文の引用条件を記録。2021論文本文のCC BY-NC表示とdataset licenseを分けて記録。画像権利者・第三者権利の確認が残るためRelease/APIは保留。
- 詳細：[Pistachio](datasets/pistachio_image_dataset.md)、[監査report](../reports/pistachio_image_dataset-v1-full-audit.json)。

## 2026-11-09：整形済み3データの権利・成果物再確認

- FruitSeg30 v0.1.0、Pistachio Image Dataset v0.1.0、Recyclable Waste v0.1.0のZIPを一時領域で再検査。CRCとファイル一覧・全ファイルのSHA-256/サイズがartifact manifestに一致しました。ZIPはGitに追加していません。
- 各公式配布ページのCC BY 4.0表示と提供者の出典説明を確認し、帰属・改変通知（ピスタチオは指定論文引用）を条件に再配布審査を記録しました。
- FruitSeg30は29クラス1,914画像・マスク組、ピスタチオは2,148画像、Recyclable Wasteは977画像。教材課題と注意事項をデータ別ページへ記載しました。
- GitHub Release assetが未作成のため、3件ともライブラリからはまだ取得できません。食品廃棄・E-Wasteは人物／印刷肖像等の権利・プライバシー確認を保留しています。

## 2026-11-09：FruitSeg30 固定Release公開

- FruitSeg30 v0.1.0をGitHub Release `fruitseg30-v0.1.0` に公開。assetは68,242,354 bytes、GitHub APIのSHA-256はmanifest一致（`129384a6e9599b0b9eb756ec93abda25a90bdd70a514fd04f905a2ff2e8c5ba5`）。
- 画像・マスクのバイナリはGit履歴に含めず、Release assetだけで配布。固定タグURLのHTTP応答を確認。
- ライブラリ一覧をstudent-enabledへ切り替える設定と説明の更新をPRに準備中。

- FruitSeg30取得APIを含むPR #25をmainへマージ。固定Release assetとmainブランチのAPI設定が揃いました。PyPI配布版への反映はパッケージ更新時です。


## 2026-11-09：SmallFishBD v0.1.1 Release公開

- artifact準備PR #14をCV_data_artifacts mainへマージ後、固定タグReleaseを作成しました。
- ZIPは29,799,609 bytes。GitHub APIのSHA-256 `367b332bc0da479e9a708449f45cf7aa10eb190267a6bc1f1a87e5a38ce8f547`がローカル成果物と一致し、固定URLはHTTP 200を返しました。
- CC BY 4.0の帰属・変更表示、全画像視覚レビューを踏まえた再配布審査を記録。ライブラリの固定URL・ハッシュ・公開状態、データ説明、候補台帳を更新する内容をCV_data PR #27に提出しました。

## 2026-11-10：RDD2020 Japanの固定Release取得API

- 公開済みの`rdd2020-japan-v0.1.0`を`datasets.get("rdd2020_japan")`で取得できるようにする変更を作成中。
- 642 MBの固定ZIPに対し、このデータだけのダウンロード・展開後容量・ファイル数上限を指定し、既存データの標準上限は変えない。ZIP直下配置を許す場合も許可したトップレベル名だけに限定し、絶対パス・親参照・symlinkを拒否する。
- 日本語README、データ説明、AI改造ガイドを更新。CC BY-NC 3.0の非商用条件と、現在の安全性を判断しない注意を利用者向けに記載。
- この変更は独立PRでレビュー待ち。ローカルの標準ライブラリ単体テストは34件成功、2件はPillow未導入のためskip。ZIP直下形式、データ別上限、親パス拒否をネットワークなしで確認。


## 2026-11-11：LeFood-Setのペア画像回帰API

- 固定Release `lefood-set-v0.1.0`を利用し、524組の食前・食後画像、実測重量、派生値を検証して取得するAPIを追加。
- パス逸脱、ペア重複、manifest件数、数値・導出列、画像ファイル集合を検証し、pair単位splitを維持。
- CC BY 4.0の帰属・変更表示と、インドネシアの病院食データを日本の給食や健康判断へ一般化しない説明を追加。


## 2026-11-12：生徒向け画像データ4件のRelease・API登録

- Indoor Waste Image Dataset、WasteSegCluster v4、Fire Recognition v4、AgriFreshNET v1の出典ページでCC BY 4.0を確認。具体的な清掃確認、地域環境学習、防災画像分類、青果の先行確認課題に用途を限定。
- 画像全数と注釈・クラス・splitを監査し、manifest・ライセンス・監査レポートをCV_data_artifactsへ登録。各Release assetのサイズとGitHub SHA-256を照合。
- AgriFreshNETは同じSHA-256の重複・異なる鮮度ラベルの競合を含む76ファイルを除外し、14,084枚を収録。
- 4件ともZIPのパス安全性、manifest・ラベル構造をライブラリ検証器で確認。Japanese Receipt Detailedを含め、生徒向け公開データは23件となる。火災の「Safe_Fire」は実際の安全を意味せず、青果の見た目分類は可食性を判定しない。
- Artifact PR #44 merged。固定Release: `wastesegcluster-v0.1.0`, `indoor-waste-image-v0.1.0`, `fire-recognition-image-v0.1.0`, `agrifreshnet-v0.1.0`。


## 2026-11-12：道路の穴マスク付きデータを準備

- Mendeley Data v3の固定スナップショットでCC BY 4.0とDOIを確認。元ZIP 231,728,698 bytesのSHA-256 `e59bb8d771e18f059ab78d88e640e83869fc8c8fd808697a0c2c48e16eec4f76`を照合し、安全なZIP目録とCRCを確認しました。
- 元画像2,235枚、道路・ひび・穴の各マスクを確認し、道路の穴の課題に絞って元画像とPOTHOLEマスク2,235組を画素変更なしで整備。ブラジル旧道路画像のため、地元の現況や安全判定には使いません。
- 同一道路区間をまたがないtrain/val/test splitを作成。artifact ZIP 207,450,159 bytes、SHA-256 `3c5999c01f7dbac64cdf3e7a7ee5467b62b471142dc8fab78cb9f35527ed5eb7`。manifestに4,476ファイルのハッシュを記録。
- DIU-HandGesture31はCC BY 4.0と参加者の画像共有同意を確認しましたが、実画像にクラス名文字の焼き込みがあることを見つけ、分類学習への漏洩があるため公開対象から除外して台帳で保留しました。
- 生徒向けAPIへの登録後は24件になります。


## 2026-11-12：CLICK Trash Datasetの固定ReleaseとAPI追加

- Mendeley Data v2のCC BY 4.0表示、DOI、固定アーカイブSHA-256を確認。ZIP全3,404エントリーのパス・symlink・重複名・CRCを監査し、画像1,126枚を全件デコード。
- single-class `trash`を選び、元のbbox 2,213件とtrain/val/test splitを維持。長辺1,024px以下へ再書き出し、EXIF/GPS/カメラ機器メタデータを除去。4枚の背景画像は空ラベルで保持。
- 代表画像を各splitから1枚ずつ確認。落ち葉・土・草地にある包装ごみを確認し、包装文字・商標は一部に残る旨と非推薦の注記を記録。撮影地はインドで、日本の地域環境を代表しない。
- 共通artifact ZIPは668,588,437 bytes、SHA-256 `5a97374493c341aac6fe9a6b7a65dcd4437eddb3071085238c2237e9aaff023e`。manifest・bbox・画像/ラベル対応検証に成功。
- CV_data_artifacts PR #46をマージし、`click-trash-v0.1.0` ReleaseにZIPを登録。GitHub API上のサイズ・SHA-256がローカル値と一致。
- `click_trash`を取得API、課題カタログ、データ説明、候補台帳へ追加。生徒向けAPIは25件。


## 2026-11-12：歩道上の物体候補データを整備

- Mendeley Data v1の公式ページでCC BY 4.0とDOIを確認。元ZIP 84,945,675 bytesの固定URL・SHA-256を記録し、展開前に照合。全2,501エントリーのパスとsymlink、重複名、CRCを監査しました。
- 全1,250画像をデコードし、640×640、train 1,000 / valid 250、bbox 1,627件を確認。クラス別件数はbump 479 / fence 368 / hole 419 / pole 361。画像・ラベル欠落、座標範囲外、完全重複はありません。
- 元JPEGのSHA-256と正規化bboxを保持して共通物体検出形式へ整理。ZIPは84,776,089 bytes、SHA-256 `fb95637824d7470ec7da5f890b48af24a9cbda291b07d5074ef684f95ac17b7a`。ファイルmanifest、パス、CRCを照合。
- 配布元は公開Roboflowデータから画像を選んだと説明していますが、元データセットごとのID・ライセンスは列挙していません。配布元ページのCC BY 4.0表示を記録し、この出所の限界を利用条件に明記しました。
- 課題用途は歩道上の段差・穴・柵・ポール候補を人が確かめる記録地図の試作。物体の存在を通行障害や安全性の判定に使わないよう説明しました。
- CV_data_artifacts PRと固定Release、CV_dataの取得API・日本語説明・候補台帳を更新。生徒向けAPIは26件になります。

## 2026-11-12：身近な課題向けデータ3件を監査・共通形式化

- TrashNetは固定コミットのMIT Licenseと著者らの収集説明を確認。2,527画像の素材分類で、白背景と地域分別ルールの限界を明記。
- ViFoodLabel v2はCC BY-NC 4.0、実物パッケージを自ら撮影した説明、600画像と9項目のJSON正解を確認。商用不可、項目別OCR評価として扱い、文字単位教師データとは呼ばない。
- 電力量計v1はCC0 1.0とCOCO注釈を確認。全体写真からラベル付き数字bbox 977件を切り出し、元画像単位でsplit。配布物には数字切り出しのみを収録。
- 3件の固定Release用ZIPを作成し、manifest・CRC・共通artifact構造を検証。ZIPはTrashNet 42,765,280 bytes（train 1,762 / val 382 / test 383）、ViFoodLabel 187,378,509 bytes、電力量計数字 11,516,398 bytes。
- 3件の固定Release assetを公開し、公開URLから再取得した全ZIPのSHA-256一致を確認。APIの生徒向け件数を22件に更新しました。


## 2026-11-13：空画像・翌日天気データとLoRA Notebook修正を統合

- CV_data PR #63をmainへsquash merge（`a824ee96d0123843ba58c6cf0df299656903e545`）。`sky_weather_next_day`はmainの`datasets.get()`から取得できる登録状態です。
- 成果物Releaseは[sky-weather-next-day-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/sky-weather-next-day-v0.1.0)。ZIP 10,014,277 bytes、SHA-256 `c438ca3444bf72773d4a7bb430ed3f20885db8fbb0fd5d3f00ee7727149564e0`。
- CIはPython 3.11、3.12、3.13の全6ジョブ成功。天候metadata列の型付きDataFrameテストを含む。
- `generation_smoke_test.ipynb`は`capabilities_ja`を返す固定commitをインストールするため、KeyErrorの原因となった旧版ずれを解消。ColabでのSDXL生成とデータ取得は利用者環境で未確認。


## 2026-11-13：Colabの旧TorchAOとLoRA読込の競合

- LoRA 4件すべてが、Colabに事前導入されたtorchao 0.10.0とPEFT 0.19以降の互換性エラーで読み込みに失敗。GPU最大使用量6.57 GiBであり、メモリ不足ではない。
- PEFT上流のIssue #3964と修正PR #3989を確認。量子化していないモデルのLoRA挿入でも古いTorchAO検出が例外になる既知問題。修正はPEFT mainに統合されているが、現在のPyPI版に含まれるかは未確認。
- 画像生成Notebookに、TorchAO量子化を使わないこの実行では古いtorchaoを削除し、Colabランタイムを再起動してから全セルを実行する手順を追加。torchaoを別用途で使うランタイムには適用しない。
- NotebookのColab再実行・4件の画像生成成功は未確認。


## 2026-11-13：LoRA実行時のTorchAO変更を避け、PEFT修正版を固定

- ユーザーの懸念を受け、共有環境上で`pip uninstall torchao`を行うNotebook手順を撤回。Colab上で既存パッケージを削除・変更しない方針へ変更。
- PEFTの修正PR #3989のmerge commit `c2d5f697fbb30063cbde6f39e2734883b70b8753`を特定。この修正はTorchAO 0.10.0を警告付きで無効扱いし、TorchAOを使わない標準LoRA挿入を続行する。
- 生成NotebookはCV_dataの固定main commitとPEFT修正merge commitを導入する。PEFTの修正を含む正式版が出るまでの暫定固定である。
- インストール案内にローカル仮想環境を推奨する手順を追加。仮想環境にtorchaoを持ち込まない限り、共有Python環境のパッケージは変更しない。
- Notebook JSONを読み書きして構造を確認。Colab T4での再実行・LoRA生成成功は未確認。


## 2026-11-13：画像生成のPEFT依存を明示

- `generation.load()`はDiffusersのLoRA読込でPEFTを必要とする一方、従来の`diffusion` extraがPEFTを含まず、Colabの事前導入に偶然依存していた。
- `diffusion` extraへ`peft>=0.21.2,<1`を追加し、extrasメタデータテストの期待値を更新。
- インストール案内にPEFTの役割と、旧torchaoを含むColabでは修正版PEFTを固定する生成Notebookを使う注意を追記。PEFTの修正版がPyPI配布されるまで、Notebook外のColab利用は保証しない。
- `pip uninstall torchao`は行わない。ローカルでは仮想環境を推奨。
- 実依存解決・Colab T4生成はCI/Colabで未確認。PR CIのメタデータテストを確認する。


## 2026-11-13：PEFT依存追加後のColab LoRA実測

- ユーザーが修正版生成NotebookをColabで実行し、`torchao`をアンインストールせずにLoRAが動作したと確認。共有環境からの削除は不要。
- PEFT上流修正commitをNotebookに固定し、`diffusion` extraにもPEFTを明示追加したPR #67・#68をmainへ統合。PR #68のPythonテストCIは成功。
- wheel/sdistをCIで構築し、画像・マスク・モデル重み・データartifactの同梱なし、クリーンvenvからのwheel install/import成功を確認。Python 3.11〜3.13の全ユニットテストとpackage-smoke jobが成功。PyPI本番公開と大容量diffusion extraのクリーン環境での全依存解決は未実施。
