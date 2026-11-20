# PyPI 0.1.1公開の準備

PyPIには既存の`cv-data-lesson==0.1.0`が公開されています。これは自動GPU優先・CPUフォールバック修正前の版です。今回の公開候補は`0.1.1`で、`pip install cv-data-lesson`がこの修正版を取得できる状態にします。

## パッケージに含めるもの

PyPIへ置くのはPythonコード、カタログ・説明・ライセンス等のテキスト、wheelとsource distributionです。画像・マスク・LoRA・基盤モデル重みは含めません。データは利用者がAPIを呼んだ時に固定版Releaseから取得し、LoRA・モデル重みは機能の読み込み時に配布元から取得する設計です。PyPIのコードライセンスはMITですが、個別データ・モデルの条件はそれぞれの説明に従います。

公開後のインストール例：

```bash
python -m pip install cv-data-lesson==0.1.1
python -m pip install 'cv-data-lesson[display]'
```

ResNet、OCR、検出・領域分割、画像生成は必要なextraと別途導入するフレームワークが異なります。詳細は[インストール案内](installation.md)を参照してください。

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
