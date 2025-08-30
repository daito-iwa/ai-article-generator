#!/bin/bash

# 生成された記事を簡単に確認するスクリプト

echo "📄 生成された記事を確認"
echo "=" * 50

# 最新記事を探す
LATEST_ARTICLE=""

# 各ディレクトリをチェック
DIRS=(
    "output/demo"
    "output/auto_generated"
    "output/ollama_generated"
    "output/articles"
    "output/quick_generated"
)

echo "検索中..."
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        # 最新のmdファイルを探す
        latest=$(ls -t "$dir"/*.md 2>/dev/null | head -1)
        if [ -n "$latest" ]; then
            LATEST_ARTICLE="$latest"
            break
        fi
    fi
done

if [ -z "$LATEST_ARTICLE" ]; then
    echo "❌ 記事が見つかりません"
    echo ""
    echo "記事を生成するには:"
    echo "1) python3 generate_test_article.py"
    echo "2) python3 auto_article_generator.py --mode trending"
    echo "3) ./start_auto_generation.sh"
    exit 1
fi

echo "✅ 最新の記事: $LATEST_ARTICLE"
echo ""

# オプション選択
echo "どうしますか？"
echo "1) ブラウザで開く"
echo "2) ターミナルで表示"
echo "3) エディタで開く"
echo "4) すべての記事をリスト表示"
echo ""
read -p "選択 (1-4): " CHOICE

case $CHOICE in
    1)
        # HTMLに変換してブラウザで開く
        HTML_FILE="${LATEST_ARTICLE%.md}.html"
        
        # 簡易HTMLを生成
        cat > "$HTML_FILE" << EOF
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>$(basename "$LATEST_ARTICLE")</title>
    <style>
        body { 
            font-family: -apple-system, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            line-height: 1.6;
            background: #f5f5f5;
        }
        article {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #555; margin-top: 30px; }
        h3 { color: #666; }
        a { color: #3498db; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
    </style>
</head>
<body>
<article>
EOF
        
        # マークダウンを簡易HTMLに変換
        sed 's/^# \(.*\)/<h1>\1<\/h1>/' "$LATEST_ARTICLE" | \
        sed 's/^## \(.*\)/<h2>\1<\/h2>/' | \
        sed 's/^### \(.*\)/<h3>\1<\/h3>/' | \
        sed 's/^\*\*\(.*\)\*\*/<strong>\1<\/strong>/g' | \
        sed 's/\[^\([^]]*\)\](\([^)]*\))/<a href="\2">\1<\/a>/g' | \
        sed 's/^- \(.*\)/<li>\1<\/li>/' | \
        sed 's/^$/\<br\>/' >> "$HTML_FILE"
        
        echo "</article></body></html>" >> "$HTML_FILE"
        
        # ブラウザで開く
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$HTML_FILE"
        else
            xdg-open "$HTML_FILE" 2>/dev/null || echo "ブラウザで開けません: $HTML_FILE"
        fi
        ;;
        
    2)
        # ターミナルで表示
        echo ""
        echo "=" * 70
        cat "$LATEST_ARTICLE"
        echo "=" * 70
        ;;
        
    3)
        # エディタで開く
        if command -v code &> /dev/null; then
            code "$LATEST_ARTICLE"
        elif command -v vim &> /dev/null; then
            vim "$LATEST_ARTICLE"
        else
            nano "$LATEST_ARTICLE"
        fi
        ;;
        
    4)
        # すべての記事をリスト表示
        echo ""
        echo "📚 すべての生成記事:"
        echo "-" * 50
        
        for dir in "${DIRS[@]}"; do
            if [ -d "$dir" ] && [ "$(ls -A $dir/*.md 2>/dev/null)" ]; then
                echo ""
                echo "[$dir]"
                ls -lt "$dir"/*.md | head -10
            fi
        done
        ;;
        
    *)
        # デフォルトはブラウザで開く
        $0 1
        ;;
esac

echo ""
echo "💡 ヒント:"
echo "- 新しい記事を生成: python3 generate_test_article.py"
echo "- 複数記事を生成: ./start_auto_generation.sh"
echo "- Ollamaで生成: ./install_ollama.sh"