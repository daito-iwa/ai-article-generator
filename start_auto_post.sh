#!/bin/bash

echo "🚀 ViralHub 自動投稿システム 2024"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ollamaが起動しているか確認
if ! pgrep -x "ollama" > /dev/null; then
    echo "📦 Ollamaを起動しています..."
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# llama3.2モデルがあるか確認
if ! ollama list | grep -q "llama3.2"; then
    echo "📥 llama3.2モデルをダウンロード中..."
    echo "（初回のみ・約2GB・5-10分かかります）"
    ollama pull llama3.2
fi

echo ""
echo "✅ 準備完了！"
echo ""
echo "🎯 新機能:"
echo "   ✨ 全ジャンル対応（エンタメ・ライフスタイル・ビジネス等）"
echo "   🕐 1日3回投稿（朝・昼・夜）"
echo "   🚀 SEOブーストモード（1日12記事）"
echo "   📊 月間90記事で検索上位獲得"
echo "   💰 完全無料（Ollama使用）"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 仮想環境があれば有効化
if [ -d "venv" ]; then
    echo "🐍 仮想環境を有効化中..."
    source venv/bin/activate
fi

# 自動投稿を開始
python3 auto_post_ollama.py