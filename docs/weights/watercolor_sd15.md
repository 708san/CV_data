# 水彩LoRA（Stable Diffusion 1.5）

## どんな重み？

水彩画のような表現を画像生成に加えるLoRAです。同じ題材で、重みを使わない場合と使った場合の絵を比べる課題に使えます。

- 基盤モデル：`runwayml/stable-diffusion-v1-5`
- トリガーワード：`watercolor painting`、`impressionism, watercolor painting`
- 推奨する重みの範囲：0.1〜1.0（元モデル作者の説明）
- LoRAのライセンス表記：CreativeML OpenRAIL-M
- 必要容量：約302 MB
- 学習データ：配布者は歴史的絵画のパブリックドメイン画像と説明

## 取得と利用条件

`weights.get("watercolor_sd15", accept_license=True)`を呼ぶとき、CreativeML OpenRAIL-Mの利用条件を確認したことを明示します。固定版の重みを配布元から取得し、サイズとSHA-256を確認します。重みのミラーや再配布はしません。

基盤モデルにもCreativeML Open RAIL-Mの条件があります。用途制限を含む[ライセンス本文](https://huggingface.co/spaces/CompVis/stable-diffusion-license)を読んでください。基盤モデルの取得には配布元側の手続きが必要な場合があります。

学習画像の権利については配布者の説明に基づいて記録しています。個々の画像の権利を独立に調査・監査したものではありません。重みは他人の作品や実在人物の再現を保証するものではなく、課題は風景や身近な物の表現比較を推奨します。

## 出典

- [固定版モデルカード](https://huggingface.co/fladdict/watercolor/blob/cec30d1ee75123fa7662a4f058899fa0dc3adba0/README.md)
- [固定版の重みファイルとSHA-256](https://huggingface.co/fladdict/watercolor/blob/cec30d1ee75123fa7662a4f058899fa0dc3adba0/fladdict-watercolor-sd-1-5.safetensors)

利用時にPyTorch、Diffusers、Stable Diffusion 1.5の基盤モデルが別途必要です。GPUを推奨します。
