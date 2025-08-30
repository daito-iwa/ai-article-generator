#!/usr/bin/env python3
"""
静的HTMLブログを生成
サーバー不要で、ファイルを開くだけで閲覧可能
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

class StaticBlogGenerator:
    """静的ブログ生成器"""
    
    def __init__(self):
        self.output_dir = "my_blog"
        self.articles_dir = os.path.join(self.output_dir, "articles")
        os.makedirs(self.articles_dir, exist_ok=True)
    
    def generate_blog(self):
        """ブログ全体を生成"""
        print("🌐 静的ブログを生成中...")
        
        # 既存の記事を収集
        articles = self.collect_articles()
        
        # CSSファイル生成
        self.create_css()
        
        # 各記事のHTMLページを生成
        for article in articles:
            self.create_article_page(article)
        
        # トップページ生成
        self.create_index_page(articles)
        
        # 完了メッセージ
        index_path = os.path.abspath(os.path.join(self.output_dir, "index.html"))
        print(f"\n✅ ブログ生成完了！")
        print(f"📁 保存場所: {self.output_dir}/")
        print(f"🌐 ブラウザで開く: file://{index_path}")
        
        # 自動で開く
        import webbrowser
        webbrowser.open(f'file://{index_path}')
    
    def collect_articles(self):
        """既存の記事を収集"""
        articles = []
        
        # 各出力ディレクトリから記事を収集
        directories = [
            'output/demo',
            'output/auto_generated',
            'output/ollama_generated',
            'output/articles'
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    if file.endswith('.md'):
                        filepath = os.path.join(directory, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # タイトル抽出
                        lines = content.split('\n')
                        title = "無題の記事"
                        for line in lines:
                            if line.startswith('# '):
                                title = line[2:].strip()
                                break
                        
                        # スラッグ生成
                        slug = file.replace('.md', '')
                        
                        articles.append({
                            'title': title,
                            'content': content,
                            'slug': slug,
                            'date': datetime.fromtimestamp(os.path.getmtime(filepath)),
                            'original_path': filepath
                        })
        
        # 日付でソート（新しい順）
        articles.sort(key=lambda x: x['date'], reverse=True)
        
        # デモ記事がない場合は作成
        if not articles:
            demo_articles = self.create_demo_articles()
            articles.extend(demo_articles)
        
        return articles
    
    def create_demo_articles(self):
        """デモ記事を作成"""
        demo_articles = [
            {
                'title': 'AIブログ自動生成システムの使い方',
                'slug': 'how-to-use-ai-blog',
                'date': datetime.now(),
                'content': '''# AIブログ自動生成システムの使い方

このブログは、AIによって自動生成された記事を表示しています。

## 特徴

- 完全自動で記事生成
- SEO最適化済み
- アフィリエイトリンク自動挿入

## 収益化の仕組み

### 1. アフィリエイト収益
記事内に自然にアフィリエイトリンクを配置し、クリックや購入で収益を得ます。

### 2. Google AdSense
ページビューに応じて広告収益を獲得できます。

## おすすめのレンタルサーバー

### エックスサーバー
国内シェアNo.1の高速レンタルサーバー。安定性が抜群です。
[→ エックスサーバーの詳細はこちら](https://px.a8.net/svt/ejp?a8mat=XXX)

### ConoHa WING
表示速度国内最速のレンタルサーバー。初心者にも優しい管理画面。
[→ ConoHa WINGの詳細はこちら](https://px.a8.net/svt/ejp?a8mat=YYY)

## まとめ

AIブログシステムを使えば、誰でも簡単に収益化可能なブログを運営できます！'''
            },
            {
                'title': '副業で月10万円稼ぐ方法',
                'slug': 'side-business-guide',
                'date': datetime.now(),
                'content': '''# 副業で月10万円稼ぐ方法

副業で安定した収入を得る方法を解説します。

## おすすめの副業

1. **ブログ運営**
   - 初期投資が少ない
   - 在宅で可能
   - 不労所得化できる

2. **プログラミング**
   - 高単価案件が多い
   - スキルが資産になる

3. **投資**
   - 資産運用で増やす
   - 長期的な視点が重要

## 成功のコツ

- 継続することが最重要
- 小さく始めて大きく育てる
- 複数の収入源を持つ

## まとめ

副業は誰でも始められます。まずは行動することが大切です！'''
            }
        ]
        
        return demo_articles
    
    def create_css(self):
        """CSSファイルを作成"""
        css_content = '''
/* ブログスタイル */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

/* ヘッダー */
.header {
    background: #2c3e50;
    color: white;
    padding: 30px 0;
    margin-bottom: 40px;
    text-align: center;
}

.header h1 {
    font-size: 2.5em;
    margin-bottom: 10px;
}

.header p {
    font-size: 1.2em;
    opacity: 0.9;
}

/* 記事一覧 */
.article-list {
    display: grid;
    gap: 30px;
}

.article-card {
    background: white;
    padding: 30px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

.article-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.15);
}

.article-card h2 {
    margin-bottom: 15px;
    font-size: 1.8em;
}

.article-card h2 a {
    color: #2c3e50;
    text-decoration: none;
}

.article-card h2 a:hover {
    color: #3498db;
}

.article-meta {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 15px;
}

.article-excerpt {
    color: #555;
    line-height: 1.8;
}

.read-more {
    display: inline-block;
    margin-top: 15px;
    color: #3498db;
    text-decoration: none;
    font-weight: bold;
}

.read-more:hover {
    text-decoration: underline;
}

/* 記事ページ */
.article {
    background: white;
    padding: 40px;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    max-width: 800px;
    margin: 0 auto;
}

.article h1 {
    font-size: 2.5em;
    margin-bottom: 20px;
    color: #2c3e50;
}

.article h2 {
    font-size: 1.8em;
    margin: 30px 0 15px;
    color: #34495e;
}

.article h3 {
    font-size: 1.4em;
    margin: 20px 0 10px;
    color: #34495e;
}

.article p {
    margin-bottom: 20px;
    line-height: 1.8;
}

.article a {
    color: #3498db;
    text-decoration: none;
}

.article a:hover {
    text-decoration: underline;
}

.article ul, .article ol {
    margin: 20px 0;
    padding-left: 30px;
}

.article li {
    margin-bottom: 10px;
}

/* 広告エリア */
.ad-container {
    background: #f9f9f9;
    border: 2px dashed #ddd;
    padding: 20px;
    margin: 30px 0;
    text-align: center;
    border-radius: 5px;
}

.ad-container p {
    color: #999;
    font-size: 0.9em;
}

/* フッター */
.footer {
    background: #34495e;
    color: white;
    text-align: center;
    padding: 30px 0;
    margin-top: 60px;
}

.footer p {
    opacity: 0.8;
}

/* レスポンシブ */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .header h1 {
        font-size: 2em;
    }
    
    .article {
        padding: 20px;
    }
    
    .article h1 {
        font-size: 2em;
    }
}
'''
        
        css_path = os.path.join(self.output_dir, 'style.css')
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def create_index_page(self, articles):
        """トップページを作成"""
        html = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI自動生成ブログ</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>AI自動生成ブログ</h1>
            <p>毎日新しい記事を自動生成・投稿しています</p>
        </div>
    </header>
    
    <main class="container">
        <div class="article-list">
'''
        
        # 記事カード生成
        for article in articles[:20]:  # 最新20記事
            date_str = article['date'].strftime('%Y年%m月%d日')
            excerpt = self.get_excerpt(article['content'])
            
            html += f'''
            <article class="article-card">
                <h2><a href="articles/{article['slug']}.html">{article['title']}</a></h2>
                <div class="article-meta">投稿日: {date_str}</div>
                <div class="article-excerpt">{excerpt}</div>
                <a href="articles/{article['slug']}.html" class="read-more">続きを読む →</a>
            </article>
'''
        
        html += '''
        </div>
        
        <div class="ad-container">
            <p>広告スペース - Google AdSenseなどを配置</p>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 AI自動生成ブログ. Powered by AI Article Generator</p>
        </div>
    </footer>
</body>
</html>'''
        
        index_path = os.path.join(self.output_dir, 'index.html')
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def create_article_page(self, article):
        """個別記事ページを作成"""
        # Markdownを簡易HTMLに変換
        content_html = self.markdown_to_html(article['content'])
        date_str = article['date'].strftime('%Y年%m月%d日')
        
        html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - AI自動生成ブログ</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1><a href="../index.html" style="color: white; text-decoration: none;">AI自動生成ブログ</a></h1>
            <p>毎日新しい記事を自動生成・投稿しています</p>
        </div>
    </header>
    
    <main class="container">
        <article class="article">
            <h1>{article['title']}</h1>
            <div class="article-meta">投稿日: {date_str}</div>
            
            <div class="ad-container">
                <p>広告スペース - 記事上部</p>
            </div>
            
            {content_html}
            
            <div class="ad-container">
                <p>広告スペース - 記事下部</p>
            </div>
        </article>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="../index.html" style="color: #3498db; text-decoration: none; font-weight: bold;">← トップページに戻る</a>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 AI自動生成ブログ. Powered by AI Article Generator</p>
        </div>
    </footer>
</body>
</html>'''
        
        article_path = os.path.join(self.articles_dir, f"{article['slug']}.html")
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def markdown_to_html(self, markdown):
        """簡易Markdown→HTML変換"""
        html = markdown
        
        # 見出し
        html = html.replace('\n### ', '\n<h3>').replace('</h3>\n### ', '</h3>\n<h3>')
        html = html.replace('\n## ', '\n<h2>').replace('</h2>\n## ', '</h2>\n<h2>')
        html = html.replace('\n# ', '\n<h1>').replace('</h1>\n# ', '</h1>\n<h1>')
        
        # リンク
        import re
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # 太字
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # 段落
        paragraphs = html.split('\n\n')
        html = ''
        for para in paragraphs:
            if para.strip():
                if not para.strip().startswith('<h'):
                    html += f'<p>{para}</p>\n'
                else:
                    html += para + '\n'
        
        return html
    
    def get_excerpt(self, content, length=150):
        """記事の抜粋を取得"""
        # 最初の段落を取得
        lines = content.split('\n')
        excerpt = ''
        
        for line in lines:
            if line.strip() and not line.startswith('#'):
                excerpt = line.strip()
                break
        
        if len(excerpt) > length:
            excerpt = excerpt[:length] + '...'
        
        return excerpt

def main():
    """メイン処理"""
    print("🌐 静的ブログ生成システム")
    print("=" * 50)
    
    generator = StaticBlogGenerator()
    generator.generate_blog()
    
    print("\n💡 使い方:")
    print("1. my_blog/index.html をブラウザで開く")
    print("2. 記事を追加: python3 generate_test_article.py")
    print("3. ブログ再生成: python3 create_static_blog.py")
    print("\n📱 スマホでも閲覧可能です！")

if __name__ == "__main__":
    main()