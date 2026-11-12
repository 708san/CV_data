# 家庭ごみの素材分類（TrashNet）

段ボール・ガラス・金属・紙・プラスチック・その他ごみの画像2,527枚です。家庭で出る容器や包装の素材を分類する試作に使えます。**データは白い背景で撮影されています**。家のごみ箱や生活空間で撮影した画像とは条件が違うため、生徒が撮った安全な空容器画像を追加して、背景が変わると分類がどう変わるかを比較する課題に向きます。

素材クラスは自治体の分別可否を表しません。分別案内を作る場合は地域の公式ルールを別途参照し、モデルの予測だけで処分方法を決めないでください。

- 出典：Gary Thung and Mindy Yang, [TrashNet固定コミット](https://github.com/garythung/trashnet/tree/6fa2b878c6c1b4304b91109070ce0edf9279bb31)
- ライセンス：MIT。著作権表示とライセンス全文をartifactに同梱。
- 画像：2,527枚。画素は変更せず、画像単位で決定的なtrain/val/test分割を作成。
- 状態：固定Release公開済み（[trashnet-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/trashnet-v0.1.0)）。asset SHA-256：`ce35f986308784e280bc7c757c5346043d4b5514818ce8260df9534a85417eea`。

出典・制約は[監査記録](../../reports/trashnet-v0.1.0-audit.json)を参照。
