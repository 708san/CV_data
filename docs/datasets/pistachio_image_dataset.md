# Pistachio Image Dataset（公開保留）

殻付きピスタチオ2種類を画像分類する課題候補です。「画像の見た目から分類できるか」「撮影条件やクラス数の偏りは精度にどう影響するか」を調べる題材に向きます。分類結果を販売価格・品質・安全性の判定として使わないでください。

## 現時点で確認したこと

- 公式Mendeley Dataの固定版1を確認しました。
- 公式ページのライセンス表記はCC BY 4.0です。
- 公式固定ZIPのサイズは27,859,492 bytes、SHA-256は`140760707018b7f53d91a86a1d7be96d92b1a0d26a75690ab9280ed1170df895`です。
- SHA-256一致後に安全展開し、画像フォルダから2,148枚を全量検査しました。
- Kirmizi_Pistachio 1,232枚、Siirt_Pistachio 916枚で、すべてJPEG・600×600・RGB、破損0枚、完全一致重複0グループでした。
- 画像を変更せず、seed 42でクラス別にtrain 1,717、val 214、test 217へ分ける共通classification artifactを生成し、manifest照合に成功しました。これはローカル監査物であり、公開Releaseにはまだ登録していません。
- 固定source manifestを`CV_data_artifacts`に保存しました。

## 公開保留の理由

MendeleyページのCC BY 4.0表記と固定ZIPは確認できましたが、元画像の第三者権利や、データ提供者が記載した「dataset内コンテンツの追加許諾が必要になり得る」という注意を別途確認していません。また、公式ZIPには画像以外の特徴量・説明ファイルも含まれるため、教材artifactへ含める範囲を限定する必要があります。

そのため正式API・生徒向けNotebook・PyPI配布にはまだ追加していません。元画像権利、クレジット、ZIP内の非画像ファイルの扱い、共通artifactの公開条件を確認後に判断します。

出典：[公式Mendeley Dataページ](https://data.mendeley.com/datasets/h7pf57cgg9/1)
