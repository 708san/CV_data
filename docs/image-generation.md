# 画像生成モデル

## 用途

画像生成は、地域の困りごとを説明するポスターの挿絵、アプリのアイコン、手持ち写真のイラスト化などに使えます。完成画像内の日本語は誤りやすいため、見出し・説明・日時はスライドや画像編集ソフトで後から載せてください。生成画像は課題のアイデアを伝える補助であり、事実や安全性の証拠にはなりません。

## 登録済みLoRA

| ID | 内容 | 配布元ライセンス表示 | 固定取得先 | 用途と注意 |
| --- | --- | --- | --- | --- |
| `fluent_emoji_3d` | SDXL用の丸みのある3Dアイコン・絵文字風 | MIT（モデルカード）。学習データカードもMIT表記 | [モデルページ](https://huggingface.co/klibaner/fluent-emoji-style-sdxl)、revision `7ff36ef02e53e75a4ca3bd5bd326de3f30a41fba` | `msemj style`が自動でpromptに付く。単体で中央に置く絵が得意。文字描画には使わない |
| `watercolor_sdxl` | 写真・風景を水彩画風にする | Apache-2.0（モデルカード） | [モデルページ](https://huggingface.co/ostris/watercolor_style_lora_sdxl)、revision `0b65af0ac64347c8a35b82b4695ef5eadeffd5d7` | トリガー不要。許可を得た写真を地域課題の説明画像やポスター挿絵に使える。学習元データはモデルカードに記載なし |
| `pixel_art_sdxl` | 単体のピクセルアート素材 | CreativeML Open RAIL++-M（SDXLから継承と配布元表示）。学習元はCC0表示 | [モデルカード](https://huggingface.co/unsupervised-abdullah/pixel-art-sdxl-lora)、revision `85565b5401663e1277c70b51fd34a8b8c2b9e3f9` | `pxlsprite`が自動で付く。ごみ分別・食品ロスを学ぶミニゲームの素材向け。1,000枚の合成スプライトで学習。正確な16×16画像ではなく背景も一定しない |
| `thomas_cole_landscape` | 風景を19世紀の油彩画風にする | MIT（LoRA重み）。学習画像は配布元が米国でパブリックドメインと説明 | [モデルカード](https://huggingface.co/VRuins/thomas-cole-sdxl-lora)、revision `30373be8e89838dff2a4c6bfa2001d4188632695` | `tcole`が自動で付く。許可を得た風景写真を自然環境・公園紹介のポスター背景に使える。個々の学習画像の出典記録は保持されていない |

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

## 画像から画像への変換

SDXLのImage-to-Image機能を使い、入力写真と説明文から画像を作り直します。[Diffusersの画像変換API](https://huggingface.co/docs/diffusers/using-diffusers/img2img)では入力画像・prompt・strengthを使います。`strength`は0〜1の範囲で指定し、小さい値は入力の構図を残しやすく、大きい値は変更を強めます。

```python
from cvlesson import generation

print(generation.available_devices())
editor = generation.load(task="image-to-image", lora="watercolor_sdxl", device="cuda")
result = editor.generate(
    "地域の公園をきれいにする活動を表す、丸みのある明るい絵文字風イラスト",
    image="park.jpg",
    strength=0.55,
    seed=42,
)
result.save("park_icon.png")
```

写真の人物を使う場合は本人の同意を得てください。住所・学校名・顔などの個人情報が写っていないか確認してから、外部サービスへ画像をアップロードしてください。現在のAPIはHugging Faceからモデルを取得しますが、入力写真はモデル提供元へアップロードしません。

## 利用例の制限

- ポスターでは図・アイコンだけを生成し、文字と連絡先は後から正しく追加します。
- 写真のイラスト化では、許諾を得た写真を使います。入力と出力の両方を確認し、誤解を招く用途には使いません。
- `watercolor_sdxl`の学習元データはモデルカードに記載されていません。配布元の重みライセンスはApache-2.0ですが、学習画像の権利確認済みという意味ではありません。
- GPUは勝手に選択されません。`available_devices()`で確認し、使う場合は `device="cuda"` を明示します。

## Colabで動作を試す

[画像生成・LoRAの確認NotebookをColabで開く](https://colab.research.google.com/github/708san/CV_data/blob/codex/library-ocr-runtime/notebooks/colab/generation_smoke_test.ipynb)か、[Notebookの内容](../notebooks/colab/generation_smoke_test.ipynb)を確認できます。ColabでT4 GPUを選び、「すべてのセルを実行」してください。固定commitのライブラリを使い、登録済み4件を順に試します。初回はSDXL本体と4つの重みを取得するため数GBの空き容量が必要です。4件すべて成功すると最後に成功メッセージが出ます。Colab上で実行するまでは実環境テスト済みではありません。
