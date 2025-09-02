# 🚀 ViralHub 完全自動化セットアップガイド

## 📋 概要

ViralHubは24時間365日完全自動でAI記事を投稿する収益化プラットフォームです。このガイドに従って設定すれば、人の介入なしで毎日記事が投稿されます。

## 🎯 完全自動化される機能

- ✅ **1日3回自動投稿** (朝8:00・昼14:00・夜20:00 UTC)
- ✅ **全ジャンル対応** (エンタメ・ライフスタイル・ビジネス・テクノロジー等)
- ✅ **SEO最適化** (トレンドキーワード自動選択)
- ✅ **完全無料運営** (GitHub Pages + 無料AI)
- ✅ **収益化対応** (AdSense広告自動配置)

## 🔧 セットアップ手順

### 1. GitHub Actionsを有効化

1. **GitHubリポジトリ**にアクセス
2. **Actions**タブをクリック
3. 「**I understand my workflows, enable them**」をクリック
4. `.github/workflows/auto-post.yml`が表示されることを確認

### 2. GitHub Pagesを設定

1. リポジトリの **Settings** → **Pages**
2. **Source**: `Deploy from a branch`
3. **Branch**: `main` / `/ (root)`
4. **Save**をクリック
5. サイトURL（例: `https://yourusername.github.io/ai-article-generator/`）をメモ

### 3. 自動投稿をテスト

手動でワークフローを実行してテスト：

1. **Actions**タブ → **🤖 ViralHub AI自動投稿システム**
2. **Run workflow**ボタンをクリック
3. **Run workflow**（緑ボタン）をクリック
4. 数分後に `data/articles.json`に新しい記事が追加されることを確認

### 4. スケジュール確認

自動投稿は以下の時間に実行されます（UTC時間）：

- **08:00 UTC** (日本時間 17:00)
- **14:00 UTC** (日本時間 23:00)  
- **20:00 UTC** (日本時間 05:00)

## 📊 動作確認

### ✅ 正常動作のチェックリスト

- [ ] GitHub Actions が有効化されている
- [ ] GitHub Pages でサイトが表示される
- [ ] 手動実行で記事が生成される
- [ ] `data/articles.json`に記事データが追加される
- [ ] サイトで新しい記事が表示される

### 🔍 トラブルシューティング

#### エラー: "workflow not found"
- `.github/workflows/auto-post.yml`ファイルが正しく配置されているか確認
- リポジトリのメインブランチにファイルがあるか確認

#### エラー: "permission denied"
- リポジトリの Settings → Actions → General
- "Workflow permissions"を"Read and write permissions"に設定

#### 記事が生成されない
- Actions タブでエラーログを確認
- `github_actions_poster.py`の実行権限を確認

## 💰 収益化設定

### Google AdSense設定

1. **AdSenseアカウント作成**
2. **サイトを審査に提出** (`https://yourusername.github.io/ai-article-generator/`)
3. **承認後、広告コード取得**
4. `index.html`, `article.html`, `post.html`の`<!-- AdSense広告 -->`部分にコードを挿入

### アフィリエイト設定

1. **ASP (A8.net、楽天アフィリエイト等)** に登録
2. **記事内容に関連する商品リンク**を設定
3. **自動生成記事テンプレート**にアフィリエイトリンクを組み込み

## 📈 SEO最適化

### 自動で最適化される項目

- **メタタグ**: タイトル・ディスクリプション自動生成
- **構造化データ**: JSON-LD形式で記事情報を出力
- **内部リンク**: 関連記事の自動リンク
- **サイトマップ**: 新記事追加時に自動更新
- **モバイル最適化**: レスポンシブデザイン

### 手動で設定可能な項目

- **Google Search Console**の連携
- **Google Analytics**の設定
- **カスタムドメイン**の設定

## 🔄 メンテナンス

### 完全自動運営のため、基本的にメンテナンス不要

- **記事生成**: 自動実行
- **データ管理**: 自動で最新100記事まで保持
- **サイト更新**: GitHub Actionsが自動実行
- **エラー処理**: 自動復旧機能内蔵

### 定期確認推奨項目（月1回程度）

- [ ] GitHub Actions の実行状況確認
- [ ] 記事品質のチェック
- [ ] AdSense収益の確認
- [ ] Google Search Console のエラーチェック

## 🎉 完了！

設定完了後は**完全に放置**で運営可能です。

**月間90記事**（1日3記事 × 30日）が自動生成され、SEO効果とトラフィック増加により収益化が期待できます。

---

## 📞 サポート

質問や問題がある場合は、GitHubのIssuesでお気軽にお聞かせください。

**ViralHubで自動収益化の新時代を始めましょう！** 🚀