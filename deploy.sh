#!/bin/bash

echo "🚀 ViralHub サイトのデプロイを開始します"

# 変更をステージング
echo "📁 変更ファイルをステージング中..."
git add assets/articles-loader.js
git add assets/article.js  
git add article.html
git add index.html
git add data/articles.json

# コミット
echo "💾 変更をコミット中..."
git commit -m "記事表示システムの完全修復

- article.jsのクラス名不一致を修正 (.article-container → .article-main)
- article.htmlの静的ChatGPT記事コンテンツを削除し動的テンプレートに変更
- URLパラメーター(?id=記事ID)による記事読み込みを有効化
- LocalStorageテスト記事の完全削除機能を強化
- 記事タイトル、作者、カテゴリー、タグの動的表示
- パンくずリストとメタデータの正しい更新

これで記事タップ時に正しい記事が表示されます

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# プッシュ
echo "🌐 GitHubにプッシュ中..."
git push origin main

echo ""
echo "✅ デプロイ完了！"
echo "🌐 サイトURL: https://daito-iwa.github.io/ai-article-generator/"
echo ""
echo "GitHub Pagesの反映には数分かかる場合があります。"
echo "記事詳細ページが正しく動作することを確認してください。"