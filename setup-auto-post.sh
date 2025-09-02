#!/bin/bash

echo "🚀 ViralHub 自動投稿セットアップ開始"
echo "=================================="

# 現在のディレクトリを確認
echo "📂 現在のディレクトリ: $(pwd)"

# Gitリポジトリを初期化
echo ""
echo "1️⃣ Gitリポジトリを初期化..."
git init

# .gitignoreを作成
echo ""
echo "2️⃣ .gitignoreファイルを作成..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
auto_post_ollama.log

# Temporary
*.tmp
*.bak
EOF

echo "✅ .gitignore作成完了"

# 全ファイルをステージング
echo ""
echo "3️⃣ ファイルをGitに追加..."
git add .

# 初回コミット
echo ""
echo "4️⃣ 初回コミットを作成..."
git commit -m "🎉 ViralHub 完全自動投稿システム初期化

- GitHub Actions自動投稿システム実装
- 1日3回（朝・昼・夜）自動投稿
- 全ジャンル対応（エンタメ・ライフスタイル・ビジネス等）
- SEO最適化機能
- 投稿フォーム実装
- 完全無料運営（GitHub Pages + 無料AI）"

echo ""
echo "✅ ローカルリポジトリの準備完了！"
echo ""
echo "=================================="
echo "📋 次のステップ："
echo ""
echo "1. GitHubで新しいリポジトリを作成"
echo "   - リポジトリ名: ai-article-generator"
echo "   - Public（公開）を選択"
echo "   - READMEやライセンスは追加しない"
echo ""
echo "2. GitHubリポジトリのURLをコピー"
echo "   例: https://github.com/yourusername/ai-article-generator.git"
echo ""
echo "3. 以下のコマンドを実行してプッシュ:"
echo "   git remote add origin [GitHubリポジトリのURL]"
echo "   git push -u origin main"
echo ""
echo "4. GitHubでActionsを有効化"
echo "   - リポジトリのActionsタブへ"
echo "   - 「I understand my workflows, enable them」をクリック"
echo ""
echo "5. GitHub Pagesを有効化"
echo "   - Settings → Pages"
echo "   - Source: Deploy from a branch"
echo "   - Branch: main / (root)"
echo ""
echo "🎉 これで完全自動投稿が開始されます！"