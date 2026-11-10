# LeFood-Set: Leftovers Food Dataset

## 出典・利用条件

- 公式データ：[Mendeley Data v1](https://data.mendeley.com/datasets/cchsk79jkt/1)、DOI `10.17632/cchsk79jkt.1`
- 論文：[Sari, Nakazawa & Wani (2025), PLOS ONE](https://doi.org/10.1371/journal.pone.0320426)
- Mendeley v1と論文はCC BY 4.0を表示。必要な帰属と変更表示をartifactに含める。
- 教材用artifact v0.1.0は[CV_data_artifacts Release](https://github.com/708san/CV_data_artifacts/releases/tag/lefood-set-v0.1.0)で公開済み。回帰用APIは未実装のため、まだ`cvlesson`から取得できない。

## 内容

524ペア、1,048枚の食前・食後JPEGと、34料理カテゴリのメタデータを含む。CSVには前後重量、観察者による7段階評価、導出した重量差・残量比、ペア単位のtrain/validation/test列がある。元画像は画素変更せず格納し、元の撮影順を保つIDでファイル名を整理した。

公式説明の678データ行のうち、524行は画像が揃う。残り154行は食前・食後画像の両方がなく、artifactから除外した。10ペアは計測された食後重量が食前重量より大きい。値を修正せず、`weight_order_anomaly`を付けて残す。

全1,048 JPEGをデコードし、公式ファイル別SHA-256・サイズと一致すること、完全一致重複がないこと、GPS/EXIF/orientation metadataがないことを確認した。全ペアのコンタクトシートを目視し、料理と皿が写り、人物・顔・個人識別情報は見つからなかった。

## 高校生の身近な課題への利用

食べる前後の画像と実測重量、見た目の評価を比べ、家庭・学校・食堂で食べ残しを減らすために何を測ればよいか考える題材にできる。食べ残しの残量推定結果と実測重量のずれを分析し、改善案を立てる。

食事や撮影条件はインドネシアの病院食研究に由来する。日本の学校給食を代表しないため、地域の結論を出すには現地で同じ方法の計測が必要。健康、栄養、患者個人の判断や医療用途には使わない。

## 派生artifact

- Archive: `lefood-set-v0.1.0.zip`
- Size: 53,035,809 bytes
- SHA-256: `ca1846273d0636ea59f387a586c6f004cfc02d58a639ad5a3c7c844b66cb863a`
- Source file-set SHA-256 aggregate: `096b72129bd62ef742d5062db575f6c713eae2d6ea6937131de62b1a2b18a594` (source inventory includes per-file SHA-256 and byte sizes)
- Artifact manifest: [`manifests/lefood_set-v0.1.0.json`](../../manifests/lefood_set-v0.1.0.json)
- Rights record: [`licenses/lefood-set-v1.md`](../../licenses/lefood-set-v1.md)
- Audit report: [`reports/lefood-set-v0.1.0-audit.json`](../../reports/lefood-set-v0.1.0-audit.json)
