# 電力量計の数字画像（OCRの基礎）

7セグメント表示の電力量計画像に付いたCOCOの数字枠から、数字だけを切り出した977枚です。メーター記録を補助するOCRを考える入口として、0〜9の画像分類を試し、傾き・照明・反射による読み取りの違いを比べられます。

数字単体の分類データなので、数字列の順番、小数点、桁の意味、メーター全体の読み取り正解は含みません。表示全体の値を自動で決めるものではありません。元画像はタミル・ナードゥ州の消費者宅で撮影されています。公開artifactには全体写真を含めず、注釈のある数字枠と周囲8%の余白だけを収録しました。

- 出典：KARTHICK K and Kavaskar S (2019), [Mendeley Data v1](https://data.mendeley.com/datasets/fnn44p4mj8/1), DOI [10.17632/fnn44p4mj8.1](https://doi.org/10.17632/fnn44p4mj8.1)
- ライセンス：CC0 1.0。
- 画像：977切り出し。元画像単位を保ったtrain/val/test分割。
- 状態：固定Release公開済み（[energy-meter-digits-v0.1.0](https://github.com/708san/CV_data_artifacts/releases/tag/energy-meter-digits-v0.1.0)）。asset SHA-256：`e1e44c6666f4dbb13e0eed67cb3433f783b0e5bfbadf054c92814f566f7e599f`。

出典・制約は[監査記録](../../reports/energy_meter_digits-v0.1.0-audit.json)を参照。
