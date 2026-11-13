# PyPI初回公開の準備

初回候補はパッケージ名`cv-data-lesson`、版`0.1.0a1`（alpha）です。2026-11-13にPyPI JSON APIを確認した時点ではプロジェクト情報が見つからずHTTP 404でした。これは名前の予約・将来の利用可能性を保証しません。PyPIで公開されるまでは`pip install cv-data-lesson`は使えません。

## パッケージに含めるもの

PyPIへ置くのはPythonコード、カタログ・説明・ライセンス等のテキスト、wheelとsource distributionです。画像・マスク・LoRA・基盤モデル重みは含めません。データは利用者がAPIを呼んだ時に固定版Releaseから取得し、LoRA・モデル重みは機能の読み込み時に配布元から取得する設計です。PyPIのコードライセンスはMITですが、個別データ・モデルの条件はそれぞれの説明に従います。

公開後のalpha版インストール例：

```bash
python -m pip install --pre cv-data-lesson
python -m pip install --pre 'cv-data-lesson[display]'
```

alpha版を使うため`--pre`を指定します。ResNet、OCR、検出・領域分割、画像生成は必要なextraと別途導入するフレームワークが異なります。詳細は[インストール案内](installation.md)を参照してください。

## PyPIで一度だけ行う設定

PyPIへログインし、アカウント設定の **Publishing → Add a new pending publisher** から次を登録します。

| 項目 | 値 |
| --- | --- |
| PyPI project name | `cv-data-lesson` |
| Owner | `708san` |
| Repository name | `CV_data` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

GitHub側の`pypi` environmentを作成し、必要ならdeployment protection ruleを設定します。GitHub ActionsはOIDCのTrusted Publishingを使い、PyPI API tokenをGitHub Secretsへ保存しません。PyPIのpending publisherは最初の公開まではプロジェクト名を予約しないため、登録後も名前が取られる可能性があります。

公式手順：[PyPIのpending publisher作成](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)、[GitHub ActionsからのTrusted Publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/)。

## 公開workflowの条件

`.github/workflows/publish.yml`はGitHub Releaseを`published`にした時だけ起動します。ビルドとmetadata検査を行い、Release tagが`pyproject.toml`の版と一致すること、配布物に画像・モデル重みが含まれないことを確認してから、検証済みartifactをPyPIへ送ります。手動実行やtag pushでは起動しません。

この文書とworkflowの準備はPyPI公開を実行しません。初回公開には、PyPIのpublisher設定、GitHub Release/tagの作成、PyPIアップロードについて別途確認が必要です。
