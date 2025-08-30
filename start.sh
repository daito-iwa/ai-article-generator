#!/bin/bash

# AI記事生成システム起動スクリプト

echo "🚀 AI記事生成システムを起動します..."

# 起動モード選択
echo ""
echo "起動モードを選択してください:"
echo "1) アフィリエイト収益モデル（完全無料版）"
echo "2) 有料プランモデル（課金版）"
echo ""
read -p "選択 (1 or 2): " MODE

# APIキー設定チェック
if [ ! -f "config/api_keys.json" ]; then
    echo "❌ config/api_keys.json が見つかりません"
    echo "設定ファイルを作成してAPIキーを設定してください"
    exit 1
fi

# 必要なディレクトリを作成
mkdir -p data output logs static templates

# 依存関係のインストール
echo "📦 依存関係をインストール中..."
pip install --break-system-packages fastapi uvicorn jinja2 python-multipart

# 選択されたモードで起動
if [ "$MODE" = "1" ]; then
    echo "💰 アフィリエイト収益モデルで起動中..."
    echo "URL: http://localhost:8888"
    echo "停止: Ctrl+C"
    python3 web_app_affiliate.py
else
    echo "💳 有料プランモデルで起動中..."
    echo "URL: http://localhost:8888"
    echo "停止: Ctrl+C"
    python3 web_app.py
fi