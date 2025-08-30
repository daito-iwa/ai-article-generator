#!/bin/bash

# 自動ブログシステムのデプロイスクリプト

echo "🚀 自動ブログシステム セットアップ"
echo "================================"

# 1. 必要なディレクトリ作成
echo "📁 ディレクトリ作成中..."
mkdir -p data logs output/blog static/images templates

# 2. 依存関係インストール
echo "📦 必要なパッケージをインストール中..."
pip3 install --break-system-packages flask schedule

# 3. 初回記事生成
echo "📝 初回記事を生成中..."
python3 auto_blog_system.py --mode generate --count 5

# 4. システム起動方法の表示
echo ""
echo "✅ セットアップ完了！"
echo ""
echo "🌐 ブログサイトを起動:"
echo "   python3 auto_blog_system.py --mode web"
echo "   → http://localhost:5000 でアクセス"
echo ""
echo "⏰ 自動投稿を開始:"
echo "   python3 auto_blog_system.py --mode schedule"
echo "   → 毎日9時、15時、21時に自動投稿"
echo ""
echo "📝 手動で記事生成:"
echo "   python3 auto_blog_system.py --mode generate --count 3"
echo ""

# 5. systemdサービスファイル作成（Linux用）
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Systemdサービスファイルを作成しますか？ (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        cat > auto_blog.service << EOF
[Unit]
Description=Auto Blog Generator Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 $(pwd)/auto_blog_system.py --mode schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        echo "サービスファイルを作成しました: auto_blog.service"
        echo "インストール方法:"
        echo "  sudo cp auto_blog.service /etc/systemd/system/"
        echo "  sudo systemctl enable auto_blog"
        echo "  sudo systemctl start auto_blog"
    fi
fi

# 6. cron設定（macOS/Linux共通）
echo ""
echo "📅 cronで自動起動を設定しますか？ (y/n)"
read -r response
if [[ "$response" == "y" ]]; then
    # 現在のcrontabを取得
    crontab -l > mycron 2>/dev/null || true
    
    # 新しいジョブを追加
    echo "0 9,15,21 * * * cd $(pwd) && /usr/bin/python3 auto_blog_system.py --mode generate --count 2" >> mycron
    
    # crontabを更新
    crontab mycron
    rm mycron
    
    echo "✅ cronジョブを設定しました（9時、15時、21時に実行）"
fi

echo ""
echo "🎉 すべての設定が完了しました！"