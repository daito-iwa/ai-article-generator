#!/bin/bash

# 自動記事生成スクリプト

echo "🤖 自動記事生成システム"
echo ""
echo "生成モードを選択してください:"
echo "1) キーワードファイルから生成（keywords.txt）"
echo "2) トレンドキーワードから自動生成"
echo "3) カスタムキーワードファイルから生成"
echo ""
read -p "選択 (1-3): " MODE

# APIキー設定チェック
if [ ! -f "config/api_keys.json" ]; then
    echo "❌ config/api_keys.json が見つかりません"
    echo "設定ファイルを作成してAPIキーを設定してください"
    exit 1
fi

# 実行
case $MODE in
    1)
        echo "📝 keywords.txt から記事を生成します..."
        python3 auto_article_generator.py --mode file --keywords-file keywords.txt
        ;;
    2)
        echo "🔥 トレンドキーワードから記事を生成します..."
        read -p "生成する記事数 (デフォルト: 5): " COUNT
        COUNT=${COUNT:-5}
        python3 auto_article_generator.py --mode trending --count $COUNT
        ;;
    3)
        read -p "キーワードファイルのパスを入力: " FILE
        if [ -f "$FILE" ]; then
            echo "📝 $FILE から記事を生成します..."
            python3 auto_article_generator.py --mode file --keywords-file "$FILE"
        else
            echo "❌ ファイルが見つかりません: $FILE"
            exit 1
        fi
        ;;
    *)
        echo "❌ 無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "✅ 処理完了！"
echo "生成された記事は output/auto_generated/ に保存されています"