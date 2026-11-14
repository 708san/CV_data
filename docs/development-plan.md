# 完了：安定版0.1.0を公開し、`--pre`を通常導線から外す

更新日：2026-11-14。対象仕様：0.26、6。理由：利用者が毎回プレリリース指定を付けずに導入できるよう、alpha9から安定版へ移行する。

作業単位：1ブランチ・1PR。コード機能の変更は含めず、公開版メタデータ、利用者向け導入文書、Colab Notebook、公開記録をまとめて安定版に揃える。

作業順と受け入れ条件：
1. 仕様書へ安定版要件を先に記録する（完了）。
2. 本計画を先行記録する。版を`0.1.0`にし、Production/Stable classifierと固定Documentation URLを一致させる。PyPI README、全ガイド、エラー案内、Colab install行から`--pre`を外し、Notebookでは公開版`0.1.0`を固定する。alpha9以前の履歴記述は過去の事実として残す。
3. 通常版install、extraの依存解決、PyPI wheel/sdist、パッケージ内容、Notebook版固定、リンク・版表記、ネットワーク不要テストをCIで確認する。テストで安定版version/classifierとNotebookの版一致も確認する。
4. PRをCI成功後に統合し、GitHub Release `v0.1.0`からTrusted Publishingを実行する。PyPIのversion、wheel/sdist、README、Documentation URLを確認する。
5. 既存Colab検証はalpha9までの動作確認であり、安定版パッケージのColab再実行は別状態として正確に記録する。

完了条件：`python -m pip install cv-data-lesson`と各機能extraの通常導入で安定版が選ばれ、公開文書とNotebookに現行alpha向け`--pre`指定が残らず、CI・PyPI公開確認が成功する。

