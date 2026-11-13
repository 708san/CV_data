# PyPI公開・更新の運用記録

`cv-data-lesson==0.1.0a4`は2026-11-13にPyPIへ公開済みです。PyPI上の同じ版は差し替えられません。次の更新は`0.1.0a5`としてビルドし、GitHub Releaseの公開をきっかけにTrusted Publishingで送ります。

## 利用者向けコマンド

```bash
python -m pip install --pre cv-data-lesson
```

PyPIへ一般公開した各alpha版は、同じコマンドで取得できます。READMEと利用ガイドは公開済み版に合わせて更新します。開発checkoutやeditable installは開発者向けの作業であり、利用者向けインストール案内へ混ぜません。

## パッケージに含めるもの

PyPIへ置くのはPythonコード、カタログ・説明・ライセンス等のテキスト、wheelとsource distributionです。画像・マスク・LoRA・基盤モデル重みは含めません。データは利用者がAPIを呼んだ時に固定版Releaseから取得し、LoRA・モデル重みは機能の読み込み時に配布元から取得する設計です。PyPIのコードライセンスはMITですが、個別データ・モデルの条件はそれぞれの説明に従います。

基本インストールに、表・画像例の確認で使う軽量依存も含めます。ResNet、OCR、検出・領域分割、画像生成の重い依存は機能別extrasに分離します。

```bash
python -m pip install --pre cv-data-lesson
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

公開後の更新では、`pyproject.toml`の版を上げ、mainへ反映した同じ版から`v<version>`のGitHub Releaseを作成します。workflow完了後にPyPI JSON APIでversion、wheel、sdist、SHA-256を確認します。

## 公開履歴

- `0.1.0a1`：2026-11-13公開。PyPI READMEに未公開の案内が残った。
- `0.1.0a2`：高校生向け説明・AI改造ガイド・利用者向け導入案内を整理。
- `0.1.0a3`：基本導入から表・画像表示までを一つのコマンドにまとめ、PyPI READMEの見出しとリンクを改善。2026-11-13に公開。
- `0.1.0a4`：Python 3.13での日本語フォント依存importエラーを修正。2026-11-13公開。
