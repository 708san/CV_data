# TCD LoRA（Stable Diffusion 1.5）

## どんな重み？

TCD（Trajectory Consistency Distillation）を使い、Stable Diffusion 1.5の画像生成を少ないステップで試すためのLoRAです。絵柄を覚えさせる重みではありません。同じ題材を通常設定と少ないステップ設定で生成し、時間や見た目を比べる課題に使えます。

- 基盤モデル：`runwayml/stable-diffusion-v1-5`
- LoRAライセンス表記：MIT
- 必要容量：約135 MB
- トリガーワード：指定なし
- 例示設定：TCD scheduler、4ステップ、guidance scale 0

## 取得と利用条件

`weights.get("tcd_sd15")`を呼んだときに、固定版の重みを配布元から取得し、サイズとSHA-256を確認します。重みのミラーや再配布はしません。

LoRA本体はMIT表記ですが、画像生成には別途Stable Diffusion 1.5の基盤モデルが必要です。基盤モデルにはCreativeML Open RAIL-Mの利用制限があります。利用前に[ライセンス本文](https://github.com/CompVis/stable-diffusion/blob/main/LICENSE)を読んでください。基盤モデルの取得には配布元側の手続きが必要な場合があります。

## 出典

- [固定版モデルカード](https://huggingface.co/h1t/TCD-SD15-LoRA/blob/449a99f6bbded2bdbbc66386b2a4fbf8db8d3807/README.md)
- [固定版の重みファイルとSHA-256](https://huggingface.co/h1t/TCD-SD15-LoRA/blob/449a99f6bbded2bdbbc66386b2a4fbf8db8d3807/pytorch_lora_weights.safetensors)

利用時にPyTorch、Diffusers、Stable Diffusion 1.5の基盤モデルが別途必要です。GPUを推奨します。
