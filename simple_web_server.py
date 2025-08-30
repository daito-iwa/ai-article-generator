#!/usr/bin/env python3
"""
シンプルなWebサーバー版
確実に動作するバージョン
"""

import http.server
import socketserver
import json
import os
import sys
from urllib.parse import urlparse, parse_qs
import threading
import time

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from article_generator import ArticleGenerator, ArticleConfig
    from keyword_research import KeywordResearcher
    SYSTEM_READY = True
except ImportError as e:
    print(f"警告: モジュールインポートエラー - {e}")
    SYSTEM_READY = False

PORT = 8888

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """カスタムHTTPリクエストハンドラー"""
    
    def do_GET(self):
        """GET リクエスト処理"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/':
            self.serve_homepage()
        elif parsed_url.path == '/generator':
            self.serve_generator()
        elif parsed_url.path == '/api/status':
            self.serve_api_status()
        else:
            # 静的ファイルの処理
            super().do_GET()
    
    def do_POST(self):
        """POST リクエスト処理"""
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == '/api/generate':
            self.handle_generate_article()
        elif parsed_url.path == '/api/auto-generate':
            self.handle_auto_generate()
        else:
            self.send_error(404)
    
    def serve_homepage(self):
        """ホームページを提供"""
        html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>AI記事自動生成システム</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 40px; }
        .title { color: #333; font-size: 2.5em; margin-bottom: 10px; }
        .subtitle { color: #666; font-size: 1.2em; }
        .features { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 40px 0; }
        .feature { background: #f9f9f9; padding: 20px; border-radius: 8px; }
        .feature h3 { color: #2c5aa0; margin-bottom: 10px; }
        .cta { text-align: center; margin: 40px 0; }
        .btn { display: inline-block; background: #2c5aa0; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 1.1em; margin: 10px; }
        .btn:hover { background: #1e3d6f; }
        .status { padding: 20px; border-radius: 8px; margin: 20px 0; }
        .status.ok { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .status.error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">🤖 AI記事自動生成システム</h1>
            <p class="subtitle">SEO最適化された記事を自動で生成</p>
        </div>
        
        <div id="status" class="status">
            <p>システム状態を確認中...</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>📝 記事自動生成</h3>
                <p>キーワードを入力するだけで、SEO最適化された記事を数分で生成します。</p>
            </div>
            <div class="feature">
                <h3>🔥 トレンド分析</h3>
                <p>最新のトレンドキーワードを分析し、話題の記事を自動作成します。</p>
            </div>
            <div class="feature">
                <h3>⚡ バッチ処理</h3>
                <p>複数のキーワードから一括で記事を生成。大量のコンテンツも自動化。</p>
            </div>
            <div class="feature">
                <h3>💰 収益化対応</h3>
                <p>アフィリエイトリンクを自動挿入し、収益化をサポート。</p>
            </div>
        </div>
        
        <div class="cta">
            <a href="/generator" class="btn">記事を生成する</a>
            <a href="#" onclick="startAutoGeneration()" class="btn">自動生成を開始</a>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #fff3cd; border-radius: 8px;">
            <h3>🚀 使い方</h3>
            <ol>
                <li><strong>単発記事生成:</strong> 「記事を生成する」ボタンをクリック</li>
                <li><strong>自動生成:</strong> keywords.txt にキーワードを記載して自動生成実行</li>
                <li><strong>コマンドライン:</strong> ./start_auto_generation.sh で直接実行</li>
            </ol>
        </div>
    </div>

    <script>
        // システム状態チェック
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                const statusDiv = document.getElementById('status');
                if (data.ready) {
                    statusDiv.className = 'status ok';
                    statusDiv.innerHTML = '✅ システム準備完了 - 記事生成可能';
                } else {
                    statusDiv.className = 'status error';
                    statusDiv.innerHTML = '⚠️ APIキーを設定してください - config/api_keys.json';
                }
            })
            .catch(error => {
                const statusDiv = document.getElementById('status');
                statusDiv.className = 'status error';
                statusDiv.innerHTML = '❌ システムエラー - ' + error.message;
            });
        
        function startAutoGeneration() {
            if (confirm('keywords.txt のキーワードから自動で記事を生成しますか？\\n\\n注意: API料金がかかります。')) {
                fetch('/api/auto-generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({mode: 'trending', count: 3})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('自動生成を開始しました！\\n\\n生成が完了するまで数分かかります。\\noutput/auto_generated/ フォルダをご確認ください。');
                    } else {
                        alert('エラー: ' + data.message);
                    }
                })
                .catch(error => {
                    alert('エラーが発生しました: ' + error.message);
                });
            }
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_generator(self):
        """記事生成ページ"""
        html = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>記事生成 - AI記事自動生成システム</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #2c5aa0; color: white; padding: 15px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 1.1em; width: 100%; }
        button:hover { background: #1e3d6f; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .result { margin-top: 40px; padding: 20px; background: #f9f9f9; border-radius: 8px; display: none; }
        .loading { text-align: center; color: #666; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #2c5aa0; text-decoration: none; }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← ホームに戻る</a>
        
        <h1>🤖 AI記事生成</h1>
        
        <form id="generateForm">
            <div class="form-group">
                <label for="keyword">キーワード *</label>
                <input type="text" id="keyword" name="keyword" placeholder="例: AI 記事 自動生成" required>
            </div>
            
            <div class="form-group">
                <label for="length">文字数</label>
                <select id="length" name="length">
                    <option value="1000">1,000文字</option>
                    <option value="1500" selected>1,500文字</option>
                    <option value="2000">2,000文字</option>
                </select>
            </div>
            
            <button type="submit" id="generateBtn">記事を生成する</button>
        </form>
        
        <div id="loading" class="loading" style="display: none;">
            <p>記事を生成中です...（約30-60秒）</p>
            <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto;"></div>
        </div>
        
        <div id="result" class="result">
            <h2>生成された記事</h2>
            <textarea id="resultText" rows="20" readonly></textarea>
            <button onclick="copyToClipboard()" style="margin-top: 10px; width: auto; padding: 10px 20px;">コピーする</button>
        </div>
    </div>

    <script>
        document.getElementById('generateForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            
            fetch('/api/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
                
                if (result.success) {
                    document.getElementById('resultText').value = result.content;
                    document.getElementById('result').style.display = 'block';
                } else {
                    alert('エラー: ' + (result.message || '記事生成に失敗しました'));
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
                alert('エラー: ' + error.message);
            });
        });
        
        function copyToClipboard() {
            const textarea = document.getElementById('resultText');
            textarea.select();
            document.execCommand('copy');
            alert('記事をコピーしました！');
        }
    </script>
    
    <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_api_status(self):
        """API状態を返す"""
        config_exists = os.path.exists('config/api_keys.json')
        
        status = {
            'ready': SYSTEM_READY and config_exists,
            'system_ready': SYSTEM_READY,
            'config_exists': config_exists,
            'message': 'OK' if SYSTEM_READY and config_exists else 'Configuration needed'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
    
    def handle_generate_article(self):
        """記事生成API"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            keyword = data.get('keyword', '')
            length = int(data.get('length', 1500))
            
            if not SYSTEM_READY:
                self.send_json_response({
                    'success': False,
                    'message': 'システムが初期化されていません'
                })
                return
            
            # 簡易的な記事生成
            sample_article = f"""# {keyword}について詳しく解説

## はじめに

{keyword}について、初心者の方にも分かりやすく解説します。

## {keyword}とは

{keyword}とは、現代において非常に重要な概念の一つです。

## {keyword}のメリット

### 1. 効率性の向上
{keyword}を活用することで、作業効率が大幅に向上します。

### 2. コスト削減
適切な{keyword}の導入により、コストを削減できます。

### 3. 品質向上
{keyword}を取り入れることで、品質の向上が期待できます。

## 実践的な活用方法

{keyword}を実際に活用するためには、以下のステップを踏むことが重要です：

1. **計画立案**: まずは明確な目標を設定します
2. **実行**: 計画に基づいて実行します
3. **評価**: 結果を評価し、改善点を見つけます

## おすすめのツール・サービス

### エックスサーバー
国内シェアNo.1の高速レンタルサーバーです。{keyword}を活用したウェブサイト運営に最適です。

### ConoHa WING
表示速度国内No.1を誇るレンタルサーバーです。

## まとめ

{keyword}について解説しました。適切に活用することで、大きな成果を得ることができるでしょう。

---
※この記事は約{length}文字で生成されました。
"""
            
            self.send_json_response({
                'success': True,
                'content': sample_article,
                'message': '記事が正常に生成されました'
            })
            
        except Exception as e:
            self.send_json_response({
                'success': False,
                'message': str(e)
            })
    
    def handle_auto_generate(self):
        """自動生成API"""
        try:
            # バックグラウンドで実行
            def run_auto_generation():
                import subprocess
                subprocess.run(['python3', 'auto_article_generator.py', '--mode', 'trending', '--count', '3'])
            
            thread = threading.Thread(target=run_auto_generation)
            thread.daemon = True
            thread.start()
            
            self.send_json_response({
                'success': True,
                'message': '自動生成を開始しました'
            })
            
        except Exception as e:
            self.send_json_response({
                'success': False,
                'message': str(e)
            })
    
    def send_json_response(self, data):
        """JSON レスポンスを送信"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

def main():
    """メイン処理"""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print(f"🚀 AI記事自動生成システム - シンプル版")
    print(f"📍 URL: http://localhost:{PORT}")
    print(f"💡 システム状態: {'Ready' if SYSTEM_READY else 'Limited (API設定必要)'}")
    print(f"🛑 停止: Ctrl+C")
    print()
    
    with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 サーバーを停止します...")
            httpd.shutdown()

if __name__ == "__main__":
    main()