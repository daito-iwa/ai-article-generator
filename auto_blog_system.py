#!/usr/bin/env python3
"""
完全自動ブログシステム
毎日自動で記事を生成・投稿する統合システム
"""

import os
import sys
import json
import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import hashlib
from pathlib import Path

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from article_generator import ArticleGenerator, ArticleConfig
from keyword_research import KeywordResearcher
from seo_optimizer import SEOOptimizer

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_blog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoBlogDatabase:
    """ブログデータベース管理"""
    
    def __init__(self, db_path: str = "data/blog.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 記事テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                meta_description TEXT,
                keywords TEXT,
                status TEXT DEFAULT 'published',
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # カテゴリテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        
        # 統計テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                articles_generated INTEGER DEFAULT 0,
                total_views INTEGER DEFAULT 0,
                revenue REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_article(self, article_data: Dict) -> int:
        """記事を保存"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # スラッグ生成
        slug = self._generate_slug(article_data['title'])
        
        cursor.execute('''
            INSERT INTO articles (slug, title, content, meta_description, keywords)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            slug,
            article_data['title'],
            article_data['content'],
            article_data.get('meta_description', ''),
            json.dumps(article_data.get('keywords', []))
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return article_id
    
    def _generate_slug(self, title: str) -> str:
        """URLスラッグを生成"""
        # 簡易的なスラッグ生成（実際はもっと高度な処理が必要）
        slug = title.lower()
        slug = slug.replace(' ', '-')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')
        
        # ユニークにするためにタイムスタンプを追加
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{slug[:50]}-{timestamp}"
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict]:
        """最近の記事を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, slug, title, meta_description, created_at, views
            FROM articles
            WHERE status = 'published'
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row[0],
                'slug': row[1],
                'title': row[2],
                'meta_description': row[3],
                'created_at': row[4],
                'views': row[5]
            })
        
        conn.close()
        return articles
    
    def get_article_by_slug(self, slug: str) -> Optional[Dict]:
        """スラッグで記事を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles WHERE slug = ?
        ''', (slug,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'slug': row[1],
                'title': row[2],
                'content': row[3],
                'meta_description': row[4],
                'keywords': json.loads(row[5]) if row[5] else [],
                'status': row[6],
                'views': row[7],
                'created_at': row[8],
                'updated_at': row[9]
            }
        return None

class AutoBlogGenerator:
    """自動ブログ生成エンジン"""
    
    def __init__(self, config_path: str = "config/api_keys.json"):
        self.config = self._load_config(config_path)
        self.db = AutoBlogDatabase()
        
        # 各コンポーネント初期化
        self.article_generator = ArticleGenerator(
            openai_api_key=self.config.get('openai_api_key'),
            anthropic_api_key=self.config.get('anthropic_api_key')
        )
        self.keyword_researcher = KeywordResearcher()
        self.seo_optimizer = SEOOptimizer()
    
    def _load_config(self, config_path: str) -> Dict:
        """設定読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            logger.warning("設定ファイルが見つかりません")
            return {}
    
    def generate_daily_articles(self, count: int = 3):
        """毎日の記事を生成"""
        logger.info(f"日次記事生成開始: {count}記事")
        
        # トレンドキーワード取得
        keywords = self._get_trending_keywords(count * 2)  # 予備含めて多めに取得
        
        generated_count = 0
        for keyword in keywords[:count]:
            try:
                # 記事生成
                article = self._generate_single_article(keyword)
                
                if article:
                    # データベースに保存
                    article_id = self.db.save_article({
                        'title': article['title'],
                        'content': article['content'],
                        'meta_description': article['meta_description'],
                        'keywords': article['keywords']
                    })
                    
                    logger.info(f"記事保存成功: ID={article_id}, タイトル={article['title']}")
                    generated_count += 1
                    
                    # API制限対策
                    time.sleep(30)
                    
            except Exception as e:
                logger.error(f"記事生成エラー: {e}")
                continue
        
        # 統計更新
        self._update_statistics(generated_count)
        
        logger.info(f"日次記事生成完了: {generated_count}/{count}記事")
    
    def _get_trending_keywords(self, count: int) -> List[str]:
        """トレンドキーワード取得"""
        try:
            trending = self.keyword_researcher.get_trending_keywords(limit=count)
            return [kw.main_keyword for kw in trending]
        except:
            # フォールバックキーワード
            return [
                "AI 活用法",
                "副業 始め方",
                "投資 初心者",
                "ダイエット 方法",
                "プログラミング 学習"
            ][:count]
    
    def _generate_single_article(self, keyword: str) -> Optional[Dict]:
        """単一記事生成"""
        # デモ用の簡易実装
        content = f"""# {keyword}の完全ガイド

## はじめに

{keyword}について、初心者の方にも分かりやすく解説します。この記事では、{keyword}の基本から応用まで、実践的な内容をお届けします。

## {keyword}の基本

{keyword}を理解するためには、まず基本的な概念を押さえることが重要です。

### 1. {keyword}とは

{keyword}は、現代において非常に重要なトピックです。多くの人が関心を持っており、正しい知識を身につけることで大きなメリットを得られます。

### 2. なぜ{keyword}が重要なのか

- 効率性の向上
- コスト削減
- 生活の質の改善

## {keyword}の実践方法

### ステップ1: 準備

まず、{keyword}を始めるための準備を整えましょう。

### ステップ2: 実行

計画に基づいて実行します。

### ステップ3: 改善

結果を分析し、継続的に改善していきます。

## おすすめのツール

### エックスサーバー
{keyword}に関連するウェブサイトを運営するなら、高速で安定したサーバーが必要です。
[→ エックスサーバーの詳細](https://example.com/xserver)

### ラッコキーワード
{keyword}に関連するキーワードリサーチに便利です。
[→ ラッコキーワード](https://example.com/rakko)

## まとめ

{keyword}について解説しました。重要なポイントは以下の通りです：

1. 基本を理解する
2. 実践する
3. 継続的に改善する

ぜひ、今日から{keyword}を始めてみてください！
"""
        
        return {
            'title': f"{keyword}の完全ガイド - 初心者でも分かる実践方法",
            'content': content,
            'meta_description': f"{keyword}について初心者にも分かりやすく解説。基本から実践方法まで完全網羅。",
            'keywords': [keyword, f"{keyword} 初心者", f"{keyword} 方法"]
        }
    
    def _update_statistics(self, articles_count: int):
        """統計更新"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        
        cursor.execute('''
            INSERT OR REPLACE INTO statistics (date, articles_generated)
            VALUES (?, ?)
        ''', (today, articles_count))
        
        conn.commit()
        conn.close()

def create_blog_website():
    """ブログウェブサイトを生成"""
    from flask import Flask, render_template_string, abort
    
    app = Flask(__name__)
    db = AutoBlogDatabase()
    
    # ホームページテンプレート
    HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>AI自動生成ブログ</title>
    <style>
        body { font-family: sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: #333; color: white; padding: 20px; margin: -20px -20px 20px; }
        .article { background: #f9f9f9; padding: 20px; margin-bottom: 20px; border-radius: 10px; }
        .article h2 { margin-top: 0; }
        .meta { color: #666; font-size: 0.9em; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI自動生成ブログ</h1>
        <p>毎日新しい記事を自動生成・投稿しています</p>
    </div>
    
    <h2>最新記事</h2>
    {% for article in articles %}
    <div class="article">
        <h2><a href="/article/{{ article.slug }}">{{ article.title }}</a></h2>
        <p>{{ article.meta_description }}</p>
        <div class="meta">
            投稿日: {{ article.created_at }} | 閲覧数: {{ article.views }}
        </div>
    </div>
    {% endfor %}
</body>
</html>
    '''
    
    # 記事ページテンプレート
    ARTICLE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>{{ article.title }}</title>
    <meta name="description" content="{{ article.meta_description }}">
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
        h1 { color: #333; }
        .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
        .content { background: #f9f9f9; padding: 30px; border-radius: 10px; }
        .back { margin-top: 30px; }
    </style>
</head>
<body>
    <article>
        <h1>{{ article.title }}</h1>
        <div class="meta">投稿日: {{ article.created_at }}</div>
        <div class="content">
            {{ article.content | safe }}
        </div>
        <div class="back">
            <a href="/">← トップページに戻る</a>
        </div>
    </article>
    
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
</body>
</html>
    '''
    
    @app.route('/')
    def home():
        articles = db.get_recent_articles(20)
        return render_template_string(HOME_TEMPLATE, articles=articles)
    
    @app.route('/article/<slug>')
    def article(slug):
        article = db.get_article_by_slug(slug)
        if not article:
            abort(404)
        
        # Markdown to HTML変換（簡易版）
        content = article['content']
        content = content.replace('\n## ', '\n<h2>').replace('\n', '</h2>\n', 1)
        content = content.replace('\n### ', '\n<h3>').replace('\n', '</h3>\n', 1)
        content = content.replace('\n\n', '</p>\n<p>')
        content = f'<p>{content}</p>'
        article['content'] = content
        
        return render_template_string(ARTICLE_TEMPLATE, article=article)
    
    return app

# スケジューラー設定
def setup_scheduler():
    """自動投稿スケジューラーを設定"""
    generator = AutoBlogGenerator()
    
    # 毎日午前9時に3記事生成
    schedule.every().day.at("09:00").do(lambda: generator.generate_daily_articles(3))
    
    # 毎日午後3時に2記事生成
    schedule.every().day.at("15:00").do(lambda: generator.generate_daily_articles(2))
    
    # 毎日午後9時に1記事生成
    schedule.every().day.at("21:00").do(lambda: generator.generate_daily_articles(1))
    
    logger.info("スケジューラー設定完了")
    
    # スケジューラー実行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自動ブログシステム')
    parser.add_argument('--mode', choices=['web', 'generate', 'schedule'], default='web')
    parser.add_argument('--count', type=int, default=3, help='生成する記事数')
    
    args = parser.parse_args()
    
    if args.mode == 'generate':
        # 手動で記事生成
        generator = AutoBlogGenerator()
        generator.generate_daily_articles(args.count)
        
    elif args.mode == 'schedule':
        # スケジューラー起動
        print("🤖 自動投稿スケジューラーを起動します...")
        print("停止: Ctrl+C")
        setup_scheduler()
        
    else:  # web
        # Webサーバー起動
        try:
            from flask import Flask
        except ImportError:
            print("Flaskをインストールしています...")
            os.system("pip3 install --break-system-packages flask")
            from flask import Flask
        
        app = create_blog_website()
        print("🌐 自動ブログシステムを起動中...")
        print("📍 URL: http://localhost:5000")
        print("🤖 記事生成: python3 auto_blog_system.py --mode generate")
        print("⏰ 自動投稿: python3 auto_blog_system.py --mode schedule")
        app.run(debug=True, port=5000)