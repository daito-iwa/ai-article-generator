#!/usr/bin/env python3
"""
生成された記事を簡単に閲覧できるWebサーバー
"""

import os
import glob
import http.server
import socketserver
from urllib.parse import urlparse, unquote
import markdown

PORT = 8888

class ArticleViewerHandler(http.server.SimpleHTTPRequestHandler):
    """記事ビューアーのハンドラー"""
    
    def do_GET(self):
        """GETリクエスト処理"""
        parsed_url = urlparse(self.path)
        path = unquote(parsed_url.path)
        
        if path == '/':
            self.serve_article_list()
        elif path.startswith('/view/'):
            # 記事を表示
            article_path = path[6:]  # /view/ を削除
            self.serve_article(article_path)
        else:
            super().do_GET()
    
    def serve_article_list(self):
        """記事一覧を表示"""
        # すべての生成された記事を検索
        articles = []
        
        # 各出力ディレクトリから記事を収集
        directories = [
            'output/demo',
            'output/auto_generated', 
            'output/ollama_generated',
            'output/articles',
            'output/quick_generated'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                md_files = glob.glob(f"{directory}/*.md")
                for file in md_files:
                    # ファイル情報を取得
                    stat = os.stat(file)
                    articles.append({
                        'path': file,
                        'name': os.path.basename(file),
                        'size': stat.st_size,
                        'modified': stat.st_mtime,
                        'directory': directory
                    })
        
        # 更新日時でソート（新しい順）
        articles.sort(key=lambda x: x['modified'], reverse=True)
        
        # HTML生成
        html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>AI生成記事ビューアー</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; 
            margin: 0;
            padding: 0;
            background: #f5f5f5;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 0 20px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        .article-list {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .article-item {
            padding: 20px;
            border-bottom: 1px solid #ecf0f1;
            transition: background 0.2s;
        }
        .article-item:hover {
            background: #f8f9fa;
        }
        .article-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
            text-decoration: none;
            display: block;
            margin-bottom: 5px;
        }
        .article-title:hover {
            color: #3498db;
        }
        .article-meta {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .article-path {
            color: #95a5a6;
            font-size: 0.8em;
            margin-top: 5px;
        }
        .no-articles {
            text-align: center;
            padding: 50px;
            color: #7f8c8d;
        }
        .quick-actions {
            background: #e8f4f8;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .action-button {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            margin: 5px;
        }
        .action-button:hover {
            background: #2980b9;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI生成記事ビューアー</h1>
        <p>生成されたすべての記事を閲覧・管理</p>
    </div>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{total_articles}</div>
                <div class="stat-label">総記事数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_words}</div>
                <div class="stat-label">総文字数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{today_articles}</div>
                <div class="stat-label">本日の記事</div>
            </div>
        </div>
        
        <div class="quick-actions">
            <h3>🚀 クイックアクション</h3>
            <a href="#" onclick="generateNew()" class="action-button">新規記事を生成</a>
            <a href="#" onclick="generateTrending()" class="action-button">トレンド記事を生成</a>
            <a href="#" onclick="generateOllama()" class="action-button">Ollamaで生成</a>
        </div>
        
        {article_html}
    </div>
    
    <script>
        function generateNew() {
            const keyword = prompt('生成したいキーワードを入力してください:');
            if (keyword) {
                alert('記事生成を開始します: ' + keyword + '\\n\\nターミナルで以下を実行:\\npython3 auto_article_generator.py --mode file --keywords-file <(echo "' + keyword + '")');
            }
        }
        
        function generateTrending() {
            alert('トレンド記事を生成します\\n\\nターミナルで以下を実行:\\npython3 auto_article_generator.py --mode trending --count 5');
        }
        
        function generateOllama() {
            alert('Ollamaで記事を生成します\\n\\nターミナルで以下を実行:\\npython3 ollama_article_generator.py --count 3');
        }
    </script>
</body>
</html>
        """
        
        # 記事リストHTML生成
        if articles:
            article_html = '<div class="article-list">'
            for article in articles:
                from datetime import datetime
                modified_date = datetime.fromtimestamp(article['modified']).strftime('%Y年%m月%d日 %H:%M')
                size_kb = article['size'] / 1024
                
                article_html += f'''
                <div class="article-item">
                    <a href="/view/{article['path']}" class="article-title">{article['name']}</a>
                    <div class="article-meta">
                        {modified_date} | {size_kb:.1f}KB | {article['directory']}/
                    </div>
                    <div class="article-path">{article['path']}</div>
                </div>
                '''
            article_html += '</div>'
        else:
            article_html = '<div class="no-articles">まだ記事が生成されていません</div>'
        
        # 統計情報を計算
        total_articles = len(articles)
        total_words = sum(article['size'] for article in articles) // 3  # 概算
        
        from datetime import datetime, timedelta
        today = datetime.now().date()
        today_articles = sum(1 for article in articles 
                           if datetime.fromtimestamp(article['modified']).date() == today)
        
        # HTMLを完成
        html = html.format(
            total_articles=total_articles,
            total_words=f"{total_words:,}",
            today_articles=today_articles,
            article_html=article_html
        )
        
        # レスポンス送信
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_article(self, article_path):
        """個別記事を表示"""
        if not os.path.exists(article_path) or not article_path.endswith('.md'):
            self.send_error(404)
            return
        
        # マークダウンファイルを読み込み
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            self.send_error(500)
            return
        
        # マークダウンをHTMLに変換
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(content)
        
        # HTML生成
        html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(article_path)}</title>
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .article {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3 {{ color: #2c3e50; }}
        h1 {{ border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ margin-top: 30px; }}
        a {{ color: #3498db; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; color: #666; }}
        .back-link {{ 
            display: inline-block; 
            margin-bottom: 20px; 
            color: #3498db; 
            text-decoration: none;
        }}
        .back-link:hover {{ text-decoration: underline; }}
        .actions {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
        }}
        .action-btn {{
            display: inline-block;
            margin: 0 10px;
            padding: 8px 16px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .action-btn:hover {{ background: #2980b9; }}
    </style>
</head>
<body>
    <a href="/" class="back-link">← 記事一覧に戻る</a>
    
    <div class="article">
        {html_content}
        
        <div class="actions">
            <a href="#" onclick="copyToClipboard()" class="action-btn">📋 コピー</a>
            <a href="{article_path}" download class="action-btn">💾 ダウンロード</a>
            <a href="#" onclick="window.print()" class="action-btn">🖨️ 印刷</a>
        </div>
    </div>
    
    <script>
        function copyToClipboard() {{
            const content = document.querySelector('.article').innerText;
            navigator.clipboard.writeText(content).then(() => {{
                alert('記事をクリップボードにコピーしました！');
            }});
        }}
    </script>
</body>
</html>
        """
        
        # レスポンス送信
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

def main():
    """メイン処理"""
    print("🌐 AI記事ビューアーを起動中...")
    print(f"📍 URL: http://localhost:{PORT}")
    print("🛑 停止: Ctrl+C")
    print()
    
    # markdownライブラリチェック
    try:
        import markdown
    except ImportError:
        print("⚠️  markdownライブラリをインストールしています...")
        os.system("pip install --break-system-packages markdown")
        import markdown
    
    # サーバー起動
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), ArticleViewerHandler) as httpd:
        try:
            # ブラウザを自動で開く
            import webbrowser
            import threading
            def open_browser():
                import time
                time.sleep(1)
                webbrowser.open(f'http://localhost:{PORT}')
            
            thread = threading.Thread(target=open_browser)
            thread.daemon = True
            thread.start()
            
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 サーバーを停止します...")
            httpd.shutdown()

if __name__ == "__main__":
    main()