#!/bin/bash

# 簡単ブログ起動スクリプト

echo "🚀 AIブログシステム"
echo "=" * 30

echo "どの方法でブログを確認しますか？"
echo ""
echo "1) 静的ブログ（推奨） - サーバー不要"
echo "2) 記事ファイルを直接確認"
echo "3) 新しい記事を3つ生成してからブログ作成"
echo "4) Ollama版で記事を生成してブログ作成"
echo ""
read -p "選択 (1-4): " CHOICE

case $CHOICE in
    1)
        echo "📄 静的ブログを生成中..."
        python3 create_static_blog.py
        ;;
    2)
        echo "📁 記事フォルダを開きます..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open output/
        else
            echo "記事の場所: output/"
            ls -la output/*/
        fi
        ;;
    3)
        echo "📝 新しい記事を3つ生成中..."
        python3 generate_test_article.py
        sleep 2
        python3 auto_article_generator.py --mode trending --count 2 || echo "トレンド生成をスキップ"
        echo "🌐 ブログを生成中..."
        python3 create_static_blog.py
        ;;
    4)
        echo "🤖 Ollamaで記事を生成してみます..."
        python3 ollama_article_generator.py --count 2 || echo "Ollama記事生成をスキップ（設定が必要）"
        echo "📝 デモ記事も生成..."
        python3 generate_test_article.py
        echo "🌐 ブログを生成中..."
        python3 create_static_blog.py
        ;;
    *)
        echo "デフォルト: 静的ブログを生成します"
        python3 create_static_blog.py
        ;;
esac

echo ""
echo "🎉 完了！"
echo ""
echo "📂 ファイルの確認:"
echo "   Finder: open my_blog/"
echo ""
echo "🌐 ブラウザで確認:"
echo "   my_blog/index.html をダブルクリック"
echo ""
echo "💡 追加の記事生成:"
echo "   python3 generate_test_article.py"
echo "   python3 create_static_blog.py  # ブログ更新"