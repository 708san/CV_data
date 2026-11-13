# 空画像と翌日の天気

**公開済み**です。`datasets.get("sky_weather_next_day")`で固定Releaseから取得できます。出典・ライセンス・変更内容を確認してから利用してください。

## 何を調べられるか

全天空カメラ画像から、撮影した翌日の昼間に晴れ・曇り・雨のどれだったかを分類する教材データです。画像分類モデルを学習し、天気ラベルの正解率やクラスごとの違いを調べたり、画像から予測できること・できないことを考えたりできます。

画像はColorado州GoldenのNREL SRRLに設置されたカメラのものです。日本の天気予報を作るデータではありません。

## 内容

- 画像：1,000枚。224×224 JPEG。元画像の画素データは変更していません。
- クラス：`sunny`（晴れ）664枚、`cloudy`（曇り）184枚、`rainy`（雨）152枚。
- 分割：train 656枚、validation 161枚、test 183枚。
- splitは週単位の時系列ブロックを保ち、撮影日が別splitへ分かれないようにしています。
- 撮影日時はUTCと固定MST（UTC−7）、日付はMST基準です。固定MSTは夏時間を反映しません。

testでは雨の割合がtrainより大きく、各splitのクラス比率が異なります。正解率だけでなく、クラス別の結果や混同行列を確認してください。

## 取得後の表

`data.to_df()`は画像パス、分類ラベル、日本語ラベル、splitに加えて以下の列を返します。画像データ自体は表に読み込まず、パスで参照します。

- 時刻・日付：`captured_utc`、`captured_mst`、`capture_date_mst`、`target_date_mst`
- 数値列：`next_day_rain_mm`、`next_day_precipitation_mm`、`next_day_mean_cloud_cover_pct`、`next_day_snowfall_cm`
- 出典参照：`weather_data_source`、`source_image_path`

例：

```python
from cvlesson import datasets

data = datasets.get("sky_weather_next_day")
frame = data.to_df()
print(frame[[
    "image_path", "label_ja", "split",
    "next_day_rain_mm", "next_day_mean_cloud_cover_pct"
]].head())
```

分類では`label`を目的変数に使います。降水量や雲量は画像分類モデルの入力に自動では加わらず、`to_df()`で参照できる測定値です。分類以外の問いを立てる場合は、値の定義・単位・時間範囲を確認してから使ってください。

## 出典・ライセンス

画像：Joshua E. Hammond、Brian A. Korgel、NREL SRRL Minute-Resolution Sky Imagery Dataset。CC BY 4.0。  
気象データ：Open-Meteo Historical Weather APIのERA5再解析値。CC BY 4.0。  
[データセットカード](https://huggingface.co/datasets/knl2366/NREL_Sky_Imagery)／[Open-Meteoの利用条件](https://open-meteo.com/en/terms)／[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

再利用時は、各出典・ライセンスへのリンク・変更内容を表示してください。Open-Meteoの無料APIサービス利用条件は非商用で、教育コンテンツは例示された利用です。データのCC BY 4.0ライセンスとAPIサービスの条件は別に適用されます。APIから新たに取得する場合は最新条件を確認してください。

今回の入力ZIP（10,014,296 bytes）のSHA-256は`c30cf675819fea9b0bad62e0d0c8cb77890b808253e92c604b39d6c97a6f5280`です。入力ZIPには上流画像データの完全な固定revisionが記録されていないため、入力ZIPと整形済みartifactのSHA-256を固定して追跡します。

## 使うときの限界

- ERA5は再解析値であり、公式予報や現地の直接観測ではありません。
- 1地点・限られた季節の1,000枚です。日本や別の地域、別の季節の天気を代表しません。
- 「翌日の天気」ラベルは教材用ルールによる分類です。気象庁の公式な天気区分ではありません。
- データの時系列分割は保っていますが、testはrainyの割合がtrainと大きく異なります。
- 実際の外出・避難・農作業などの判断には使用しないでください。
