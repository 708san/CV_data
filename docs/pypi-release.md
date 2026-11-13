# PyPI公開・更新の運用記録

`cv-data-lesson==0.1.0a6`は2026-11-13にPyPIへ公開済みです。OCR結果の一覧表示を含む`0.1.0a7`を準備中です。PyPI上の同じ版は差し替えられないため、新しい版として公開します。

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

公開後の更新では、`pyproject.toml`の版を上げ、PyPI READMEと`project.urls.Documentation`のリンクを作成予定の`v<version>`へ合わせてmainへ反映します。同じ版から`v<version>`のGitHub Releaseを作成します。workflow完了後にPyPI JSON APIでversion、wheel、sdist、SHA-256、READMEを確認し、GitHub tag内のREADME・利用ガイドとインストールコマンドを照合します。

## 公開履歴

- `0.1.0a7`：OCR結果を読み順の一覧で示し、各行の画像部分を折りたたんで確認できる表示を追加。`OCRResult.to_dict()`は維持。公開準備中。

- `0.1.0a1`：2026-11-13公開。PyPI READMEに未公開の案内が残った。
- `0.1.0a2`：高校生向け説明・AI改造ガイド・利用者向け導入案内を整理。
- `0.1.0a3`：基本導入から表・画像表示までを一つのコマンドにまとめ、PyPI READMEの見出しとリンクを改善。2026-11-13に公開。
- `0.1.0a4`：Python 3.13での日本語フォント依存importエラーを修正。2026-11-13公開。
- `0.1.0a5`：基本導入と機能別extrasの説明を修正。`vision` extraへPyTorch/Torchvisionを含め、Colab Notebookを公開PyPI版固定に統一。2026-11-13公開。
- `0.1.0a6`：OCR表示・CPU依存、検出枠とSAM連携、TorchAO互換、単一LoRA選択Notebook、複数extrasの依存解決を改善。2026-11-13公開。

### `0.1.0a6`公開確認

- GitHub Release: [v0.1.0a6](https://github.com/708san/CV_data/releases/tag/v0.1.0a6)
- PyPI: [cv-data-lesson 0.1.0a6](https://pypi.org/project/cv-data-lesson/0.1.0a6/)
- main commit: `bc7a46e1d859f4dd04061cafe1af76ec0a3d0996`
- PyPI JSONでwheelとsource distributionの登録を確認。GitHub Actionsのbuild・publish jobは成功。
- 公開確認はColab実機検証を意味しない。Colab結果は[確認表](colab-verification.md)に記録する。

### `0.1.0a5`公開確認

- GitHub Release: [v0.1.0a5](https://github.com/708san/CV_data/releases/tag/v0.1.0a5)
- PyPI: [cv-data-lesson 0.1.0a5](https://pypi.org/project/cv-data-lesson/0.1.0a5/)
- main commit: `f9306108be06b185b84fd63660b490700c7786d1`
- wheel: 68,579 bytes; SHA-256 `7eefc0092d75a6d659ff7d15e67684ed856876d9f06e338e4d95f7ad0c433022`
- source distribution: 81,799 bytes; SHA-256 `3286565bf31e81095df8db1bf18b0a66a02eb44a706661ac11e9e74a050f5ca0`
- Python 3.13 clean venv: PyPI install、`cvlesson` import、学生向けデータ23件の一覧、`pip check`成功。基本importでTorchを読み込まないことを確認。
