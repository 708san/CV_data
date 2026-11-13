高校生が身近な課題に画像AIを活用するための教材ライブラリ「CV教材ライブラリ」です。画像分類・数値予測・文字読み取り・物体検出・領域分割・画像生成を試せます。自分で決めた課題に合わせて、データや画像、出力を選べます。

配布名は`cv-data-lesson`、Pythonから読み込む名前は`cvlesson`です。
PyPIでは配布名と版番号がページタイトルに表示されます。GitHubのこのREADMEは更新中の内容、PyPI上のREADMEは公開時点の内容です。各公開版の使い方は、その版のリリースノートとリンク先のガイドをご覧ください。

## インストール

Python 3.11〜3.13で利用できます。現在はalpha版のため、pipに開発版も選ばせる`--pre`を付けます。通常のデータ利用と表・画像例の表示は、次の1行で導入できます。

```bash
python -m pip install --pre cv-data-lesson
```

データ本体・モデル重みはインストール時には入りません。使うデータやモデルを選んだときに取得します。

## まず試す

```python
from cvlesson import datasets

# データを一覧で見て、使いたいIDを選ぶ
for item in datasets.list_available(audience="student")[:8]:
    print(item["id"], item["name_ja"], "—", item["task"])

# 例：トマトの葉データを取得して、表と画像を確認
data = datasets.get("tomato_leaves")
print(data.to_df().head())
data.show_examples(6)
```

## できること

- **データを選ぶ**：データの説明、形式、出典、ライセンス、取得サイズを確認して、固定版を安全に取得します。
- **分類・回帰**：ResNet18の画像特徴を使い、課題に合わせた出力層を学習します。`fit`、`predict`、`score`で扱えます。
- **OCR**：日本語対応の学習済みモデルで文字・位置・信頼度を読み取り、文字が多い画像でも一覧と行別画像で確認できます。元のOCR結果は辞書やJSONとして他のアプリへ渡せます。
- **物体検出・領域分割**：学習済みモデルで物体の枠や、指定した物のマスクを推論します。
- **画像生成・変換**：SDXLで文章から画像を生成し、登録済みLoRAや入力画像を使って絵柄を変えます。

高校生向けの機能説明と、データからモデルへつなぐ例は[使い方ガイド](https://github.com/708san/CV_data/blob/v0.1.0a6/docs/student-guide.md)へ。AIに自分の課題に合わせた変更を相談する場合は[AI改造ガイド](https://github.com/708san/CV_data/blob/v0.1.0a6/docs/ai-coding-guide.md)を参照してください。

## 使い方と利用条件

- まず[インストール案内](https://github.com/708san/CV_data/blob/v0.1.0a6/docs/installation.md)を確認してください。CPU版OCRは`[ocr]`だけで導入できます。検出・領域分割・画像生成も機能別extraから必要なPython依存を導入できます。
- [データ一覧と形式](https://github.com/708san/CV_data/blob/v0.1.0a6/docs/data-model-compatibility.md)から、扱いたいデータのタスク・ラベル・注釈を確認できます。
- [Colabで公開版を試す手順](https://github.com/708san/CV_data/blob/v0.1.0a6/docs/colab-verification.md)に、機能別Notebookとランタイムをまとめています。
- データやモデルごとに利用条件が異なります。使う前に各説明ページのライセンス・出典・注意を確認してください。
- このパッケージに画像・マスク・LoRA重み・基盤モデル重みは含みません。取得やモデル読み込みは明示的に呼び出したときだけ始まります。
- GPUは自動で選びません。利用可能か確認してから明示的に指定します。CPUでの利用可否や必要容量は機能ごとの案内を確認してください。

ライブラリコードはMITライセンスです。データ・モデルの条件は個別に適用されます。
