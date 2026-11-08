# 北斎風・浮世絵LoRA（Stable Diffusion 1.5）

## どんな重み？

浮世絵風の表現を画像生成に加えるLoRAです。水彩LoRAと同じ題材・乱数seedで生成し、色や線の表現を比べる課題に使えます。

- 基盤モデル：`stable-diffusion-v1-5/stable-diffusion-v1-5`
- トリガーワード：`sks`
- LoRAのライセンス表記：CreativeML OpenRAIL-M
- 必要容量：約19.2 MB
- 学習データ：配布者はArt Institute of Chicago Open AccessのCC0作品と説明

## 取得と利用条件

`weights.get("hokusai_sd15", accept_license=True)`を呼ぶとき、CreativeML OpenRAIL-Mの利用条件を確認したことを明示します。固定版の重みを配布元から取得し、サイズとSHA-256を確認します。重みのミラーや再配布はしません。

基盤モデルにもCreativeML Open RAIL-Mの条件があります。用途制限を含む[ライセンス本文](https://huggingface.co/spaces/CompVis/stable-diffusion-license)を読んでください。

学習画像については配布者の説明に基づいて記録しており、画像ごとの権利を独立に監査したものではありません。歴史的な絵画の作風を題材に、身近な物や風景で生成結果を比べる用途を想定しています。

## 出典

- [固定版モデルカード](https://huggingface.co/espressosession/latent-studio-hokusai-lora/blob/eb7ba98923bc91cf978a2175b2fb921b158c72e0/README.md)
- [固定版の重みファイルとチェックサム](https://huggingface.co/espressosession/latent-studio-hokusai-lora/blob/eb7ba98923bc91cf978a2175b2fb921b158c72e0/pytorch_lora_weights.safetensors)

利用時にPyTorch、Diffusers、Stable Diffusion 1.5の基盤モデルが別途必要です。GPUを推奨します。
