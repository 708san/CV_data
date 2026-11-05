# 文化祭案内アイコンの画像

青・白を基調とする168枚のアイコン画像です。56種類のモチーフが3パターンずつ含まれています。512×512画素のPNG画像と、画像の内容を説明する文を組み合わせて使います。

このデータは、画像を種類別に分類する教材ではなく、LoRA（Low-Rank Adaptation：少ない追加パラメータでモデルを調整する技術）で画像の表現を学習するための素材です。

## 取得して調べる

```python
from cvlesson import datasets

data = datasets.get("festival_icons")
print(data.images_dir)
print(data.labels_csv)       # image,caption
print(data.metadata_jsonl)   # file_name,text
captions = data.to_df()      # pip install -e '.[dataframe]'
print(captions.head())
```

学習時のトリガー語（特定の表現を呼び出すための語）は`universal_icon_style`です。元教材では、新たな「ステージアイコン」を作る課題に利用します。

## 出典と利用条件

- 元データ：[CV_sample_data 文化祭アイコン](https://github.com/708san/CV_sample_data/tree/main/cases/festival-icons)
- 利用する固定版：[festival-v1.0.0](https://github.com/708san/CV_sample_data/releases/tag/festival-v1.0.0)
- **制作者からGitHub一般公開の許可はあるものの、改変・商用利用・再配布に関する標準ライセンスは設定されていません。** これらの用途には別途確認が必要です。

画像はこのライブラリやPyPIへ再収録しません。配布元の固定Releaseから取得します。

## 固定Releaseの実体監査

`festival-v1.0.0`は2026-11-05に全168枚を検査しました。ZIPのSHA-256、画像の読み込み、`labels.csv`と`metadata.jsonl`の整合性を確認し、破損0枚、完全一致重複候補0件、キャプション欠損0件でした。8×8平均ハッシュでは類似候補417組が見つかりましたが、これはレビュー用候補であり、自動削除や重複確定はしていません。権利審査は未実施です。[監査レポート](../../reports/festival-icons-v1.0.0.json)

## 画像とラベルの検査

固定Releaseから取得した168枚を検査するには、開発用の `python -m cvlesson.audit festival_icons --check-images --report report.json` を使います。Pillowが必要です。この検査は改変・商用利用・再配布を許可するものではありません。