完了：PR [#107](https://github.com/708san/CV_data/pull/107)をCI成功後にsquash merge（`4a62ca7`）。GitHub Release [v0.1.0](https://github.com/708san/CV_data/releases/tag/v0.1.0)からPyPI Trusted Publishingを実行し、[PyPI 0.1.0](https://pypi.org/project/cv-data-lesson/0.1.0/)でversion・Production/Stable classifier・READMEリンク・Documentation URL・wheel/sdistを確認。wheel SHA-256 `41e206ad4f62ab220df5e1f96958dcee8fe33576b44db7b3a76e44dbb947d3a9`、sdist SHA-256 `6181fa864af6fbfef89be29c562efa2b2379169a8a04beda3471beeae4ecc3c2`。PR CIでPython 3.11/3.12/3.13、display、package-smoke、複数extra依存解決が成功。ローカルPython 3.12は106件成功・22件skip。新規一時venvで`pip install cv-data-lesson`を実行し、`0.1.0`選択、import、生徒向けデータ23件の一覧を確認。安定版でのColab再実行は未実施。

# 完了：文書更新をalpha9としてPyPIへ反映

更新日：2026-11-14。対象仕様：0.25、6。理由：GitHub mainのREADME・API・高校生向け案内は更新済みだが、PyPI本文はalpha8時点のスナップショットである。過去のPyPI更新依頼に基づき、alpha9として利用者へ届ける。

作業単位：独立ブランチ1件、版更新とNotebook/文書の同期を含む1PR。

作業順と受け入れ条件：
1. 本計画を先行記録する。PyPI版をalpha9に更新し、project Documentation URL、Notebookの公開版指定、Colab確認ガイド、画像生成ガイド、高校生向け版表示、PyPI公開履歴を一致させる。
2. Notebook固定版テストがalpha8を直書きしているため、`pyproject.toml`のプロジェクト版と各公開Notebookの指定を照合する方式へ更新する。OCR Notebookのextra確認も同じプロジェクト版を参照する。将来の版更新でテスト側の固定値が古くならないことを受け入れ条件にする。
3. ネットワーク不要テスト、Notebook構文・固定版検査、依存解決、wheel/sdist buildとclean installをPR CIで確認する。機能コードはalpha8から変更していないため、Colab実機再実行は新しい機能の検証として扱わない。
4. PRをCI成功後にmergeし、GitHub Release `v0.1.0a9`を作成してPyPI Trusted Publishingを実行する。公開後にPyPIの版・配布物・READMEリンクを確認する。
5. Colabでalpha9の新規install・全機能再実行は未実施と明記する。利用者へ再確認用のColab Notebookを示す。

完了条件：PyPIでalpha9が取得でき、配布名・version・README・project linksがalpha9のGitHub文書と揃う。CI成功、PyPI配布物確認後に完了とする。

完了：PR [#105](https://github.com/708san/CV_data/pull/105)はCI成功後にsquash merge（`73d2d15`）。GitHub Release [v0.1.0a9](https://github.com/708san/CV_data/releases/tag/v0.1.0a9)と[PyPI 0.1.0a9](https://pypi.org/project/cv-data-lesson/0.1.0a9/)を公開し、wheel/sdist、SHA-256、README内のAPI・高校生向けガイド案内、Documentation URLを確認した。Release workflowのbuild・metadata・禁止バイナリ検査・Trusted Publishingが成功。PR CIもPython 3.11/3.12/3.13、display、package-smoke、複数extra依存解決が成功。ローカルPython 3.12は104件成功・22件skip（任意依存なし）。alpha9のColab再実行は未実施。

# 完了：公開API・インストール・利用ガイドの最終整備

更新日：2026-11-14。対象仕様：0.25、6。目的は、公開中のalpha8を利用する高校生・教員が導入方法と実際のAPI契約を迷わず確認でき、AIに改造を頼む場合も実装にないAPIを作らせない状態に整えること。

作業単位：独立ブランチ1件、文書と仕様変更をまとめた1PR。

作業順と受け入れ条件：
1. 仕様書を先に更新し、正確なAPIリファレンス・インストール安定性・ガイド間の一貫性を要件化する。
2. ソースコード・公開シグネチャ・データカタログを確認し、メソッド、引数、既定値、入力、戻り値、副作用、制約を実装に沿ってまとめる。
3. README、導入案内、高校生向け案内、AI改造ガイド、機能ガイド、公開履歴の古いalpha表記・リンク・不要な`--upgrade`推奨を直す。Colabを通常の実行先として説明する。
4. ドキュメント内リンク、版表記、コード例の構文、`git diff --check`を確認し、リポジトリ規定のネットワーク不要テストを実行する。
5. 計画・進捗を完了状態へ更新し、PRを作成する。Colab実機で新規導入や重量級モデルを再実行した扱いにはしない。

完了条件：公開APIの使い方を一か所で調べられる。高校生向け説明とAI向け仕様が同じAPIを案内する。通常インストール、機能別インストール、Colabでの再実行手順が互いに矛盾しない。軽量テストと文書整合検査が成功し、未実施の実機確認は未確認と明示する。

進捗：PR [#103](https://github.com/708san/CV_data/pull/103)をCI成功後にmainへsquash merge（`0560d63`）。仕様0.25、公開APIリファレンス、高校生向け案内、AI改造ガイド、README、導入・機能ガイドを実装に照合して更新した。公開版リンクをalpha8へ揃え、Colabの通常installから`--upgrade`を外した。ローカルPython 3.12では104件成功・22件skip（Pillow・pandas等が未導入）。CIではPython 3.11/3.12/3.13、標準依存表示チェック、wheel/sdist build・clean venv install、複数extra依存解決がすべて成功。13文書のPython例・ローカルリンク、`git diff --check`も通過。Colabでの再実行、OCR実画像品質、GPU/重量級モデルの追加確認は未実施。PyPI・GitHub Releaseは作成していない。

# 完了：OCR全文表示をalpha8でColab確認

更新日：2026-11-14。対象仕様：0.24、4.2、5.3。利用者から、公開版OCR Notebookの全文優先表示を確認したとの報告を受けた。OCR全文の枠表示と折りたたみ詳細は確認済み。実行環境など未共有の情報は記録しない。

完了済み：OCR全文優先表示、行詳細の折りたたみ、OCRResult・OCRLine・to_dict()の互換性、ガイドとNotebook更新、PR #99のCI成功・main統合、Release v0.1.0a8とPyPI配布、Colabでの表示確認。データを他のUIへ渡すAPIの説明も案内済み。独立した他アプリ上での実装検証は未実施。

受け入れ条件：OCR全文が原文の改行を保つひとつの領域で読める。行別詳細を必要時に開ける。GPU名・Python版など未報告の実行条件や、未実施の別アプリ連携テストを確認済みと記録しない。

進捗：利用者確認を[Colab確認表](colab-verification.md)と[開発進捗](development-progress.md)に反映し、この作業を完了。
---

# 完了：ColabでのImage-to-Image確認を記録

更新日：2026-11-14。利用者がImage-to-ImageのColab動作を確認した報告をColab検証表と開発進捗へ反映する。OCR表示修正後の再実行は未確認のまま維持する。

作業順と受け入れ条件：
1. 本計画を先行記録する。
2. Image-to-Imageを利用者確認済みに変更し、実行条件の未報告状態は維持する。
3. OCR表示修正後の再実行は未確認のままにする。該当する日本語OCR Notebookへのリンクを利用者に示す。
4. 開発計画・Colab確認表・進捗の状態を一致させ、PR CI成功後に統合する。

進捗：Image-to-Image確認を記録したPR #95は全6 CIジョブ成功後にmainへ統合済み。OCR表示修正後の再実行は未確認のまま維持。今回の記録更新を完了。

---

# 完了：利用者報告のColab実測を検証表へ反映

更新日：2026-11-14。仕様0.22のColab実機検証記録を、利用者が確認した範囲に限って更新する。コード・Notebookの変更は行わず、ユーザー実測と未確認項目を区別する。

作業順と受け入れ条件：
1. 本計画へ先行記録する。
2. Colab確認表へ、分類（正解率0.825の報告を含む）、回帰、OCR推論、DETR/SAMとChromeアップロード、LoRAのユーザー報告を記録する。実行環境やLoRAの詳細が不明な箇所は「未報告」とする。
3. Image-to-ImageとOCR表示セルの再実行は報告がないため未確認のまま残す。
4. 開発進捗を更新し、文書間で実測・CI・未確認状態が一致することを確認する。
5. PRを作成し、CI成功後にmainへ統合する。

受け入れ条件：報告されたColab結果だけを実機確認済みにし、未確認の動作を成功扱いしない。

進捗：Colab確認表と開発進捗へ利用者報告を反映済み。Image-to-Image、OCR表示修正後の再実行、実行環境・LoRA IDの詳細は未確認として保持。PR #93は全6 CIジョブ成功後にmainへ統合済み。文書更新作業を完了。

---

# 実装・CI完了：ColabでのSAM重ね合わせ画像の二重表示を解消（Colab確認待ち）

更新日：2026-11-14。ユーザー実測ではDETR＋SAMは動作し、SAM表示セルだけ同じ画像が2回出る。`cvlesson.display.show()`は内部表示した後、合成画像も返すため、Colabがセル末尾の戻り値を自動表示して重複している。

順序と受け入れ条件：
1. 既存の`show()`の表示・戻り値契約は維持し、表示用Notebookでは戻り値を変数へ代入する。
2. DETR/SAM検証Notebookの末尾式を確認し、同じ出力の二重表示を防ぐ。
進捗：対象セルを`_ = cv_display.show(...)`にし、関数内での表示後にColabが戻り値を再表示する動きを抑止。SAM表示の説明例も戻り値を変数へ代入する形に変更。Notebook JSONと全Pythonコードセルの構文を確認済み。CIのPython 3.11/3.12/3.13、display-smoke、package-smoke、optional-dependency-resolutionは全て成功。Chrome上のColab再確認は未実施。
3. Notebook JSONと変更セルの構文を確認し、CIを通す。ユーザーがChromeで再読込して1枚だけ表示されるか確認する。

# 実装・CI完了：DETR・SAMの画像上の結果表示を明確にする（Colab確認待ち）

更新日：2026-11-14。対象仕様：0.22、4.3、5.3。既存の`cvlesson.display`が枠・ラベル・信頼度および半透明マスクを描けるため、Colab検証Notebookで可視化を一貫して使い、出力の意味と色を説明する。画像アップロードは利用者の希望に合わせてポップアップ方式を既定に戻し、Chromeで再確認できるようにする。

順序と受け入れ条件：
1. 仕様0.22を先に更新し、検出枠・ラベル・信頼度、SAM半透明マスク、DETR+SAM合成表示を要件化する。
2. DETR/SAM Notebookの画像入力セルをポップアップ式に戻す。画像パス指定は代替手段として案内する。
3. `cvlesson.display`を別名でimportし、DETR枠と検出クラス・信頼度を元画像へ重ねる。SAMは元画像と半透明マスクを見比べられる形にする。検出枠からSAMへ渡した結果も両方を重ねて表示する。
4. 表示の色・ラベル・スコアが何を示すか短く説明し、DETR閉集合検出とSAMのマスク出力の限界を維持する。
5. 検証NotebookのJSON・コードセル構文・CIを確認し、公開Notebookリンクを用意する。Colab T4実行はユーザーが共有するログを得てから実測済みに更新する。

受け入れ条件：検出がある場合は矩形・クラス名・信頼度が画像で見え、SAMは元画像に半透明で重ねて表示される。連携結果ではDETR枠とSAMマスクを同じ画像で確認できる。ポップアップ画像アップロードから推論までNotebookを実行できる。

進捗：DETR/SAM Notebookでポップアップ式アップロードを既定にし、パス指定へ切り替え可能にした。DETR上位5件までを黄色い枠・COCO名・信頼度付きで重ね、SAMの緑色半透明マスクと元画像を連続表示。DETR+SAMの合成結果とFruitSeg30比較も画像上で確認できる。`cvlesson.display`の既存APIを利用し、表示モジュールは`cv_display`としてIPython関数と衝突しない。Notebook JSON・全Pythonセル構文、PR #91のPython 3.11/3.12/3.13・display/package smoke・optional dependency resolution CIが成功。Chrome上のColab T4再実行は未確認で、利用者の実行ログ待ち。

---
# 完了：Colab画像アップロードのRangeErrorを回避

更新日：2026-11-14。ユーザー報告の例外は`files.upload()`実行時のColabフロントエンド由来で、OCR・検出モデル処理より前に発生する。Colab側の同型報告ではSafariで再現する例がある（[Colab issue #364](https://github.com/googlecolab/colabtools/issues/364)）。

順序と受け入れ条件：
1. この計画を先行記録する。既存の「自分の画像を使う」仕様は維持し、Colab upload widgetに依存しない入力手順を選ぶ。
2. 検出・画像生成のColab Notebookを、左側Files欄から置いた画像のパスを指定する方式に変更する。ファイルが見つからない場合は、Colab UIでの配置方法とパス例を表示する。
3. 生徒向けガイドと各機能ガイドのColab例も同じ方式に揃え、Drive上の画像を使う場合のパス指定を補足する。
4. Notebook JSONとコードセル構文を確認する。Colab実機再実行は利用者の実行ログで確認し、未実施なら未確認と記録する。

進捗：PR #89で検出・領域分割、画像生成のColab Notebookから`files.upload()`を除き、Colab左側のFiles欄からアップロードしたファイルのパスを設定する方式に変更。OCR・ResNet・検出・画像生成・データ形式・生徒向けガイドのColab例も同じ手順に更新。Notebook JSONとPythonコードセル構文を確認し、CIのPython 3.11/3.12/3.13、display-smoke、package-smoke、optional-dependency-resolutionが全て成功。PRはmainへマージ済み。Colabでの画面操作・ブラウザ実機確認は未実施。

# 完了：OCR Notebookのdisplay名衝突を修正

更新日：2026-11-14。対象：Colab OCR確認Notebookの表示例。今回の報告ではOCR推論・結果データは成功し、表示セルのみ`AttributeError`で停止した。

作業順と受け入れ条件：
1. IPython表示関数と`cvlesson.display`モジュールの名前衝突を確認する。
2. Notebook内で両者を別名（`notebook_display` / `cv_display`）にし、表示コードを更新する。
3. Notebook JSONを読み直し、表示セルの参照名とインストール版を確認する。Colabの再実行結果は別途確認し、未実施なら実機検証済みと書かない。

進捗：PR #87でIPython関数を`notebook_display`、`cvlesson.display`モジュールを`cv_display`として分離し、合成画像・OCR枠表示の呼び出しを修正。Notebook JSONの再読み込みで確認し、CIのPython 3.11/3.12/3.13、display-smoke、package-smoke、optional-dependency-resolutionが全て成功。PRはmainへマージ済み。Colabでの再実行は未確認。

---

# 完了：OCR・検出・生成の実使用エラーを修正し、alpha6を公開

更新日：2026-11-14。対象版：PyPI `0.1.0a6` / GitHub `v0.1.0a6`。PR #85はmainへマージ済み。Colab実機検証は未実施。

対象仕様：0.21、4.2〜4.4、5.1〜5.4、6、7。OCRの結果を読みやすくし、CPU版OCRを一つのextraから導入できるようにする。DETR出力とSAM連携で画像寸法の不一致・範囲外枠を扱い、画像生成のPEFT/TorchAO互換とNotebookのLoRA選択を改善する。

作業順と受け入れ条件：
1. 仕様0.21とこの計画を先行更新する。
2. OCRResultのraw fields・`to_dict()`を保ち、`str(result)`を行テキスト化する。画像表示を調整可能にし、OCR Notebookでテキスト表示と画像上の位置確認を示す。
3. `ocr` extraに標準CPU用PaddlePaddleを加える。GPU実行は公式のGPU wheelを必要とする例外として、CPU版と混同しない導入方法を示す。
4. Detectionに生成元の画像寸法を保持し、検出枠を有限かつ入力範囲内に整える。別寸法画像への`segment_detections()`では枠を拡縮し、直接予測では入力画像座標を保つ。
5. Diffusers/PEFT/TorchAOの報告エラーを一次資料と依存解決で調べる。通常のSDXL LoRA読み込みで既存の未使用TorchAO旧版が障害にならない形にし、外部モデルなしのテストを追加する。
6. 画像生成APIの既定値を利用者向けに明示し、Colab生成Notebookを単一LoRA選択式にする。モデル情報は一覧表示し、初期状態では選択した1件しか重みを取得・生成しない。
7. 複数extrasを同時指定する依存解決をdry-runし、競合を直す。CPU offline tests、Notebook JSON/Python構文、PR CIを確認する。
8. 修正版をPR/Release/PyPIへ反映し、公開PyPI版をColabで分類、回帰、OCR、DETR/SAM、画像生成（選択LoRA一つ）実行する。Colabランタイムへ直接接続できない場合は、Notebookと記録表を整えて利用者の実行ログで実測更新する。

進捗：PR #85をmainへマージし、GitHub Release `v0.1.0a6`とPyPI `0.1.0a6`を公開。Publish workflowのbuild・publish両jobが成功し、PyPI JSONでwheelとsdistを確認した。PR CIではPython 3.11/3.12/3.13、表示smoke、package smoke、OCR・vision・diffusion同時依存解決が成功。ローカルunit testsは101件成功、19件skip（optional依存未導入）。Notebookの実行・Colab T4でのOCR/DETR/SAM/SDXL実機確認は未実施で、[Colab確認表](colab-verification.md)の利用者実行待ち。
## 公開後の文書更新：alpha6公開状態へ同期

作業単位：公開記録、Colab実行手順、計画の現状表示を`0.1.0a6`の実際の状態へ更新する。

受け入れ条件：alpha6を公開済みと明記し、インストール・Colab手順から「公開後に実行」の表現を除く。Colab実機結果は未確認のまま保ち、公開成功と実機検証成功を区別する。

順序：本項を計画へ先行記録し、PyPIのversion/filesとGitHub Release/PRの状態を照合した後、公開記録とColab手順を更新する。文書のリンク・版表記と`git diff --check`を確認してPRにする。


対象仕様：0.20、5.1、6、7。利用者からの「PyPIとGitHubの表記差」「画像生成時のTorch導入」「実使用の問題点を列挙・改善」「使用ガイド」「全機能のColab実機確認」に対応する。既存の未コミット変更は別checkoutに残し、この作業ブランチでは触れない。

監査で確認した問題点（詳細：[ユーザビリティ監査](usability-review-2026-11-13.md)）：
- PyPIの表示はリリース時点で固定され、GitHub `main`は更新されるため、内容が時間とともにずれる。`cv-data-lesson`（配布名）、`cvlesson`（import名）、`CV教材ライブラリ`（表示名）の対応も初回利用で目に入りにくい。
- 基本installにはpandas・Pillow・表示依存が含まれているのに、`student-guide.md`は`to_df()`や画像表示にextrasが要ると案内し、データ別ページも旧extraコマンドを残している。
- `diffusion` extraは`diffusers[torch]`によりTorchを依存に含むが、インストール表は先にTorchを手動導入するよう読み取れる。
- `vision` extraはTorch/Torchvisionを含まないため、モデル利用者が別途導入する必要がある。機能別extraの意味が統一されていない。
- Colab smoke NotebookはPyPIのalpha4ではなく、異なるGit commitをインストールする。実際に配布されているwheelを確認したことにならず、OCR NotebookにはCV_dataを2回installするセルもある。
- 主要機能のColab Notebookは分かれているが、どれを何順で実行し、何を成功と記録するかの一枚の確認表がない。すべてを一ランタイムに入れると、OCRとPyTorch系の依存競合・SDXLの大容量取得に直面する。
- `street.jpg`など例中のプレースホルダー画像は、そのまま実行するとファイル未存在エラーになる。生徒向けガイドにアップロードまたはサンプル取得の前準備を明示する。

計画と順序：
1. 仕様0.20と本計画へ上の問題・受け入れ条件を先に記録する。
2. `vision` extraにTorch/Torchvisionを含め、通常は各機能のextra一回でPython依存が揃うようにする。`diffusion`は既にTorchを自動導入することを明記し、Colab・CUDAを自分で選ぶ場合の先行手順だけを例外として説明する。PaddlePaddleはOS/CUDAごとのwheelのため別導入を維持する。
3. 使い方ガイド・インストール表・データ別コード例・PyPI READMEの主文を同一導入方針に揃え、PyPI README内の詳細リンクをリリース版に紐づける。配布名/import名/日本語表示名を同じ場所で説明する。
4. 全Colab NotebookのinstallをPyPIの公開alpha版に統一し、Git checkoutではなくPyPIから配布されたartifactをテストする。OCRの重複install行を一つにする。
5. Colabの機能別実機検証一覧を追加する。データ取得と画像表示、分類、回帰、OCR、DETR、SAM、SDXL text-to-image/image-to-image、4 LoRAを対象とする。OCR CPU環境とPyTorch/T4環境は分ける。巨大モデル・データのローカル取得はしない。
6. `pyproject.toml`を次版alphaへ上げ、依存metadata・全offline tests・Notebook静的検査・wheel/sdistとCIを確認する。PRを作り、CI成功後にmerge/releaseする（公開権限は利用者の既存明示許可を適用）。
7. 公開PyPI版でColab Notebookを実行し、環境、GPU、パッケージ版、モデル取得、結果、エラーを記録する。Colabランタイムにこちらから直接接続できない場合、Notebookと手順を完了した状態で利用者の実行ログを受け取り、実測記録を更新する。

受け入れ条件：
- `python -m pip install --pre cv-data-lesson`後にデータ一覧・DataFrame・日本語画像例の表示まで追加extraなしでできる。
- `torch`、`vision`、`diffusion`は機能extraから依存を入れられる。GPU別PyTorchを公式選択する場合、およびPaddlePaddleは必要な理由を案内する。実行時にpip installはしない。
- PyPIの説明は配布名・import名・版・インストール・機能概要がGitHub側の案内と一致する。リリース時点のスナップショットとmainの更新差を誤認させない。
- 全Colab smoke Notebookが公開PyPI版をinstallし、実行順、ランタイム、データ/モデル量、出力確認が分かる。
- Colab実機で成功した機能だけを検証済みと記録し、GPU機能は実測したGPU名を残す。

進捗：監査を実施し、仕様0.20と本計画を先行更新。`vision` extraへTorch/Torchvisionを追加し、PEFT最低版を0.21.3へ更新。基本利用と機能別導入の不一致、画像パスの未定義例、ColabのGit commit直installとOCR二重installを修正。PyPI版固定の5機能NotebookとColab確認表を用意。Python 3.11/3.13で各92テスト成功（この作業環境では軽量optional依存が未導入のため18件skip）、Notebook JSON/Python構文・固定PyPI版検査、Markdownローカルリンク・コード例、`git diff --check`成功。PR #83のPython 3.11/3.12/3.13 unit、display-smoke、package-smokeは全て成功し、mainへmerge。`v0.1.0a5`をGitHub prereleaseとPyPIへ公開。PyPI JSONとwheel/sdistを確認し、Python 3.13の新規venvでPyPIからinstall、カタログ23件、`pip check`、基本import時にTorch未読込を確認。残作業は5機能の実Colab確認で、結果は[Colab確認表](colab-verification.md)に未実行として記録。

## 公開後の確認単位：alpha5クリーン導入と公開記録

対象仕様：5.1、6、7。PyPI `0.1.0a5`とGitHub `v0.1.0a5`が公開されたため、利用者向けの導入経路と公開履歴を事実に合わせる。

受け入れ条件：PyPI clean venvから基本インストール、`cvlesson` import、学生向けカタログ表示、依存整合性検査が通る。PyPI/GitHubの版、Documentationリンク、wheel/sdist SHA-256を記録し、Colab実行は実測前のまま明示する。

進捗：Python 3.13 clean venvへ`cv-data-lesson==0.1.0a5`をPyPIからinstall。`datasets.list_available(audience="student")`が23件を返し、基本importでTorchは読み込まれず、`pip check`は依存不整合なし。PyPI wheelは68,579 bytes / SHA-256 `7eefc0092d75a6d659ff7d15e67684ed856876d9f06e338e4d95f7ad0c433022`、sdistは81,799 bytes / SHA-256 `3286565bf31e81095df8db1bf18b0a66a02eb44a706661ac11e9e74a050f5ca0`。Colab実モデル検証は未実施。

## 今回の作業単位：公開後の利用者向け文書を再構成し、PyPI alphaを更新

対象仕様：1、2、4、5、6、7。現行`main`の`0.1.0a1`はPyPIへ公開済みだが、READMEに「未公開」と開発用editable installの説明が残っている。機能説明・モデルの入出力と限界・生徒がAIへ変更を依頼する仕様も散らばっている。最新実装とColabで実際に確認した範囲を照合し、利用者用の入口を作り直す。公開済み版を差し替えず`0.1.0a2`を作成してPyPI更新する。

順序：
1. 仕様0.17へ、利用者と開発者の文書分離、機能別の入出力・学習/推論・環境・制限説明、AI改造ガイドの必須要素を記録する（先行）。
2. 本計画へ対象・順序・受け入れ条件を記録する（先行）。
3. 最新`main`の公開API・データ件数・LoRA registry・実測状況を確認し、PyPI READMEを一般利用者向けの短い案内へ置き換える。開発checkout手順をPyPIのREADMEから除く。
4. 高校生向けガイドを作成し、データ選択から分類/回帰、OCR、検出、領域分割、画像生成の入力・出力・学習/推論・既定値・GPU・限界を現行実装に沿って説明する。課題例は自由に広げられる例として示す。
5. AI改造ガイドを高校生向けに書き直す。既存APIを使う一般的な依頼ひな形、必要情報、確認方法、変更してよい部分と維持すべき権利・データ条件を記載する。
6. インストール・quickstart・PyPI公開状況・開発進捗を一貫させ、実行可能な`--pre`コマンド、機能別extras、CPU/GPU選択、未確認範囲を明記する。
7. `pyproject.toml`を`0.1.0a2`へ更新。PR CIのunit・Notebook・package build/metadata/binary検査を通す。PRをmainへ統合した後、ユーザーの公開依頼に基づき`v0.1.0a2` GitHub Releaseを作成し、Trusted Publishing完了とPyPI JSONを確認する。

受け入れ条件：PyPI READMEに「未公開」「cloneしてeditable install」といった開発中の誤案内がない。一般利用者が公開PyPIからそのまま使えるインストールコマンドが先頭にある。機能説明が実装API・既定モデル・入出力・学習/推論・実測状況・制限と一致し、未実装機能を利用可能と書かない。AI改造ひな形は特定課題に閉じず、生徒が目的・データ・出力・成功条件を変えられる。alpha2がPyPIに現れ、wheel/sdistとRelease CIが成功する。

進捗：仕様0.17と本作業計画を先行記録。作業用コピーは公開済み`main` commit `f6975d3`から分離し、他のcheckout内未コミット変更には触れていない。生徒向けデータ23件と登録LoRA4件を実装から集計。README、学生ガイド、AI改造ガイド、quickstart、インストール案内、実行時依存エラー、PyPI運用記録を更新し、`pyproject.toml`を`0.1.0a2`へ変更した。Python 3.13ネットワーク不要テスト91件成功（18件skip）、利用者向けコード例15ブロック構文・Markdownローカルリンク66件・py_compile・`git diff --check`成功。ローカルbuild frontend不在のためwheel/sdistはPR CIに委ねる。CI・PR・Release・PyPI確認は続行中。

# CV_data 開発計画

更新日：2026-11-13

## 完了：Python 3.13での日本語フォント依存エラーを修正しalpha4を公開

対象仕様：5.1、6、7。PyPI alpha3をPython 3.13の新規venvへ実際に導入したところ、`japanize-matplotlib==1.1.3`のimportが削除済み`distutils`を参照して失敗した。PyPI install自体・データ一覧importは通るが、日本語Matplotlib表示の利用経路で問題になる。

順序：
1. 仕様0.19へ、Python 3.12以降のdistutils互換問題を避け、font packageに含まれるIPAexGothicを直接matplotlibへ登録する要件を記録する（先行）。
2. matplotlib font managerとimportlib.metadataからフォント資源を解決し、`japanize_matplotlib`のPython module importをしない実装へ変更する。フォントが見つからない場合は基本パッケージの再導入方法を示す。
3. mockベースの日本語フォント設定テストを配布metadata/resource lookupに合わせて更新し、missing resourceと正常登録を検証する。
4. 配布版を`0.1.0a4`へ上げ、PyPIから新規一時venvへinstallしてimport・データ一覧・フォント設定まで実行する。PyPI配布物にdataset/model binaryがないこととCIを確認する。
5. PRをmainへ統合し、ユーザー許可済みのGitHub Release/Trusted Publishingで公開。次のColab確認へ進む。

受け入れ条件：macOS/Python 3.13のクリーンvenvで`python -m pip install --pre cv-data-lesson`後、`datasets.list_available()`が動き、`show_examples()`がIPAexGothicを使える。`japanize_matplotlib`のimportに依存しない。既定のColab/Linux CIでも表示smoke、unit、package smokeが通る。

進捗：alpha3の実PyPI installで`distutils`問題を再現。仕様0.19と本計画を先行更新後、font packageのwheel resourceを`importlib.metadata`から解決し、matplotlibへ直接登録する実装とテストを追加。Python 3.11〜3.13のPR CI、display-smoke、package-smoke成功後にPR #81をmainへマージ。GitHub Release `v0.1.0a4`のTrusted Publishing成功。PyPIから新規macOS/Python 3.13 venvへ導入し、import・一覧取得・`show_examples()`でIPAexGothicを使う画像表示を確認。依存込み全91テスト成功（skipなし）。wheel 68,367 bytes、SHA-256 `83b19705bd9c10466558d2c3bb57f4059edb8b5d8b719e94545dc2ec497e5883`。sdist 81,279 bytes、SHA-256 `a984d0b1d2f1f279e3dd3ce52a4bf1efa18c41c4028d6af9e8734034ab0b`。

## 今回の作業単位：PyPIの初回利用導線を簡単にし、alpha3を準備

対象仕様：5.1、6、7。現在のPyPI説明では`[display]`を付けないと画像・表の確認ができるか分かりにくく、README内リンクもPyPI上で確実に開けず、見出しがPyPI自動表示の配布名・版と重なっている。標準導入後にデータを探して表示するまでの手順を短くする。

順序：
1. 仕様0.18へ「基本インストールに軽量な表・画像表示依存を含む」「PyPI READMEは自動表示見出しを重ねず絶対リンクにする」「初回例を題材選びから表示までつなぐ」を記録する（先行）。
2. `pyproject.toml`の標準依存にpandas、Pillow、NumPy、Matplotlib、日本語フォントを加える。重量級のAI framework・モデル重みは含めず、`display`/`dataframe` extrasは既存利用者との互換のため維持する。
3. README、インストール案内、quickstart、PyPI運用記録、依存エラー案内を一つの導入手順にそろえる。PyPI READMEの内部リンクはGitHub絶対URLにし、H1重複をなくす。alpha版で`--pre`が要る理由は短く示す。
4. 配布版を`0.1.0a3`へ進め、軽量依存が基本installにあること・重量級依存がないこと・導入例をテストで確認する。
5. ユニットテスト、Notebook検査、wheel/sdist・PyPI metadata・バイナリ検査、差分を確認する。PRを作成しCIを通す。PyPI公開後にインストールを再確認する。
6. 次の開発順を計画へ明示する：Colabのデータ→分類/回帰/OCR/検出/分割/生成フローの再確認、入力・出力・エラーの一貫性改善、stable化の受け入れ条件整理。

進捗：仕様0.18と本計画を先行更新。標準依存・PyPI README・クイックスタート・エラー案内・基本導入のテストを更新。Python 3.11〜3.13のネットワーク不要テストは各91件成功（各18件skip）。PR #79はunit、標準依存display smoke、package-smokeすべて成功してmainへマージ。GitHub Release `v0.1.0a3`を公開し、Trusted Publishing成功。PyPI JSONで0.1.0a3、wheel/sdist、summary、project URLsを確認。Colabでの公開版clean-install動作確認は次の作業。

受け入れ条件：PyPI利用者向けの基本コマンドが`python -m pip install --pre cv-data-lesson`の1つで、`datasets.get()`、`to_df()`、`show_examples()`まで追加extraなしで使える。PyPI READMEのリンクがすべて絶対URLで、配布名・版の重複H1がない。基本依存にtorch、PaddleOCR、Transformers、Diffusersを含まない。alpha3の説明が公開物と一致し、CI成功を確認する。

## その後の開発順

1. Colabの使い切り確認Notebookで、データ取得から各モデルの入力・出力までを再実行し、動いた環境・固定版・制限を記録する。
2. 初心者が迷うAPI差（データ形式、画像/パス入力、結果表示、予測値の読み方）を実データ例から優先順位付けし、仕様→計画→実装→テスト→教材文書の順で整える。
3. 安定版は、主要導線のColab確認、PyPI clean-install、Python対応範囲、optional extrasの互換、権利情報とデータ固定版、ユーザー向け説明の整合がそろった後に判断する。alpha表記を先に外さない。

## 今回の作業単位：PyPI初回alpha配布候補を整える（公開・アップロードは保留）

対象仕様：5.1、5.2、6、7。既存CIはwheel/sdist build、Twine、バイナリ混入、クリーン環境importを検査済み。PyPI配布名は`cv-data-lesson`、初回候補版は`0.1.0a1`とする。alpha版としてPyPIに登録できるよう metadata、README、Trusted Publishingの専用workflowと手順を整える。PyPI登録・GitHub Release/tag作成・アップロードはこの作業単位に含めない。

事前確認：
- 2026-11-13にPyPI JSON APIへ`cv-data-lesson`を照会しHTTP 404。確認時点で登録は見つからなかったが、名前は公開されず予約もされていないため、登録時に取得済みとは限らない。
- CIで`twine check dist/*`と禁止バイナリ・軽量wheel import検査が成功している。
- READMEに旧作業ブランチ固定リンク、現状と合わないColab未実行の表記がある。PyPI表示文書として整理する。

順序：
1. この作業単位と完了条件を本計画へ記録する（先行）。
2. pyprojectを初回alpha候補（`0.1.0a1`、Alpha classifier）に合わせ、コード・データを分離して配布することを明記する。
3. READMEと公開導入・機能別extrasの案内を現状にそろえ、旧branch URL、誤解を招く権利・実行状態の説明を直す。
4. GitHub Release公開イベントにだけ反応する専用`publish.yml`を用意する。tagとpyproject版を一致検査し、build・Twine・禁止バイナリ検査後にTrusted PublishingでPyPIへ送る。OIDC権限はpublish jobだけに与える。
5. PyPIのpending Trusted Publisher設定に必要なrepository/workflow/environment情報と、公開前確認手順を文書化する。
6. wheel/sdist、Twine、禁止バイナリ、クリーン環境導入、unit matrixをPR CIで確認する。PyPI/TestPyPIへのアップロードは行わない。

受け入れ条件：`0.1.0a1`のwheel/sdistをbuild・twine checkできる。画像・LoRA・モデル重みを含まない。READMEのPyPI表示、利用コマンド、任意依存説明がmetadataと一致する。release workflowは版の一致時だけPyPIへ発行し、workflow_dispatchやpush tagで誤発行しない。初回登録はpending Trusted Publisherを使う手順が明確で、公開実行前にPyPI側設定と明示承認が必要な状態を保つ。

進捗：初回候補版`0.1.0a1`とAlpha classifier、PyPI公開後の導入説明、pending publisher設定手順、Release限定のTrusted Publishing workflowを追加。PyPI JSON APIは2026-11-13時点でHTTP 404（名前の予約を意味しない）。Python 3.11/3.13で91テスト成功（各18件skip）、workflow YAMLと`git diff --check`成功。mainの既存package-smoke CIはwheel/sdist、Twine、禁止バイナリ、クリーンvenv importを検査済み。PR #76はmainへマージ済み。Python 3.11〜3.13 unit、display-smoke、package-smoke（wheel/sdist build、Twine、禁止バイナリ、クリーンvenv import）は全て成功。Release公開イベントは発生していないためpublish workflowは未実行。PyPI upload、GitHub Release/tag作成は未実施。
## 完了：SDXL/LoRAの生成設定を使いやすく説明

対象仕様：4.4、5.5、6、7。APIにはsteps、guidance、seed、出力サイズ、negative prompt、Image-to-Image strength、LoRA triggerの指定が既にあったため、新APIは追加せず、仕様0.15・ガイド・Notebook・テストを整備。Notebookを6 steps/512pxの速度優先から25 steps、guidance 7.0、768px、seed 42を変更可能な品質比較例へ更新。PR #71をmainへマージし、Python 3.11〜3.13のユニットテストとpackage-smokeを確認。ユーザーがColab動作を確認済み。実行時のVRAMや詳細な品質比較値は未記録。

## 完了：PyPI配布メタデータ検査をCIへ追加

対象仕様：5.1、7。wheel/sdist build後の配布メタデータをTwineで検査する。

実施内容：
1. package-smoke CIにTwineを追加し、build直後に`python -m twine check dist/*`を実行。
2. データ・モデル等の禁止バイナリ検査とクリーンvenv導入確認を維持。
3. PR #72をmainへマージ。Python 3.11、3.12、3.13のunit jobとPython 3.13 package-smoke job（build、Twine check、バイナリ検査、import）がすべて成功。

PyPI/TestPyPIへのアップロードは未実施。

## 完了：LoRA生成設定のColab動作確認

対象仕様：4.4、5.5、6、7。PR #71で25 steps・guidance 7.0・768×768を初期設定とし、seed、negative prompt、画像変換strengthなどをNotebookから調整できるようにした。ユーザーがColabで確認済み。実行時のGPU使用量や詳しい品質比較値は未記録のため、数値実測としては扱わない。

## 完了：日本語表示extraをCIで実環境確認

対象仕様：5.1、5.2、7。display extraにはMatplotlibとjapanize-matplotlibがあるが、現在のCI unit jobはtest extraだけを導入する。日本語フォント設定はmock testのみで、実パッケージの導入・フォント参照をCIで確かめていない。

順序：
1. この作業単位と受け入れ条件を計画へ記録する（先行）。
2. Python 3.13の独立CI jobで[test,display] extrasを導入して全オフラインテストを実行する。
3. 実際のjapanize-matplotlibが提供するフォントファイルを読み、存在・ファミリー名を確認するネットワーク不要の統合テストを追加する。通常の[test]環境では任意依存としてskipする。
4. CIの依存導入と全テストの結果を確認し、開発進捗を更新する。

受け入れ条件：既存のmockテストを維持しつつ、CIのdisplay jobでjapanize-matplotlibの実フォントパスが有効であることを確認する。画像・モデル・データのダウンロードを行わず、通常の軽量test jobを重量級依存で膨らませない。

進捗：Python 3.13の独立display-smoke jobでdisplay extra導入と実フォントパス検査を実行。全テスト成功。通常のPython 3.11〜3.13 unit matrixとpackage-smokeも成功。

## 完了：画像生成パラメータの事前入力検査

対象仕様：4.4、5.5、6、7。stepsやstrengthの既存検査ではNaN、無限大、bool、文字列などがすり抜け、幅・高さ・seed・negative promptの不正値はDiffusersまで届く可能性がある。設定ミスをモデル実行前に短い日本語で伝える。

順序：
1. 仕様0.16へ受け付ける型・値域・画像寸法条件を追記する（先行）。
2. 生成pipelineを呼ぶ前に全設定を検査し、NaN/inf、bool、型違い、不正な寸法などをValueErrorで拒否する。
3. モデル重みやDiffusersを使わないテストで、有効値の引き渡しと境界値・型違いを確認する。
4. 画像生成ガイドと進捗へ利用者向けの条件を簡潔に記載し、Notebook JSON・全CIを確認する。

受け入れ条件：stepsは正の整数、guidance_scaleは有限かつ0以上、strengthは有限な0〜1、width/heightは指定時に正の8の倍数、seedは整数かNone、negative_promptは文字列かNone、use_triggerはboolとして検査する。無効値でpipelineが一度も呼ばれず、値の直し方が分かるエラーになる。

進捗：事前検査、境界値・型違いテスト、クイックスタートと画像生成ガイドを更新。PR #75のPython 3.11〜3.13 unit、display-smoke、package-smokeがすべて成功。
## 完了：画像生成extraへLoRA実行依存PEFTを含める

対象仕様：4.4、5.1、5.2、7。`diffusion` extraへ`peft>=0.21.2,<1`を追加し、依存メタデータテストと導入案内を更新。PR #68をmainへマージし、CI成功。ユーザーがColabで修正版Notebookを実行し、torchaoをアンインストールせずにLoRA生成が動作することを確認。

## 完了：PyPI wheel/sdistとクリーン環境の基本導入を検証

対象仕様：5.1、5.2、7。PyPI本番公開前にwheel・sdistを作成し、内容物にPythonコード以外の画像・モデル重み・データartifactが紛れないことと、クリーン環境で軽量な基本install/importが通ることをCIで確認する。大容量依存とモデル重みを使う確認はこのCIへ含めない。

順序：
1. `docs/specification.md`、本計画、既存CI、pyprojectのbuild設定とパッケージ構成を確認する。
2. この作業と完了条件を計画へ記録する（完了）。
3. CIへwheel/sdistのbuild・内容物検査・一時venvでの`--no-deps` install/import smokeを追加する。
4. Python対応版で通常ユニットテストとpackage smokeを実行し、成果物を保存・公開せずCI内で破棄する。
5. PyPI本番公開・アップロードは行わず、build結果と未確認の大容量extraを計画・進捗へ記録する。

受け入れ条件：wheelとsdistが構築でき、`cvlesson`をimport可能なPythonコードを含む。データ・LoRA・画像の大容量バイナリを含まない。クリーンvenvへのinstall/import smokeと既存テストが成功する。Diffusers/PEFTの完全な依存解決やColab生成は、別途実環境で確認した範囲だけを成功と記録する。

進捗：PR #69をmainへマージ。CIのpackage-smoke jobでwheelとsdistを構築し、禁止バイナリ・artifactディレクトリが含まれないこと、50MB超のファイルがないことを確認。wheelを新規venvへ`--no-deps`で導入して`import cvlesson`とデータ一覧呼び出しに成功。Python 3.11、3.12、3.13の全ユニットテストも成功。PyPIへのアップロード、Diffusers/PEFTの全依存導入は未実施。

## 今回の作業単位：Colab旧TorchAO競合をLoRA環境を壊さず解決

対象仕様：4.4、5.1、5.2、7。Colab T4でLoRA 4件が、事前導入torchao 0.10.0とPEFT 0.19以降の互換性問題で失敗した。PEFT修正PR #3989のmerge commit `c2d5f697fbb30063cbde6f39e2734883b70b8753`を確認。共有ランタイム上でtorchaoをアンインストールする手順は取りやめ、修正を含むPEFT commitをNotebookだけで固定導入する。ローカル利用は仮想環境を推奨する。

順序：
1. 仕様4.4・5.1・5.2、生成Notebook、PEFT上流の修正内容を確認する。仕様変更は不要なColab向け互換修正とする。
2. この計画を先に更新する。
3. 生成Notebookからtorchao削除セルを外し、ライブラリの固定commitとPEFTの修正merge commitを導入するpip行を追加する。PEFT修正の公開版が提供されたら、固定commitから版指定へ切り替える。
4. 利用者文書にローカルの仮想環境を推奨する説明を必要な範囲で追記し、開発進捗を更新する。
5. Notebook JSON・セル順・コード構文・40桁固定参照を検査し、PRで統合する。

受け入れ条件：Colabでtorchaoを削除せずにLoRA読み込みを開始できる。PEFTは既知修正を含む固定commitを使う。標準の新規仮想環境では依存を隔離して導入できる。T4実生成はColabで再実行成功を得るまで未検証とする。

進捗：方針変更。PR #66のアンインストール手順は、共有環境への変更を避けるため、PEFTの修正commit導入へ置き換える。

## 今回の作業単位：空画像・翌日天気データを利用可能にし、生成Notebookの固定版ずれを修正

対象仕様：3.1〜3.3、4.4、5.1、6、7。空画像・翌日天気データを成果物Release、registry、ライブラリAPIの順に統合し、SDXL/LoRA Notebookで起きた`capabilities_ja`のKeyErrorを解消する。

事前確認：
- データartifact Releaseは公開済み。GitHubから再取得したファイルは10,014,277 bytes、SHA-256 `c438ca3444bf72773d4a7bb430ed3f20885db8fbb0fd5d3f00ee7727149564e0`で一致。
- 成果物registry等を含むCV_data_artifacts PR #49はmainへマージ済み。ライブラリ登録PR #64は本ブランチ（PR #63のhead）へマージ済み。
- 生成NotebookはCV_data固定commit `635fa30db261ae5b3d43ab87c9e5f9e66a78bd1a`をインストールしていた。この版の`loras.list_models()`は`capabilities_ja`を返さない。PR #63の現行コードcommit `940ae09babebc698563b7cf3a35bd842840388f5`では当該項目を返すことを確認した。

順序：
1. PR #49の成果物manifest・権利記録・台帳と、Release assetの固定URL/SHAを確認して成果物側を統合する。
2. 生成Notebookのインストール参照を、`capabilities_ja`を含む完全な40桁commitへ更新する。見出し・授業順・生成コードは変更しない。
3. NotebookのJSONとセル構文・固定参照を確認し、開発進捗へ原因と修正を記録する。SDXL実行はColab T4で行う。
4. PR #64をこのPRのbase branchへ取り込み、成果物データ/APIとNotebook修正を同じライブラリ変更としてmain向けPR #63から公開する。
5. 変更対象のPRレビュー状態とCI結果を確認してから統合し、最終状態を開発計画・進捗へ記録する。

受け入れ条件：成果物registryとライブラリが同一固定URL・SHAを参照し、マージ後に`datasets.get("sky_weather_next_day")`で取得できる。Notebookの指定commitで`loras.list_models()`が`capabilities_ja`を含み、表示セルがKeyErrorなしで実行できる。GPU実生成を行っていない場合はColab未確認と明記する。

進捗：CV_data_artifacts PR #49をmainへマージ済み。Release assetを再取得してサイズ・SHA一致を確認済み。LoRA一覧の`capabilities_ja`を含まない古いcommitをNotebookが固定していた原因を特定し、`940ae09babebc698563b7cf3a35bd842840388f5`へ更新しました。CV_data PR #64のデータ・API登録はPR #63のhead branchへマージ済みです。PR #63は2026-11-13にmainへマージ済み（`a824ee96d0123843ba58c6cf0df299656903e545`）。データのColab実取得とSDXL実生成は未確認です。


## 今回の作業単位：分類Notebookの`predict_proba()`型不一致を修正

対象仕様：4.1、7。`_predict_values()`はNumPy配列を返す一方、`predict_proba()`がTensorを想定する`torch.softmax()`へそのまま渡し、ColabでTypeErrorになった。既存のscikit-learn風Estimator APIの不具合として修正する。

順序：
1. 仕様4.1の出力層学習と`fit/predict/score`中心の呼び出し方を確認する。仕様変更は不要な不具合修正とする。
2. `predict_proba()`へ渡す前にNumPy logitsをTorch Tensorへ変換し、返り値を既存の確率目安のNumPy配列形式で保つ。
3. ネットワーク・モデル重みを使わず、NumPy形式のlogitsがsoftmaxに渡り、各行が正規化されるテストを追加する。
4. 分類・回帰Estimatorと基盤モデルAPIの呼び方を、実装と説明文書から短い対比で提示する。
5. 全ユニットテスト、Notebook検査、差分を確認する。Colab実画像で再実行していない部分は未確認と記録する。

受け入れ条件：Colabログの`softmax input must be Tensor, not numpy.ndarray`を修正し、`predict_proba()`が形状`(サンプル数, クラス数)`の行ごとに正規化された確率目安を返す。既存の分類・回帰のscikit-learn風Estimator APIとOCR/vision/generationの用途別APIを混同させない。

進捗：`predict_proba()`でNumPy logitsを`torch.as_tensor()`に変換してからsoftmaxへ渡す修正を実装。外部モデルを使わない型変換・確率行和のテストを追加。分類・回帰EstimatorとOCR/DETR/SAM/SDXLの呼び出し方をクイックスタートへ追記し、確率配列の形状と意味を文書化。Python 3.13で全85テスト成功（16件skip）、`git diff --check`成功。ユーザーがColab分類Notebookと回帰Notebookの正常動作を確認済み。他の機能のColab再確認は未完了。

## 今回の作業単位：Notebookのケアレスミス検査とMatplotlib日本語表示

対象仕様：5.1、6、7。分類Notebookのインストール行で閉じ引用符が欠けた不具合をきっかけに、全Notebookの変数・実行順・構文・インストール指定を再点検し、ライブラリ自身が作るMatplotlib図を日本語表示できるようにする。

順序：
1. 仕様0.13に、Matplotlibの日本語フォント自動設定、機能別依存、Notebook公開前の静的検査要件を記録する。
2. この計画へ、全Notebook監査、再発防止の自動検査、`display` extraへの`japanize-matplotlib`追加を記録する。
3. すべての配布Notebookを解析し、JSON/Python構文、未定義名、セル実行順、`%pip install`の引用符と固定参照を確認する。誤りは最小限に修正し、既存Notebookの見出し・記入欄・授業順を保つ。
4. `DatasetBundle.show_examples()`で日本語設定を遅延適用する。フォント名のrcParams設定だけに依存せず、IPAexGothicの実ファイルを`FontProperties`でタイトル・注釈へ明示し、依存案内とテストをそろえる。
5. ネットワーク不要テスト、Notebook全件検査、パッケージメタデータ、差分を確認する。

受け入れ条件：全Notebookのセル構文と静的変数検査が通り、導入セルからimportまでの順序が正しく、pip行の引用符・固定参照に誤りがない。ライブラリのMatplotlib出力は`display` extra導入時に日本語フォントを自動設定し、コアimportやMatplotlibを使わない機能では日本語化依存を読み込まない。Colab実行をしていないものは未検証と記録する。

進捗：全配布Notebookを調べ、分類Notebookの未定義`df`を`frame`へ修正。標準ライブラリだけでNotebook JSON・セル構文・セル間グローバル名・pip引用符・CV_data Git URLの40桁固定参照・install前のimportを確認するテストを追加。`display` extraに`japanize-matplotlib`を追加し、`show_examples()`内で描画時だけ日本語フォント設定を適用。`display`にDataFrame依存も含め、表示導線の追加指定を減らした。Python 3.13で全84テスト成功（16件skip）、Notebook検査3項目成功、`git diff --check`成功。Colab画面でGlyph警告と日本語の豆腐表示を確認。IPAexGothicフォントファイルをタイトル・注釈へ明示する実装とmock testを追加し、関連10テスト成功。完全な描画依存がこの環境になく、実字形のレンダリングと修正版のColab再実行は未確認。ruff/pyflakesの一時導入はネットワークDNS制限でできなかったため、標準ライブラリ検査で確認。

## 今回の作業単位：初心者向けの導入・データ・推論体験を改善

対象仕様：1、3、4、5、6、7。ColabでOCR CPUとDETR/SAM T4の実モデル推論を確認済み。初回インストールから入力・結果確認・データ利用までの使いやすさを改善する。

改善計画：[利用しやすさ改善計画](usability-plan.md)。対象は導入方法、課題からのデータ選択、データ形式とモデル入力の接続、各モデルの出力表示、課題解決例、実環境での再現確認。

順序：
1. 実測済み環境・API・データ形式をコードと文書から棚卸しし、現状説明の食い違いを直す。まず`docs/installation.md`と`docs/vision.md`のDETR/SAM確認状況を更新する。
2. 初心者の利用導線を、CPUローカル・Colab CPU・Colab T4と機能別extraごとに整理する。PyPI公開前後のインストールコマンドを区別する。
3. `DatasetBundle`の各task形式とモデルAPIを対応表にし、取得後のサンプル表示、画像・ラベル・注釈へのアクセス、モデル入力までの変換手順を確認する。
4. APIの入力型と戻り値を機能横断で比較し、パス変換・結果の可視化・保存に必要な最小の共通体験を設計する。新APIが仕様にない場合は仕様書を先に更新する。
5. 課題選択から実行・結果確認までを通す短い例と、各taskの1機能Notebookを用意する。
6. 既存の単体テストに加え、新規環境・Colabでの主要フローを確認し、対応環境と限界を記録する。

受け入れ条件：機能ごとの導入選択が明確で、掲載データの取得から内容確認・タスク形式へのアクセス方法が分かり、画像入力からモデル結果の確認までのコードが簡潔で一貫する。ライセンス・データ形式・モデル出力の意味・GPU明示選択・遅延取得を維持する。実測していない動作は確認済みと書かない。

進捗：仕様0.12へ利用者自身の画像を使う要件を追加。クイックスタートにローカルパス/Colabアップロードを追記し、DETR/SAM Notebookはアップロードまたは合成画像を選べる形に更新。SAMの矩形入力を画像サイズに合わせた。今回、分類Notebookを独自CNNから`ResNetClassifier`へ変更し、登録済みトマト画像でtrain/validation/test・推論を確認可能にした。LeFood-Set用`ResNetRegressor` Notebookを追加。OCR Notebookに非商用条件を明記した公開実レシート推論、DETR/SAM NotebookにFruitSeg30 test画像と正解マスク比較を追加。SDXL/LoRA Notebookに任意の利用者画像を使う選択を加えた。全NotebookのJSON・コード構文、`git diff --check`、Python 3.13テスト79件成功（16件は任意依存不足でskip）を確認。Colab上での新しいデータ取得・学習・推論・実画像表示は未確認。

### 今回の作業単位：分類・回帰・推論APIを実データで確認するNotebook

対象仕様：3.2、4.1〜4.3、5.4、6、7。既存の分類Notebookは独自CNNを学習しており、提供APIのResNet分類Estimatorを検証していない。実データを使う分類・回帰の学習/分離評価と、OCR/SAM基盤モデルの実画像推論を確認するColab手順を整える。

順序：
1. 仕様・データ説明・コードから分類用`tomato_leaves`と回帰用`lefood_set`の固定版、権利表示、列名、split、ターゲット単位を確認する。データartifactは既存の固定取得APIを使い、Notebookへ複製しない。
2. `notebooks/cv/classification_v1.ipynb`の見出し・授業順・記入欄を保ち、独自CNN部分をResNetClassifierの`fit/predict/predict_proba/score`を使う実データ例へ更新する。
3. Colab用にLeFood-SetのResNetRegressor Notebookを追加し、画像ペアでの学習、validation/testのR²、実測値と予測値の比較を含める。
4. OCR NotebookではCC BY-NC 4.0の実レシートを1枚推論し、非商用条件・残存情報・部分注釈の注意を明記する。全面OCR正解でないためCER等の自動評価は行わない。
5. DETR/SAM NotebookではFruitSeg30の固定Release test画像を取得し、SAMに正解マスクから得た枠をpromptとして渡す比較例を追加する。単一画像のIoUは動作確認例に限ると説明し、モデルの一般性能の評価と混同しない。
6. 過学習や長時間化を避ける固定seedのサンプル上限を設け、train/validation/test間の混入を避ける。評価指標が低い・負の値でも、Notebookを失敗扱いにせず実測結果として表示する。
7. Colab起動リンク、固定commit、環境要件、権利・データ上の限界を記し、Notebook JSON・コード構文・既存ネットワーク不要テストを検証する。

受け入れ条件：分類と回帰の両方で、登録済み固定Releaseデータの明示取得から、trainでの学習、validation/testでの分離評価、未見サンプルの推論までを追える。OCRとSAMは権利・注釈の範囲を説明した上で公開実データ画像を推論に渡す。分類Estimatorと回帰Estimatorの実APIを使い、異なるtaskのラベル・単位を混同しない。実Colabで実行していない場合は未検証として記録する。

進捗：Notebook実装・構文検査・ネットワーク不要テストまで完了。classification_v1、ResNet回帰、OCR実レシート、FruitSeg30/SAMのColab手順を追加・更新。Colabログでclassification_v1のpip installコマンドに閉じ引用符がない問題が分かり、修正を追加。全Notebookのinstallコマンド引用符も確認する。Python 3.13テスト79件成功（任意依存不足で16件skip）。データReleaseの実ダウンロード、ResNet学習、PaddleOCR実レシート推論、SAM実データIoUはColabで未実行。

### 今回の作業単位：利用者自身の画像をColab・ローカルで使う導線

対象仕様：5.4、6、7。モデルAPIはローカルのファイルパスとPillow Imageを受け取れるが、利用者がColabへ自分の画像を持ち込む具体例が不足している。追加の画像変換やプロジェクトへの複製を求めず、基本入力形式のまま利用できる手順を用意する。

順序：
1. 仕様0.12にローカル画像とColabへ明示アップロードした画像の扱い、外部への自動送信をしない境界を記録する。
2. クイックスタートにローカルパスとColabアップロードの短い例を加え、どちらも同じAPIへ渡すことを示す。
3. 固定commitで動くColab検出Notebookに任意画像のアップロード手順を追加する。合成画像の動作確認も選べるようにし、SAMの入力枠を画像サイズから決める。
4. Notebook JSONとコードセル構文、ローカルのネットワーク不要テストを確認する。実Colabでの画像アップロード・推論・表示は実際に実行した場合だけ検証済みにする。

受け入れ条件：利用者が画像ファイルを選び、画像をライブラリ形式に変換する手作業なしで、推論APIに渡せる。入力画像をリポジトリへ保存せず、Colab外への送信をライブラリが自動実行しない。特定の画像や課題に用途を限定しない。

進捗：完了（ローカル実装・構文確認まで）。ローカル画像/Colabアップロードの例と、アップロードまたは合成画像を選べるDETR/SAM・SDXL Notebookを追加。SAMの枠を画像寸法に連動させた。Colab実行での確認が残る。

### 作業単位：データ形式とモデル入力の対応表

対象仕様：3.2、4.1〜4.4。コードだけでデータを`get()`した後にモデルへ渡す形が分かりにくいため、公開データごとの保存形式・`DatasetBundle`の操作・対応するモデル入力を照合する。

順序：
1. 公開中のデータカタログからID・task・kind・split・画像/注釈形式を列挙する。
2. `to_df()`、`to_torch_dataset()`、個別フィールドを確認し、取得後に利用できる形を分類する。
3. ResNet、OCR、検出、SAM、画像生成が実際に受け取る型と、返却型を対応づける。
4. 変換が存在する箇所、利用者の手作業、現状仕様で未対応の組み合わせを区別した表を作る。未実装のAPIは紹介しない。

受け入れ条件：公開中の各データについて、取得API・内容確認方法・タスク別レコード・対応モデル入力が分かる。分類・回帰・検出・領域分割・OCRの非対応機能を学習可能と誤認させない。

進捗：完了。`datasets.list_tasks()`と`list_available()`で生徒向け22件を再集計し、`to_df()`・`to_torch_dataset()`、ResNet、OCR、DETR、SAM、SDXLの入出力を実装と照合。`docs/data-model-compatibility.md`に全22件のタスク別形式、接続例、非対応範囲を記録した。対応表はソース監査であり、データ全量の再監査ではない。

### 作業単位：推論結果の共通描画・表示・保存

対象仕様：5.3、6、7。検出・OCR・領域分割の予測結果を元画像へ重ねる処理を、初心者が利用できるAPIとして追加する。

順序：
1. 仕様0.10へ画像と結果型、合成後画像、表示・保存の契約を先に追加した。
2. 画像パスまたはPillow Imageを受け、入力や結果を変更せずPillow Imageを返す描画APIを実装する。
3. OCRポリゴンと文字、検出bbox・ラベル・score、SAMマスク、検出とSAMの組を描画し、画像サイズ・座標・mask形状を検査する。
4. Notebook表示とファイル保存を追加依存を機能呼び出し時にだけ使って実装する。SDXLのPillow出力もそのまま表示できるようにする。
5. 合成fixtureによるネットワーク不要テストで全結果型、入力非変更、保存先を検証し、API説明と利用例を更新する。

受け入れ条件：学生が自分でmatplotlibの描画コードを組まずに、OCR・検出・SAMの結果を元画像と確認できる。描画結果をPillow Imageとして後続処理へ渡すか、指定先へ保存できる。表示・保存は明示操作でのみ行い、SAMの品質予測値を確率として表現しない。

進捗：完了。`cvlesson.display.render/show/save`を追加。OCR文字枠、DETR bbox、SAM半透明mask、DETR+SAM結果を合成し、Pillow Image返却・Notebook表示・指定パス保存に対応。ネットワーク不要テストを含む79件成功（5件skip）。Colabでの表示と各OSの日本語フォント表示は未確認。

### 作業単位：画像入力・汎用例・導入案内をそろえる

対象仕様：3、4、5、6、7。現状の画像入力型を再確認し、初心者が手元画像・データ画像を扱う例と、目的別に選べる導入案内を整える。例は基本操作を示す短い雛形とし、特定データや課題に用途を限定しない。

順序：
1. 各機能が受け取るパス、Pillow Image、NumPy型を実装とバックエンド仕様で確認する。
2. 利用者が扱いやすく、安全性と既存API互換性を保てる共通入力を決める。API拡張が必要な場合は実装前に仕様書を更新する。
3. データ選択、サンプル確認、分類・回帰、OCR・検出・領域分割、画像生成を網羅する汎用最小例を用意する。具体的なデータIDは差し替え可能と示し、能力外の用途を例で限定しない。
4. インストール案内の先頭に、PyPI公開前の開発checkoutと機能ごとの選択表を置く。PyTorch/PaddlePaddleのCPU/GPU別手順、環境分離、GPU確認の詳細は保つ。
5. 文書・Notebookのコードセルを構文確認し、APIの入力形式と既存のネットワーク不要テストを検証する。

受け入れ条件：画像入力型が機能ごとに明示され、対応追加後はパスとPillow Imageの扱いが一貫する。短い例はデータ取得・入力・実行・出力の基本を示し、特定の用途に固定しない。インストール入口から利用者が目的のextraとCPU/GPU準備へ進める。未公開のPyPI packageをインストール可能と案内しない。

進捗：ResNet分類・回帰の学習/予測、DETR、SAM、OCRで画像パスとPillow Imageを受け取れるようにした。OCRは内部一時PNGを推論後に削除し、`ocr` extraへPillowを追加。NumPy画像は非対応としてエラーを明確化。`docs/quickstart.md`を題材を固定しない形で追加し、READMEをカタログから選ぶ流れに変更。`docs/installation.md`冒頭に目的別の導入表を追加。ネットワーク不要テスト79件成功（5件skip）、Pillow/NumPyを一時領域だけに入れて入力・一時ファイル削除・表示のテストを実施。Colabでの新画像入力・表示、実モデル推論は未確認。インストールと例の導線は更新済み。

## 今回の作業単位：SAMスコアの範囲を誤って固定したColab確認を修正

対象仕様：4.3、7。ユーザーのColab T4ログでDETR推論が成功し、SAMモデルの取得・読込とマスク形状・bool型の確認も通過したが、Notebookの`0 <= score <= 1`だけが失敗した。SAMのIoU品質ヘッドは範囲を保証する確率出力ではないため、仕様と確認コードを合わせる。

順序：
1. 仕様書へSAMスコアが実IoU・確率ではなく、0〜1範囲を保証しない予測値であることを明記する。
2. API説明・Colab Notebookのスコア説明を直し、有限数であることのみ検証する。
3. ネットワーク不要テストで0〜1外のスコア値を保持することを確認する。
4. Notebook構文と全テストを確認し、固定commitを更新して作業ブランチへ反映する。

受け入れ条件：SAMスコアが0〜1外でもAPI・Notebookが誤って失敗しない。スコアを確率または実測IoUと誤認しない説明が仕様・利用者文書・Notebookで一致する。

進捗：仕様0.9.1へ変更理由を記録。DETRは合成画像中の`kite`を0.706で検出。SAMのモデル重み取得、boolマスク、重ね合わせ表示をユーザーのColab T4で確認。スコア範囲assertionだけが誤っていたため、APIは未加工の品質予測値を返す仕様を文書化し、Notebookは有限数を確認するよう修正。ネットワーク不要テスト69件成功（7件skip）、Notebook JSON/Python構文と`git diff --check`成功。実データでの精度評価とCPU・他環境の実行は未確認。

## 今回の作業単位：DETR・SAM Colab検証前のHub依存競合を解消

対象仕様：4.3、5.1、5.2、7。OCR動作確認後の次の実環境検証として、Colab T4でDETR・SAMの取得と推論を行う。事前確認で`vision` extraもHugging Face Hubを`<1`に制限しており、Colab既存のTransformersが要求するHub 1.xをダウングレードする可能性を確認した。

順序：
1. `vision` extraのHub上限を`<3`へ変更し、`ocr`・`diffusion`と同じくHub 1.xを許容する。
2. 依存メタデータのテストとインストール案内を更新する。
3. Colab Notebookのコードを今回の固定commitに更新し、JSON・コードセル構文・依存指定を検査する。
4. Python 3.13ネットワーク不要テストを実行し、ブランチへ反映する。
5. 利用者がT4 Notebookを実行した結果を受け、DETR、SAM、GPU連携の実測状況を記録する。

受け入れ条件：`vision` extraがHub 1.xを不必要に下げず、固定revisionのモデルを明示読込するColab T4確認Notebookが更新される。モデル実取得とGPU推論はColab結果を得た範囲だけを検証済みとする。

進捗：Colab Notebookを点検し、`vision` extraのHub `<1`がColabのTransformersと競合し得ることを特定。Hub `<3`へ変更し、依存メタデータテストと利用案内を更新。Python 3.13で全69テスト成功（7件skip）、Notebook JSON・Pythonセル構文・`git diff --check`も成功。Notebookを固定commit `6af0bfbe2cd1b5e75cd59d407135a0f9c4355008`に更新。Colab T4でのDETR/SAM実機テストは未実施。

## 今回の作業単位：OCR extraのColab依存競合と誤案内を修正

対象仕様：4.2、5.1、5.2。ColabログでPaddleOCR 3.1.0がPaddleX 3.1.4とともにLangChain 1.x系を解決し、PaddleXの旧`langchain.docstore`参照でOCR importが失敗することを確認。また、OCR extraの`huggingface_hub<1`がColab既存のTransformers/Diffusersと競合し、依存不整合を報告している。

順序：
1. `ocr` extraでPaddleOCR 3.1系が要求するLangChainを1.0未満に制約し、既存のLangChain API依存との不整合を防ぐ。
2. OCR用Hugging Face Hub上限を他のモデル機能と揃え、Colab既存パッケージのHub 1.xを不要にダウングレードしない。
3. PaddleOCR本体の欠落と、内部依存のimport失敗を区別して、原因に合う`OCRError`を返す。
4. OCR導入文書・Colab Notebookに、既存ランタイムでの対処と再起動手順を反映する。
5. 依存メタデータ、遅延import、エラー表示、Notebook構文のネットワーク不要テストを実行する。

受け入れ条件：`langchain.docstore`を含む内部`ModuleNotFoundError`を「paddleocr未導入」と誤表示しない。`ocr` extraの依存指定が互換LangChainとHugging Face Hub 1.xを許容する。Colab利用者が依存の再導入・ランタイム再起動を行う方法が明記される。

進捗：貼付ログから、PaddleOCR 3.1.0がPaddleX 3.1.4経由でLangChain 1.xを導入し、PaddleX内の旧`langchain.docstore`参照で失敗すること、およびHub 0.xへのダウングレード・Requests 2.34への更新がColab既存依存と競合することを確認。`ocr` extraにLangChain `<1`、Hub `<3`、Requests `<2.33`の制約を設定。OCR未導入と内部依存エラーを別の案内にし、OCR導入文書とNotebookを更新。Python 3.13で全69テスト成功（7件skip）、`git diff --check`成功。ユーザーがColab CPUで実行し、`TOTAL 1280 JPY`を1行、信頼度0.993、四点座標付きで返すことを確認。合成した英数字画像でのsmoke test完了。日本語実画像の認識品質、GPU、他OSでの実機確認は未実施。

## 今回の作業単位：ColabのOCR smoke testで古いcvlessonを検出・更新

対象仕様：4.2、5.1、7。ユーザーのColab出力に旧版OCRコードが現れ、既定名`PP-OCRv5_server_det`とローカルのmobileモデルの不一致を確認した。新しい固定コードを確実に使い、古いimport済みモジュールを見分けられるようにする。

順序：
1. 固定commit `9da8f480bf6bdc9c834a5fe92f371939ad45214b`の`ocr.py`がモデル名を明示し、`lang`/`ocr_version`を渡さないことを確認する。
2. Notebookの依存インストール後に、依存を変えずライブラリ本体だけを固定commitから再インストールする手順を加える。
3. 既にimport済みの古いソースを検出し、Colabランタイムの再作成・Notebook再読込を促すチェックを追加する。
4. Notebook構文とネットワーク不要テストを確認し、PR #63を更新する。

受け入れ条件：OCR smoke testは互換修正commitのコードを使い、旧コードがロードされていたらモデル取得前に原因と復旧方法を示す。HF_TOKENは公開モデル利用に必須ではない旨を注記する。

進捗：Colabログの`lang`/`ocr_version`警告とserver/mobileのモデル名不一致から旧`cvlesson.ocr`が動いていることを特定。HF_TOKEN警告は別件で、公開モデル利用にはtoken不要。Notebookで依存導入後にライブラリ本体を固定commitからforce-reinstallし、ロードソースにmobileモデル名がない場合はランタイム再作成を促す検査を追加。HF_TOKEN警告の説明も記載。Python 3.11〜3.13で各67テスト成功（各7件skip）、Notebook JSON/コードセル構文と`git diff --check`成功。Colab再実行はこれから。

## 今回の作業単位：データ・モデルの使用例を非限定表現へ統一

## 今回の作業単位：OCR依存の互換性修正と機能別導入

対象仕様：0.9、4.2、5.1、5.2。Colabで発生した`PaddlePredictorOption`初期化エラーを修正し、OCRの依存はOCR機能を選んだ時だけ導入・importされる形を保つ。

順序：
1. PaddleOCR 3.1系とPaddleXの公式互換範囲を確認し、仕様書へ依存系列、PaddlePaddleの環境別導入、遅延import、自動pip installをしない方針を記録する。
2. 開発計画へ、依存pin・PaddleOCR初期化引数・Notebookの導入説明・テストの作業と受け入れ条件を記録する。
3. `ocr` extraにPaddleX 3.1互換範囲を追加する。PaddlePaddle本体はCPU/GPU・OSに応じて別途導入する仕様を維持する。
4. OCR既定モデル名を明示し、モデル名/ディレクトリ指定と同時に無視される`lang`・`ocr_version`引数をPaddleOCRへ渡さない。Colab Notebookから利用者向けに不要な`import paddle`を除く。
5. 日本語の導入案内、互換制約、欠落依存時の案内を整合させ、ネットワーク不要テスト・wheel・Notebook構文を確認する。

受け入れ条件：PaddleOCR 3.1系とPaddleX 3.1系が依存解決で選ばれ、Colabで報告された互換性不一致を避けられる。コアimportとOCR以外の機能はPaddle系を読み込まず、`ocr.load()`が必要な依存だけ遅延importする。利用者が`import paddle`を個別に書かずに使える。CPU/GPU用PaddlePaddleは対応環境に合う導入コマンドを明示し、ライブラリが実行中にpip installしない。

進捗：一次情報を確認。PaddleOCR 3.1.xはPaddleX 3.1系と組み合わせる必要があり、3.2系APIを読み込むと今回の例外が起こる。仕様0.9と本計画を先に更新。`ocr` extraにPaddleX互換範囲を指定し、PaddleOCRへ固定モデル名を渡して`lang`/`ocr_version`の無視警告を除去。OCR Notebookの直接`import paddle`を外し、導入・遅延読み込みの説明を更新。Python 3.11〜3.13で各67テスト成功（各7件skip）、Notebook JSON/コードセル構文、`git diff --check`成功。Colab実環境での再確認は未実施。

## 前回の作業単位：データ・モデルの使用例を非限定表現へ統一

対象仕様：0.8、3.1、4.4、6、7。データとモデルの能力・内容・形式を主に説明し、課題での使用例は候補例として示す。ライセンス条件、データの構成上の制約、モデルの技術的限界は明確に残す。

順序：
1. 仕様書へ使用例を用途制限と誤読させない要件を追記する。
2. 生徒向けデータカタログ、LoRAカタログ、モデル説明、README、ガイド、Notebookの説明文を横断確認する。
3. 固定的な「この課題に使う」説明を「できること」と「使用例」に分ける。実際の権利条件・技術的限界は削らない。
4. 文字列検索とドキュメント差分確認を行い、用途例が唯一の使い道のように読める記述を残さない。

受け入れ条件：データ・モデルごとに能力・内容が分かり、使用例は複数の題材に応用できる例として読める。法的な利用条件や、モデル・ラベル・形式が実際に持つ限界は正確に維持される。

進捗：仕様0.8へ改訂し、生徒向け22データのAPI説明、個別データ説明、LoRAカタログ、README、画像生成ガイド、AI改造ガイド、Colab生成Notebookを更新。能力・内容と使用例を分け、例が用途を限定しない旨を明記した。権利条件・技術上の制約は維持しつつ、素材カテゴリしか持たないデータに不要な用途制限があった記述を修正。旧`use_case_ja`参照がないこと、Notebook JSON、`git diff --check`を確認。ネットワーク不要テストはPython 3.11・3.12・3.13で各67件成功（各7件skip）。Python 3.9は仕様対象外のため実行対象外。



## 2026-11-09 方針更新：データ優先

ユーザーの最新指示（2026-11-13）により、学習済みLoRAの目標を8件から4件へ変更した。追加候補の課題適性とモデルライセンスをダウンロード前に確認し、条件を満たす2件を固定revision・SHA-256付きで登録済み。学習元データの説明状況も分けて表示し、数合わせの候補追加は行わない。次はColabの実モデル確認へ進む。

次の優先順は、(1)既に共通artifactがあり、権利・内容確認を終えればRelease/APIに進める候補、(2)既存source manifestと部分監査がある候補、(3)新規候補の一次情報確認とする。候補ごとの現状と残作業は[データ優先候補の確認表](data-first-shortlist-2026-11-09.md)に記録する。公開済み件数と準備済み件数は別々に数え、準備済みを利用可能とは表示しない。

## 圧縮スコープと完了見込み

ユーザーの方針に合わせ、候補50件をすべて公開対象として調べ切る計画をやめる。目標は、既存のトマトに加えてデータセット20件（最低15件）、文化祭アイコンの学習素材とは別に学習済みLoRA重み4件とする。重みは再配布用に保管せず、固定した元配布元から利用者が取得する。選定後は残り候補を保留・未選定として残し、追加の全量取得や重複監査を行わない。

- 共通API、課題から選ぶ導線、外部キャッシュ、安全な固定版取得、監査形式は維持する。件数を減らすためにデータ形式別アダプタや出典・利用条件の表示を省かない。
- 最低15件、目標20件のデータセットは分類だけに偏らないよう選び、検出・領域分割を含める。既存監査・manifest・整形artifactを再利用し、新規の実体検査は選定候補に限る。
- 学習済みLoRA重みは、元配布元の固定版・固定URL・SHA-256・利用条件・基盤モデル互換性・トリガー語を登録し、利用者が明示した時だけcheckout外のキャッシュへ直接取得する。重みをPyPI・Git・CV_data_artifactsへ複製・再配布しない。
- 「完了」は、選定数を機械可読カタログに登録し、各データの権利・固定取得・内容確認・日本語説明と、各LoRA重みの固定取得・ライセンス・互換情報が揃い、ネットワーク不要テストとパッケージ確認を通した状態とする。条件未確認の項目は承認済み一覧に出さない。
- **技術作業は今日〜明日でPyPI公開候補まで仕上げることを目標にする。** 既に監査・整形済みの候補を優先すればコード・文書の残作業はおおむね1〜2日。第三者の権利者確認が必要な項目は返答時期を制御できないため、20件・4件すべての公開承認まで同じ期限で約束はできない。未解決分を承認済みと見せず、権利の通った範囲で公開候補を完成させる。
- PyPI本番公開とデータReleaseは、既存ルールに従い明示的な公開許可後に行う。

## 1. 今回の方針

`notebooks/reference/CV_10-12_v3.ipynb`はLLM講座の教材であり、CV教材の基準Notebookではない。内容・構成を変更せず、形式上の参考資料として扱う。

データ本体は開発リポジトリへ置かず、利用時に必要なものだけをリモートから取得する。再配布が認められた整形済みデータは`CV_data_artifacts`の固定タグ付きGitHub Release assetで管理し、出典・ライセンス・source manifest・artifact manifest・監査記録だけをGitで管理する。LoRA学習素材（画像・キャプション）と学習済みLoRA重みを別管理し、重みは利用者が明示的に呼び出した時に限り、固定した元配布元から取得する。重みはミラー・再配布しない。

候補調査は、次の短いゲートで進める。

1. 公式一次情報から、固定版・取得条件・ライセンス・想定課題をまとめて確認する。
2. 固定版や利用条件が不明、または課題価値が低い候補は、理由を台帳に記録してダウンロード前に保留する。
3. 続行候補はsource manifestを一度作り、ファイルID・サイズ・SHA-256を以降の検査で再利用する。
4. 実体検査は目的に合わせて「メタデータ」「代表サンプル」「全量」の範囲を先に決め、実測範囲を明記する。
5. 権利・ラベル・プライバシーの条件を通過した候補だけを共通形式へ変換する。
6. 固定Release assetとSHA-256が整った後で、取得API・課題一覧へ登録する。
7. 生徒向けNotebookは、正式一覧から実際に取得できるデータが揃ってから作る。

候補ごとに1ブランチ・1PRとし、独立した一次情報の確認は並行できる。大容量取得、同じsource manifestの再生成、既に済んだ監査の再実行は避ける。ライセンス審査を省略して速度を上げない。

技術的に取得できることだけでは、教材で使えるとは判定しない。

## 2. 2026-11-12時点のスナップショット

- 生徒向けAPIは19件です。課題接続が弱い7件を取り下げ、追加候補3件（家庭ごみ素材分類、食品包装OCR、電力量計数字OCR）のデータ監査・整形を完了しました。固定Release assetを公開し、APIを有効化しました。追加後は22件です。Obstacles Avoidance AssistanceはMendeley v1のCC BY 4.0表示と画像・bbox対応を確認し、歩道上の物体候補を人が確かめる地図の試作向けに整備しました。配布元説明は公開Roboflow画像を選定したとしていますが、個別上流ID・ライセンスは列挙していません。元JPEGとbboxは変更せず、1,250枚・1,627件です。実際の移動やアクセシビリティをモデルに判断させません。教師向けLoRA素材は`festival_icons`1件、承認済みLoRA重みは0件です。
- ChakmaLipī v6は権利確認・全量デコードと共通形式化、固定Release公開を完了しましたが、身近な課題との接続が弱いため今回、生徒向けAPIから取り下げました。成果物・監査記録は保持します。
- `tomato_leaves`：7,209枚、破損0、完全一致重複0、ラベル不一致0。標準化後はtrain 5,191 / val 577 / test 1,441。
- `festival_icons`：168枚、破損0、キャプション欠損0、完全一致重複0。分類データではなくLoRA学習素材として管理。承認済み学習済みLoRA重みは0件。
- 候補台帳は64件。取り下げ後は`candidate` 31件、`hold` 17件、`student_enabled` 16件です。生徒向けAPIは19件で、そのうち3件は候補台帳外の個別審査データです。
- `CV_data_artifacts` mainにはsource manifest 17件、artifact registry掲載11件があります。FabricSpotDefect、BDRoadSigns、Orange Fruitのsource manifest・registry登録を追加しました。PUSTのRelease assetは存在しますが、artifact registryへの登録が見当たらず、別途台帳を整合させます。
- 候補台帳の全項目を一括で`list_available()`へ加えません。選定・権利確認・固定Releaseが済んだデータだけを個別に公開します。
- 既存Notebook、`CV_sample_data`、そのRelease、タグ、配布ファイルは変更しない。
- データ本体は`CV_data`、`CV_data_artifacts`のGit履歴、PyPIへ収録しない。GitHub Release assetまたは、権利上ミラーしない大容量原本の固定された公式配布元を利用する。実際のRelease公開は許諾と明示承認後に限る。

## 2.1 現在地（2026-11-13）

- 生徒向けデータAPIは22件です。通常一覧には教師向け`festival_icons`を含めず、教師向けを含む全体では23件です。候補数と実際に取得可能な数を混同しません。
- `models`にResNet18の分類・回帰、`generation`にSDXLのtext-to-image / image-to-image、`ocr`にPP-OCRv5 mobile日本語OCR、`vision`にDETR検出とSAMプロンプト式領域分割の推論APIを実装しました。学習・追加学習の対象範囲は仕様書に記載しています。
- 学習済みLoRAは4件を固定revision・SHA-256付きで登録し、SDXL生成で明示取得・適用できます。LoRAの実モデル推論は未確認です。
- Python 3.11〜3.13でネットワーク不要テスト67件が成功（各7件skip）。wheelを構築して一時targetへインストールし、軽量importとモデル・画像バイナリ非同梱を確認。GitHub Actionsはvision API追加の`56bd58f`とSAM互換修正の`a7bc2c5`で成功しました。
- PaddleOCR、DETR、SAMの固定モデル実取得・CPU/GPU推論、Colab T4での実環境確認は未実施です。これらは該当環境で確認するまで「実装済み」と「実環境検証済み」を分けて扱います。
- Colab向けのDETR/SAM T4 Notebook、OCR CPU Notebook、SDXL＋4 LoRAの画像生成Notebookを作成しました。Colabでの実行は未確認です。
- 作業ブランチとレビュー提案：[PR #63](https://github.com/708san/CV_data/pull/63)。mainへは直接マージしていません。

## 3. データ保管と取得の運用

- Gitにはコード・テキストmanifest・ライセンス記録・監査reportのみを置く。Git LFSもデータ保管先には使わない。
- `CV_data_artifacts`のRelease assetは、再配布条件が確認でき、整形済み配布物をこちらで保つ必要があるデータに限る。source manifestの存在は画像の再配布許諾を意味しない。
- 大きく未加工のLoRA画像素材は、ライセンス条件に従い固定版の公式配布元を直接参照する。取得時にサイズとSHA-256を検証できる場合は必ず固定する。取得条件が固定できないものは正式APIへ登録しない。
- `cvlesson`は利用者がデータ取得APIを呼んだ時だけダウンロードする。既定キャッシュは`XDG_CACHE_HOME`または`~/.cache`配下に置き、リポジトリcheckoutと分離する。カタログ表示・import・通常テストでは取得しない。
- 整形作業は一時領域で行い、元ファイルを変更しない。成果物のZIP・展開後サイズ・SHA-256・manifestを確認したら、Git管理領域へコピーしない。Release assetの作成・移行は権利確認とユーザーの明示許可後に行う。
- `datasets.cache_info()`と`datasets.clear_cache()`で、既定キャッシュの容量確認と登録済みデータの削除・再取得を利用できる。容量の見積もりは取得前に示す。

## 4. 候補精査の段階

### Phase A：候補台帳と証拠の整理

対象：`registry/candidates_50_unreviewed.json`

- 各候補に、正式名称、提供者、固定バージョン、公式配布URL、アーカイブSHA-256、形式、件数を記録する。
- ライセンス表記のURLと、元画像の権利・収集元・個別条件を分けて記録する。
- `rights_status`、`technical_status`、`publication_status`を混同しない状態遷移にする。
- 取得可能だが権利不明の候補は、技術検査だけ行い、教材提供は保留する。
- 50件の候補情報を「調査済み」と「承認済み」に読み替えない。

受入条件：候補ごとに、次に確認すべき証拠と保留理由が機械可読になっていること。

### Phase B：優先候補の権利・実体調査

次の調査順は固定リストにせず、台帳に残る未解決事項を基に選ぶ。優先度は、(1)ライセンス・元画像権利が確認可能、(2)固定版と取得条件がある、(3)高校生が扱える問いにできる、(4)既存形式アダプタで使える、の順に評価する。確認済み候補の再監査は、情報更新や保留理由を解消する具体的な根拠がある場合だけ行う。

各候補で次を確認する。

- 公式ページと固定版の一致
- ライセンス本文、出典表示、改変、商用利用、再配布条件
- 元画像の作成者・収集元・第三者データの混在
- 個人情報・不適切画像・医療的誤解・文化的配慮のリスク
- 教材での取得方式、キャッシュ方式、外部配布の可否
- 実データの全量または明示した範囲の検査結果

受入条件：権利状態が`approved_for_classroom`またはそれに相当する明示的な判定にならない候補は、正式提供一覧へ追加しない。

効率化のため、Phase Bは全候補の全量取得から始めない。一次情報と授業価値で短い候補リストを作り、ライセンス・取得の固定条件で足切りした後に、必要な範囲だけ実体を取得する。権利が解決しない場合は変換用の大容量ダウンロードを行わず、source manifestと机上調査で終える。

### Phase C：データ形式別の共通基盤

データ形式を一つに押し込めず、タスクごとに共通APIを作る。

#### 画像分類

- フォルダ分類、CSVラベル、IDXなどを共通の分類アダプタへ変換する。
- `image_path`、`label`、`label_ja`、`label_id`、`split`、`sample_id`、`group_id`を標準列にする。
- 公式testを保持し、公式valがなければtrainだけを再現可能に分割する。
- `to_df()`と`to_torch_dataset()`で同じ標準化済みレコードを使う。

#### 物体検出

- YOLO、COCO、Pascal VOCを、画像ID・ラベル・座標・画像サイズの共通表現へ変換する。
- 座標の原点、単位、画像サイズ、境界外座標を明示する。
- 変換前後の件数・座標・画像対応を検査する。

#### 領域分割

- 元画像とマスクの対応、クラスID、背景、画像サイズを検査する。
- パレット値やマスクの欠損を推測で補わない。

#### LoRA学習素材

- 画像とキャプションを管理し、分類ラベルへ変換しない。
- 基盤モデル、トリガーワード、推奨設定、ライセンス、再配布条件を別管理する。
- `festival_icons`は学習素材。権利条件が確定するまで、取得・検査可能でも教材配布承認済みにはしない。

#### 学習済みLoRA重み

- 学習素材の画像APIと別のカタログ・取得APIにする。
- 公式または作者が指定した固定配布元から取得し、モデルID、版、基盤モデル、SHA-256、利用条件、トリガー語、取得サイズを表示する。
- 明示的な`get`呼び出しでのみ取得し、外部キャッシュへ保存する。重みをPyPI、Git、`CV_data_artifacts`へ入れない。
- 取得・利用条件が許諾されているモデルだけを学生向け一覧に載せる。

受入条件：同じタスク内で、候補ごとの元形式を利用者が意識せず共通操作できること。ただし、未承認候補はAPIに公開しない。

### Phase D：取得・キャッシュ・品質保証

- 固定URL、固定版、既知SHA-256を必須にする。
- SHA-256検証前の展開を禁止する。
- ZIPパス逸脱、シンボリックリンク、展開サイズ超過を拒否する。
- 元データと標準化済みキャッシュを分離し、キャッシュはリポジトリ外に置く。
- Release assetまたは固定公式URLから、利用者が明示取得したデータだけを保存する。カタログ参照ではネットワークアクセスしない。
- 不完全ダウンロード、再試行、オフライン時のエラーを検査する。
- 画像破損、完全一致重複、類似画像候補、ラベル不一致、分割間重複をレポートする。
- 類似画像候補はレビュー用に記録し、自動削除・自動ラベル変更をしない。
- 同一個体・撮影系列・原画像のグループ情報がない場合は、漏洩防止を保証しない。

品質レポートには、画像数、使用可能数、クラス数、分割数、破損数、重複候補、除外理由、分割方法、seed、漏洩リスク、検証日時を含める。

### Phase E：課題選択用のデータ・LoRAライブラリ

Notebookを先にデータごとに固定せず、生徒が課題に合う素材を選べる情報と操作を先に完成させる。

#### データカタログ

- タスク、入力、出力、画像の内容、クラス数、サイズ、推奨環境、学習時間の目安を表示する。
- `student_enabled`、`teacher_preview`、`hold`を一覧上で区別する。
- 課題の種類から候補を絞れるようにするが、曖昧な推測でデータを選ばない。
- 実画像のサンプル、ラベル、日本語説明、出典、ライセンス、制約を同じ画面で確認できるようにする。
- 取得前に権利状態とダウンロードサイズを表示する。

想定API：

```python
from cvlesson import datasets

datasets.list_available(task="classification", audience="student")
datasets.get("トマトの葉")
data.show_examples(9)
data.to_df()
data.to_torch_dataset(split="train", image_size=(64, 64))
```

#### LoRAカタログ

画像分類データとLoRA素材を同じ分類ラベルへ変換しない。LoRAは専用の管理APIを用意する。

```python
from cvlesson import loras

loras.list_available(audience="student")
loras.info("festival_icon_style")
loras.get("festival_icon_style")
```

LoRAごとに、画像・キャプション・トリガーワード・基盤モデル互換性・推奨設定・ライセンス・再配布可否・GPU検証状態を管理する。モデル重みは無断再配布しない。

受入条件：生徒が「分類」「検出」「領域分割」「画像生成・LoRA」のどれを作りたいか選ぶと、利用可能な候補と課題上の制約を確認できること。未承認素材は生徒向け一覧に出さないこと。

### Phase F：CV教材Notebookの新設

LLM講座のNotebookを改修せず、CV用に別ディレクトリと別ファイル名で作成する。referenceの「タイプを選ぶ」「準備」「見本」「自分の課題」「テスト」「開発ログ」「振り返り」という流れをより忠実に参考にし、内容だけを画像・データ・LoRAの課題へ置き換える。

候補構成：

- `notebooks/cv/classification_v1.ipynb`
- `notebooks/cv/detection_v1.ipynb`
- `notebooks/cv/segmentation_v1.ipynb`
- `notebooks/cv/lora_materials_v1.ipynb`（権利承認後のみ）

各Notebookの条件：

- 生徒が最初に「画像を分類する」「画像の中の位置を調べる」「画像の範囲を分ける」「画像生成の絵柄を揃える」などの課題タイプを選べる。
- 課題タイプを選ぶと、利用可能なデータ・LoRAをカタログから選べる。
- 生徒が最初にデータの出典・利用条件・制約を確認できる。
- 実際の画像例とキャプションを確認してから、入力・期待する出力を書く。
- `cvlesson`の実装済みAPIだけを使う。
- データ取得、内容確認、学習または推論、評価、結果の記録を行う。
- 画像分類・検出・分割・LoRA素材を用途混同しない。
- Level 1相当の説明にとどめ、発展機能を持ち込まない。
- 生徒の課題を過度に決めつけず、記入欄と検証手順を用意する。
- 無料Google ColabのCPUを基本とし、GPUが必要な場合は明示する。

受入条件：Notebook単体で、承認済みデータの取得から課題に対応する最小の実行・評価まで再現でき、未実装APIや未承認データを使用可能と書いていないこと。

### Phase G：テスト・公開準備

- 通常テストはネットワーク不要で実行する。
- 実データ全量監査、GPU検証、大容量取得は手動または限定テストへ分離する。
- Python 3.10以降でパッケージビルドを確認する。
- README、データ別説明、AI改造ガイド、NotebookのAPI使用例を一致させる。
- PyPI本番公開、データ用GitHub Release作成、配布先変更、mainへのマージは明示許可まで行わない。

## 5. 段階的な完成目標

### M1：データ・LoRA選択基盤（基盤実装済み）

- 既存のトマトの葉で共通分類APIを安定化する。
- 課題接続が弱いデータを生徒向けAPIから取り下げる。Kuzushiji-MNISTは固定配布物とSHA-256が確定するまで保留する。
- LoRA素材のメタデータ管理APIを作り、権利未確認の素材を生徒向け一覧から除外する。
- 課題タイプから候補を選べるカタログ表示を実装する。

### M2：分類データとLoRAの教材基盤（データ公開条件の解決待ち）

- 権利・実体・品質レポートが揃った分類データを1〜2件追加する。
- 承認済みのLoRA素材がある場合、画像・キャプション・利用例を追加する。
- reference形式のCV分類・画像生成Notebookを作成する。
- クラス不均衡、公式split、グループ漏洩の制約を教材に明記する。

### M3：検出・分割（API・オフライン検証済み、実モデル環境の確認待ち）

- DETR ResNet-50でCOCO 80カテゴリの物体検出推論を提供する。
- SAM ViT-Bで点・矩形入力によるプロンプト式マスク推論を提供し、DETRの枠を渡す連携を用意する。
- 座標・マスクの変換テストを行う。意味領域分割とインスタンス用のプロンプトマスクを混同しない。

### M4：学習済みLoRA重み（4件を登録・固定取得済み、4件目標）

- `fluent_emoji_3d`と`watercolor_sdxl`を登録し、固定revision・SHA-256・利用条件・SDXL互換性を管理する。
- `pixel_art_sdxl`と`thomas_cole_landscape`を追加し、固定revision・Hub公開SHA-256・利用条件・学習元データの記載状況・高校生向け用途を管理する。
- `generation.load()`の明示利用時に配布元から取得し、ハッシュ照合後に適用する。重みはGit/PyPI/CV_data_artifactsへ複製しない。
- 目標4件を登録済み。Hubの固定revision metadataにあるファイルSHA-256を登録し、ライブラリは取得後にSHA-256を検証する。

## 6. 次に実施する課題

### 2026-11-13 LoRAカタログを4件目標に整える

対象仕様：4.4、5.1、5.2、7。登録済み2件の方針を維持し、あと最大2件を目標に一次情報で生徒の課題適性とモデルライセンスを確認する。LoRAの重みと学習データの権利情報は分けて記録する。

順序：
1. SDXL対応候補の公式モデルカードで、用途・ライセンス・固定revision・配布ファイルを確認する。
2. 高校生の身近な困りごとに使える具体的用途を定め、既存2件との用途重複も見る。
3. ライセンス表記、モデルカード、学習元データの記載状況を確認し、不明点を正確に注記する。ライセンスの明示がない候補は採用しない。
4. 条件を満たす候補のみ、完全なrevisionと実ファイルSHA-256を取得・検証して登録する。重みはリポジトリやReleaseへ保存しない。
5. カタログ、使い方、権利・用途説明、ネットワーク不要テストを更新し、Colab実行手順へ進む。

受け入れ条件：採用した各モデルに用途・出典・ライセンス表示・revision・SHA-256・基盤モデル互換性・学習元データの確認状態がある。最大4件とし、条件を満たす候補が不足する場合は実数を明記する。

進捗：4件目標を達成。pixel-artとThomas Cole風の2件を固定revision・Hub公開SHA-256で登録しました。ライセンスと用途を確認し、モデル重みは取得・再配布していません。Python 3.11〜3.13で67テスト成功（各7件skip）、差分の空白検査も成功しました。実モデル取得・生成は未検証です。

### 2026-11-13 Colab実モデル確認Notebook（今回の作業単位）

対象仕様：4.2、4.3、4.4、5.1、5.2、7。仕様0.7に従い、利用者がColabで推論を試せるNotebookを3本用意する。PyTorch/TransformersのDETR・SAM検証、別ランタイムのPaddleOCR検証、SDXLと登録済みLoRA検証を分離する。画像生成の試験にはNotebook内で作る合成風景を使い、利用者の写真送信やデータartifact取得を要求しない。LoRA一覧のライセンスと学習データの注記をモデル取得前に表示する。

順序：
1. SAMの現行Transformers公式手順と照合し、マスク後処理に`original_sizes`と`reshaped_input_sizes`の両方を渡すようAPIとfake backendテストを修正する。
2. そのコードをPRへpushし、CI成功を確認する。その固定commit SHAをNotebookのインストール元に記録する。
3. `notebooks/colab/vision_smoke_test.ipynb`を作成する。T4確認、固定commitの`vision` extra導入、合成画像でのDETR/SAM推論、結果型・マスク形状・GPU利用を表示する。
4. `notebooks/colab/ocr_smoke_test.ipynb`を別に作成する。CPUランタイム、PaddlePaddle公式導入、固定commitの`ocr` extra、合成テキスト画像の推論結果を確認する。
5. `notebooks/colab/generation_smoke_test.ipynb`を作成する。T4確認、固定commitの`diffusion` extra導入、SDXL＋登録済み4 LoRAのtext-to-image / image-to-image推論を行う。入力画像はNotebook内のPillow図形で合成し、LoRAは1件ずつ読み込んでGPUメモリを解放する。
6. Notebook JSON、コードセル構文、Markdown/リンク、固定SHA、公開可能な出力未格納をローカルで確認する。Colab実行前のNotebookを実環境検証済みと記載しない。
7. README、インストール手順、画像生成ガイド、進捗、PR本文を更新し、ユーザーが実行するセル順と成功条件を案内する。

受け入れ条件：3 NotebookがColabで開ける有効な`.ipynb`で、パッケージコード取得は完全な固定commit SHAを使う。画像生成Notebookにはブランチ上の直接起動リンクと簡潔な実行手順があり、4件すべて成功しない場合は失敗を明示する。GPU NotebookはT4がない場合にその旨を明確に表示して終了し、OCR Notebookは別ランタイムを案内する。テスト画像はNotebook内で生成し、モデル・データのバイナリや実行結果をリポジトリへ同梱しない。LoRAの権利と学習データの確認状態を重み取得前に表示し、各推論結果と環境情報を利用者が判定できる。

進捗：DETR/SAM用のT4 Notebook、OCR用のCPU Notebook、LoRAを含むSDXL生成Notebookを作成しました。Notebook JSON・Pythonセル構文・未実行出力を確認済みです。Colabでモデルを実行する前の状態を明記し、実環境の取得・生成は未確認です。

### 2026-11-13 OCRバックエンド実装（この作業単位）

対象仕様：4.2 OCR、5.1 依存関係、5.2 バックエンド連携。日本語PP-OCRv5 mobileのCPU推論APIを追加し、固定revisionからの明示取得、共通結果型、GPU事前確認、任意依存の案内を実装する。

順序：
1. 仕様書へOCRモデル・固定revision・出力・依存境界を記録する（完了）。
2. OCR moduleと遅延import、モデル取得・CPU/GPU指定、入出力変換を実装する。
3. モデル実取得なしのfake backend単体テストとoptional importテストを追加する。
4. READMEと導入説明を更新し、OCR用のPaddlePaddle公式導入分岐と実環境未検証範囲を明記する。
5. 標準ライブラリの全テスト、wheel構築、diff/パッケージメタデータ確認を行う。

進捗：OCR API、固定revision取得、共通結果型、CPU既定/GPU事前確認、インストール・生徒向け説明、mock単体テストを実装しました。Python 3.11/3.12/3.13で全58テスト成功（各7件は未導入の任意依存によるskip）。クリーンwheelを構築し、一時targetへインストールして、データ一覧・軽量import・画像等のバイナリ非同梱を確認しました。モデル実取得、Paddle CPU/GPU推論、Colab T4は未検証です。

受け入れ条件：`import cvlesson`はOCR・Paddle・Hugging Faceを読み込まない。`ocr.load()`はCPU既定で固定モデルを指定し、GPU未対応を推論前に明確に拒否する。`reader.predict()`は文字、信頼度、四点座標を共通型で返す。モデル取得・GPU・実OCR精度は通常テストで実行せず、別途実環境検証待ちとして記録する。

### 2026-11-13 検出・領域分割の推論API（コード実装・オフライン確認済み、実モデル確認待ち）

対象仕様：4.3、5.1、5.2、7。仕様0.6で採用モデル、固定revision、ライセンス表記、サイズ、タスク範囲、利用者指定モデルの固定revision条件を先に確定した。DETRはApache-2.0表示・約167 MB、SAMはTransformersが選ぶsafetensors重み約375 MB（Hub上の全ファイル表示は約1.13 GB）。DETRはCOCO 80カテゴリの閉集合検出、SAMはラベルなしの点/矩形プロンプトマスクであり、意味領域分割モデルではない。

順序：
1. 仕様へモデルと入出力契約を追加（完了）。
2. `vision` extraと遅延importの推論APIを実装する。CPUを既定にし、GPUは明示指定と事前検査を行う。
3. DETRのラベル・信頼度・画像座標xyxy、SAMの二値マスク・品質スコアを共通型へ正規化する。DETR枠からSAMを呼ぶ補助APIを実装する。別モデル指定はrepository IDと完全な40桁revisionを必須にする。
4. ダウンロードを伴わないfake backendテストを追加し、任意依存の遅延読み込みと不正な座標・装置指定を確認する。
5. 日本語README、インストール手順、AI改造ガイドとvision専用ガイドを更新し、各モデルの固定版・権利・容量・限界を明記する。
6. ネットワーク不要テスト、wheel、クリーン環境importを確認して進捗を記録する。実モデルCPU/GPU推論とColab T4は未確認として区別する。

受け入れ条件：`import cvlesson`でtorch/transformers/huggingface_hubを読み込まない。モデル読み込みを明示した時だけ固定revisionの重みを取得する。CPUが既定で、指定GPUの利用不可は重み取得前にエラーにする。既定モデル以外はrepository IDと完全な40桁revisionを必須にし、浮動参照を拒否する。検出結果はCOCO英語ラベル・0〜1スコア・元画像座標のxyxyを返す。SAM結果は元画像寸法の二値マスクとスコアを返し、検出との連携でラベルをSAMの意味ラベルのように扱わない。実際のモデル出力とColab T4は別途検証待ちとする。

進捗：`vision` API、固定revision、利用者指定モデル、遅延依存、CPU既定/GPU明示選択、座標入力検証、結果型、検出枠からSAMへの連携、初心者向け説明を実装しました。SAMの最新Transformers手順に合わせて、マスク後処理へ原画像サイズ・変換後サイズを渡します。Python 3.11/3.12/3.13で全66テスト成功（各7件skip）。Python 3.11でwheelを構築・一時領域へインストールし、基本importがtorch/Transformers/Hub/NumPy/Pillowを読み込まず、wheelにモデル・画像バイナリがないことを確認しました。Colab用Notebook 2本を作り、JSONとコードセル構文を確認しました。実モデル取得・推論とColab T4は未確認です。

### OCR以降の残作業

1. [データ優先候補の確認表](data-first-shortlist-2026-11-09.md)に挙げた既存準備物の権利・内容上の残件を解消する。まず再処理不要の候補を選び、根拠に食い違いがある場合は台帳・レポートを揃えてから進める。
2. Release assetがない準備済みデータは、元ZIPと成果物の固定SHA-256、manifest、帰属表示、変更説明を照合し、権利上の保留が解消した後にのみRelease/APIへ進める。
3. 既存監査済み候補を追加した後、一次情報で固定版・ライセンス・内容の見込みを短く確認し、最低15件、目標20件に向けて追加する。残り候補は無差別に全量取得せず、優先順位を付ける。
4. LoRAは目標4件の固定取得APIを実装済み。実モデル取得・生成はColabで確認する。
5. 生徒向けAPIは22件になりました。追加データのライセンス・固定取得・用途説明を整えたため、データ選定を完了とする。その後、全API・README・データ別説明・AI改造ガイドを揃えてPyPI公開候補を仕上げる。PyPI本番公開とデータReleaseは明示許可の境界に従う。

技術的に取得できることだけでは教材公開の承認とみなさず、準備済み・権利確認済み・公開済みを別に記録する。

### 2026-11-11 追加審査：Road Traversing Knowledge

- CC BY 4.0の固定v1、配布ZIPサイズ・SHA-256を公式Mendeley APIで確認。全1,402 PNGをデコードし、701画像・701マスクの352×288同名対応、train 561 / validation 140の公式分割を確認しました。
- マスクは13クラスIDの多クラス方式です。既存の二値マスク処理と混同しないよう、クラスID保持型のPyTorch Dataset対応を追加しています。
- 画像12枚を代表目視。道路環境の課題には使えますが、ブラジルの道路画像であり日本の道路安全を判定する用途には使いません。第三者コンテンツが含まれる場合の権利は全画像で個別確認していません。
- 整形済みZIPはCV_data_artifactsの固定Release assetに置き、Git/PyPIには画像・マスクを追加しません。Release v0.1.0を公開してassetのサイズ・SHAを再検証済み。API登録PRは提出準備中です。
