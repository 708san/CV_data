# CV Data Lesson — 高校生向け画像AIライブラリ

身近なテーマの画像データを取得し、画像分類・数値予測・文字読み取り・物体検出・領域分割・画像生成を試すPythonライブラリです。高校生が自分で決めた課題に合わせて、データや画像、出力を選んで試作できます。

## インストール

Python 3.11〜3.13で利用できます。画像を表示する場合は`display`も指定してください。

```bash
python -m pip install --pre 'cv-data-lesson[display]'
```

データ本体・モデル重みはインストール時には入りません。使うデータやモデルを選んだときに取得します。

## まず試す

```python
from cvlesson import datasets

# 生徒向けデータから題材を探す
print(datasets.list_tasks(audience="student"))
choices = datasets.list_available(task="classification", audience="student")
print(choices)

# 表示されたIDを選んで取得。初回だけデータをダウンロードします。
data = datasets.get("tomato_leaves")
print(data.to_df().head())
data.show_examples(6)
```

## できること

- **データを選ぶ**：データの説明、形式、出典、ライセンス、取得サイズを確認して、固定版を安全に取得します。
- **分類・回帰**：ResNet18の画像特徴を使い、課題に合わせた出力層を学習します。`fit`、`predict`、`score`で扱えます。
- **OCR**：日本語対応の学習済みモデルで文字・位置・信頼度を読み取ります。
- **物体検出・領域分割**：学習済みモデルで物体の枠や、指定した物のマスクを推論します。
- **画像生成・変換**：SDXLで文章から画像を生成し、登録済みLoRAや入力画像を使って絵柄を変えます。

高校生向けの機能説明と、データからモデルへつなぐ例は[使い方ガイド](docs/student-guide.md)へ。AIに自分の課題に合わせた変更を相談する場合は[AI改造ガイド](docs/ai-coding-guide.md)を参照してください。

## 使い方と利用条件

- まず[インストール案内](docs/installation.md)を確認してください。OCR、ResNet、検出、生成は追加の環境設定が必要です。
- [データ一覧と形式](docs/data-model-compatibility.md)から、扱いたいデータのタスク・ラベル・注釈を確認できます。
- データやモデルごとに利用条件が異なります。使う前に各説明ページのライセンス・出典・注意を確認してください。
- このパッケージに画像・マスク・LoRA重み・基盤モデル重みは含みません。取得やモデル読み込みは明示的に呼び出したときだけ始まります。
- GPUは自動で選びません。利用可能か確認してから明示的に指定します。CPUでの利用可否や必要容量は機能ごとの案内を確認してください。

ライブラリコードはMITライセンスです。データ・モデルの条件は個別に適用されます。
