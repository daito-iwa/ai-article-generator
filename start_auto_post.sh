#!/bin/bash

echo "🤖 Ollama自動投稿システムを起動します..."
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
echo "🚀 自動投稿を開始します"
echo "   - 3時間ごとに自動投稿"
echo "   - 完全無料（Ollama使用）"
echo "   - 停止: Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 仮想環境があれば有効化
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 自動投稿を開始
python3 auto_post_ollama.py