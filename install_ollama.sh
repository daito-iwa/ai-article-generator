#!/bin/bash

# Ollama簡単インストール & 記事生成スクリプト

echo "🤖 Ollama AI記事生成システム - セットアップ"
echo "=" * 50

# OS検出
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "📱 macOSを検出しました"
    
    # Ollamaがインストールされているか確認
    if ! command -v ollama &> /dev/null; then
        echo "📦 Ollamaをインストールします..."
        
        # Homebrewがあるか確認
        if command -v brew &> /dev/null; then
            echo "Homebrewでインストール中..."
            brew install ollama
        else
            echo "Homebrewがありません。公式サイトからダウンロードしてください："
            echo "https://ollama.ai/download"
            open "https://ollama.ai/download"
            exit 1
        fi
    else
        echo "✅ Ollamaは既にインストールされています"
    fi
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "🐧 Linuxを検出しました"
    
    if ! command -v ollama &> /dev/null; then
        echo "📦 Ollamaをインストールします..."
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo "✅ Ollamaは既にインストールされています"
    fi
else
    echo "❌ サポートされていないOS: $OSTYPE"
    exit 1
fi

# Ollamaを起動
echo ""
echo "🚀 Ollamaを起動します..."
ollama serve &
OLLAMA_PID=$!

# 少し待つ
sleep 3

# 利用可能なモデルを確認
echo ""
echo "📋 利用可能なモデル:"
ollama list

# おすすめモデルの選択
echo ""
echo "どのモデルを使用しますか？"
echo "1) llama3.2 (3.8GB) - 最新・高速・推奨"
echo "2) mistral (4.1GB) - バランス良好"
echo "3) gemma2:2b (1.6GB) - 軽量・高速"
echo "4) phi3 (2.3GB) - Microsoft製・軽量"
echo ""
read -p "選択 (1-4): " MODEL_CHOICE

case $MODEL_CHOICE in
    1) MODEL="llama3.2";;
    2) MODEL="mistral";;
    3) MODEL="gemma2:2b";;
    4) MODEL="phi3";;
    *) MODEL="llama3.2";;
esac

# モデルをダウンロード
echo ""
echo "📥 $MODEL モデルをダウンロード中..."
ollama pull $MODEL

# 記事生成の実行
echo ""
echo "✨ 準備完了！記事を生成します"
echo ""
echo "生成方法を選択:"
echo "1) テスト記事を1つ生成"
echo "2) キーワードを入力して生成"
echo "3) 5つのトレンド記事を自動生成"
echo ""
read -p "選択 (1-3): " GEN_CHOICE

case $GEN_CHOICE in
    1)
        python3 ollama_article_generator.py --model $MODEL --keyword "AI ブログ 収益化"
        ;;
    2)
        read -p "キーワードを入力: " KEYWORD
        python3 ollama_article_generator.py --model $MODEL --keyword "$KEYWORD"
        ;;
    3)
        python3 ollama_article_generator.py --model $MODEL --count 5
        ;;
    *)
        python3 ollama_article_generator.py --model $MODEL --keyword "Ollama 活用法"
        ;;
esac

echo ""
echo "🎉 完了！"
echo "📁 生成された記事: output/ollama_generated/"
echo ""
echo "💡 次回は以下のコマンドで直接実行できます:"
echo "   python3 ollama_article_generator.py --keyword \"キーワード\""

# Ollamaプロセスの情報を表示
echo ""
echo "⚠️  Ollamaは起動したままです (PID: $OLLAMA_PID)"
echo "   停止する場合: kill $OLLAMA_PID"