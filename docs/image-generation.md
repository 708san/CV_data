# 画像生成モデル

## 用途

SDXLは文章から画像を生成したり、入力画像の雰囲気を変えたりできます。ポスターの挿絵、アイコン、ゲーム素材、写真のスタイル変換などは使用例です。目的に合わせて題材を選べます。完成画像内の日本語は誤りやすいため、文字は別のアプリで載せてください。生成画像は事実や安全性の証拠にはなりません。

## インストール

画像生成に必要なDiffusers・PyTorch・PEFTなどは、`diffusion` extraからまとめて入ります。別に`pip install torch`を重ねる必要はありません。

```bash
python -m pip install --pre --upgrade 'cv-data-lesson[diffusion]'
```

Colabにも通常PyTorchが入っています。独自のCUDA版を選びたい場合だけ、PyTorch公式手順を先に実行してください。モデル本体とLoRA重みはこのinstallでは入りません。`generation.load()`を呼ぶときに取得します。詳細は[インストール案内](installation.md)を参照してください。

## 登録済みLoRA

| ID | モデルの特徴 | 配布元ライセンス表示 | 固定取得先 | 使用例と注意 |
| --- | --- | --- | --- | --- |
| `fluent_emoji_3d` | 丸みのある3Dアイコン・絵文字風の単体イラスト | MIT（モデルカード）。学習データカードもMIT表記 | [モデルページ](https://huggingface.co/klibaner/fluent-emoji-style-sdxl)、revision `7ff36ef02e53e75a4ca3bd5bd326de3f30a41fba` | `msemj style`が自動でpromptに付く。アイコン、挿絵、発表資料の素材など。文字描画は苦手 |
| `watercolor_sdxl` | 画像を水彩画風に変換・生成 | Apache-2.0（モデルカード） | [モデルページ](https://huggingface.co/ostris/watercolor_style_lora_sdxl)、revision `0b65af0ac64347c8a35b82b4695ef5eadeffd5d7` | トリガー不要。写真のスタイル変換、風景背景、説明用イラストなど。学習元データはモデルカードに記載なし |
| `pixel_art_sdxl` | 単体の物体をピクセルアート風に生成 | CreativeML Open RAIL++-M（SDXLから継承と配布元表示）。学習元はCC0表示 | [モデルカード](https://huggingface.co/unsupervised-abdullah/pixel-art-sdxl-lora)、revision `85565b5401663e1277c70b51fd34a8b8c2b9e3f9` | `pxlsprite`が自動で付く。ゲーム用の小物、キャラクター、教材の図版など。1,000枚の合成スプライトで学習。正確な16×16画像ではなく背景も一定しない |
| `thomas_cole_landscape` | 風景をHudson River School風の油彩画にする | MIT（LoRA重み）。学習画像は配布元が米国でパブリックドメインと説明 | [モデルページ](https://huggingface.co/VRuins/thomas-cole-sdxl-lora)、revision `30373be8e89838dff2a4c6bfa2001d4188632695` | `tcole`が自動で付く。風景写真の変換、地域・自然を扱う背景や挿絵など。個々の学習画像の出典記録は保持されていない |

表の使用例は入口の例で、用途を限定するものではありません。LoRAは絵柄を加えるもので、入力の内容や構図が保たれるとは限りません。

モデル重みは約341MB、約12MB、約186MB、約228MBです。Git、PyPI、CV_data_artifactsへはコピーせず、利用者が `generation.load()` を呼んだ場合にだけ固定revisionから直接取得します。各重みは登録済みSHA-256と照合します。pixel artのSHA-256は `acbae146be564ea1bcbc65c233b374a30972249aea15c8a0bcf383983603c297`、Thomas Cole風のSHA-256は `6ad18bdf606c25be342c2acda1fbcd02ad669c40163f25027d886022b52bea8a` です。

## 権利確認メモ

- LoRAのモデルカードはライセンスをMITと表示し、学習元を `Norod78/microsoft-fluentui-emoji-512-whitebg` と記載しています。トリガーは `msemj style` です。[モデルカード](https://huggingface.co/klibaner/fluent-emoji-style-sdxl)
- 学習データのカードはMIT、7,564例と表示し、Microsoft Fluent UI EmojiリポジトリのSVGとファイル名を画像・テキストへ変換したと説明しています。[学習データカード](https://huggingface.co/datasets/Norod78/microsoft-fluentui-emoji-512-whitebg)
- 元リポジトリの[LICENSE](https://github.com/microsoft/fluentui-emoji/blob/main/LICENSE)もMITです。画像はMicrosoftのFluent Emojiに由来するため、モデルカードの注意に従い、Microsoftの公式・提携モデルと誤認させないでください。生成物の商標・著作権・利用先の条件は別途確認してください。
- 基盤の[SDXL 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)はCreativeML Open RAIL++-Mです。LoRAのMIT表記だけで基盤モデルの条件が置き換わるわけではありません。SDXLライセンスの利用制限も守ってください。
- 水彩LoRAはモデルページにApache-2.0とSDXL 1.0対応が表示されています。[配布元カード](https://huggingface.co/ostris/watercolor_style_lora_sdxl)は学習元データを示していないため、学習データの権利・来歴までは確認できていません。LoRA重みのライセンス表示と学習画像の来歴を混同しないでください。
- [Pixel Art SDXL LoRA](https://huggingface.co/unsupervised-abdullah/pixel-art-sdxl-lora)はモデルカードがSDXLから継承したCreativeML Open RAIL++-Mと表示し、学習データをCC0のPixel Art Atlasから選んだ合成画像1,000枚と説明しています。学習画像は合成で、キャプションは人手確認されていないと記載されています。利用時はSDXLの条件にも従ってください。
- [Thomas Cole SDXL LoRA](https://huggingface.co/VRuins/thomas-cole-sdxl-lora)は重みをMITと表示し、約100〜110点の絵画をWikimedia CommonsとWikiArtから収集したと説明しています。配布元は米国でパブリックドメインとしていますが、画像ごとの出典一覧は保持していないと明記しています。基盤SDXLの条件は別途適用されます。
- ここでは重みを再配布せず、各利用者がHugging Faceから直接取得します。取得元のライセンス・注意書きは利用時にも確認してください。

## 権利情報が足りず見送った候補

`Muapi/flat-illustration`、`ramel2/emotional-flat-illustration-sdxl-lora`、ポスター風LoRAは、学習元の来歴やライセンス条件を十分に確認できなかったため登録していません。

## 生成パラメータを調整する

`ImageGenerator.generate()`は、パラメータを省略すると`num_inference_steps=25`、`guidance_scale=7.0`、`strength=0.65`、`use_trigger=True`を使います。`seed`は未指定ならランダム、`width`と`height`は基盤パイプライン既定のサイズを使います。

`diffusion` extraはPyPI公開済みPEFT 0.21.2以降を導入します。Colabなどに古いTorchAOが事前に入っていても、通常の非量子化SDXL LoRAを読み込む間だけTorchAOの機能判定を一時的に無効にします。環境からTorchAOを削除せず、TorchAO量子化モデルをサポートする変更でもありません。PEFT側でも同種の互換修正が進んでいます（[PEFT issue #3964](https://github.com/huggingface/peft/issues/3964)、[fix PR #3989](https://github.com/huggingface/peft/pull/3989)）。

| 引数 | 内容 |
|---|---|
| `num_inference_steps` | 生成を繰り返す回数。増やすと遅くなります。細部が整う場合がありますが、常に改善するわけではありません。 |
| `guidance_scale` | promptへの追従の強さ。高すぎると画像が不自然になることがあります。 |
| `negative_prompt` | 避けたい要素の文章。出力から完全に取り除く保証はありません。 |
| `seed` | 固定値を指定して比較しやすくします。違うGPU・ライブラリ版で同一画像を保証しません。 |
| `width`、`height` | 出力サイズ。大きいほど細部を表しやすい一方で、VRAMと時間を多く使います。8の倍数を使います。 |
| `strength` | Image-to-Imageで元画像を残す度合い。小さいほど保持し、大きいほど変化が強くなります。 |
| `use_trigger` | 登録LoRAのトリガー語を自動でpromptへ加えるかどうか。 |

入力範囲も生成前に確認します。stepsは1以上の整数、guidance scaleは有限の0以上、strengthは有限の0〜1です。width/heightを指定する場合は8以上の8の倍数、seedは整数、negative promptは文字列、use_triggerはTrue/Falseにしてください。不正な値は画像モデルを実行する前にValueErrorで知らせます。

例では768×768、25 stepsを使います。T4でメモリ不足になったらサイズを512へ下げ、生成時間を短くしたい場合はstepsを下げます。同じpromptとseedを保ち、一度に一つの値だけ変えると違いを比べやすくなります。Schedulerなど現在のAPIにないDiffusers固有設定は指定できません。

```python
from cvlesson import generation

creator = generation.load(task="text-to-image", lora="fluent_emoji_3d", device="cuda")
result = creator.generate(
    "丸みのある3Dの青い自転車アイコン",
    num_inference_steps=25,
    guidance_scale=7.0,
    width=768,
    height=768,
    negative_prompt="blurry, low quality",
    seed=42,
)
```

## 画像から画像への変換

SDXLのImage-to-Image機能を使い、入力写真と説明文から画像を作り直します。[Diffusersの画像変換API](https://huggingface.co/docs/diffusers/using-diffusers/img2img)では入力画像・prompt・strengthを使います。`strength`は0〜1の範囲で指定し、小さい値は入力の構図を残しやすく、大きい値は変更を強めます。

Colab左側の「ファイル」欄から画像をアップロードし、表示されたパスを`image_path`または`SOURCE_IMAGE_PATH`へ設定してください。`files.upload()`のポップアップは使いません。Safariなどでアップロードに失敗する場合は、画像をGoogle Driveへ置き、Driveをマウントしてそのファイルパスを指定してください。 ローカルでは`image_path`に実際の画像ファイルのパスを指定してください。

```python
from pathlib import Path

image_path = "/content/your-image.jpg"  # Colab左側の「ファイル」欄からアップロードしたパス
if not Path(image_path).is_file():
    raise FileNotFoundError("Colab左側の「ファイル」欄から画像をアップロードし、image_pathをそのファイル名に合わせてください。")
```

```python
from cvlesson import generation

print(generation.available_devices())
editor = generation.load(task="image-to-image", lora="watercolor_sdxl", device="cuda")
result = editor.generate(
    "地域の公園をきれいにする活動を表す、丸みのある明るい絵文字風イラスト",
    image=image_path,
    strength=0.55,
    seed=42,
)
result.save("park_icon.png")
```

写真の人物を使う場合は本人の同意を得てください。住所・学校名・顔などの個人情報が写っていないか確認してから、外部サービスへ画像をアップロードしてください。現在のAPIはHugging Faceからモデルを取得しますが、入力写真はモデル提供元へアップロードしません。

## 注意事項

- 画像モデルが描く文字は誤りやすいため、正確さが必要な文字情報は生成後に確認・追加してください。
- 写真を入力する場合は、利用許諾と写り込んだ人の同意を確認してください。出力も、目的に合っているか見直してください。
- `watercolor_sdxl`の学習元データはモデルカードに記載されていません。配布元の重みライセンスはApache-2.0ですが、学習画像の権利確認済みという意味ではありません。
- GPUは勝手に選択されません。`available_devices()`で確認し、使う場合は `device="cuda"` を明示します。

## Colabで動作を試す

[画像生成・LoRAの確認NotebookをColabで開く](https://colab.research.google.com/github/708san/CV_data/blob/main/notebooks/colab/generation_smoke_test.ipynb)か、[Notebookの内容](../notebooks/colab/generation_smoke_test.ipynb)を確認できます。ColabでT4 GPUを選び、「すべてのセルを実行」してください。公開版`0.1.0a6`を使い、登録済み4件の情報を確認してから選択した1件だけを取得・生成します。Image-to-Imageでは利用者が明示アップロードした画像を使います。初回はSDXL本体と選択したLoRAの重みを取得するため数GBの空き容量が必要です。Colabでの実行結果はまだ確認されていません。
