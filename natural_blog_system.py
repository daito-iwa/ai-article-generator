#!/usr/bin/env python3
"""
自然なブログシステム
バックグラウンド: AI自動生成
フロントエンド: 普通の人が書いたブログに見える
"""

import os
import sys
import json
import random
import sqlite3
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class NaturalBlogConfig:
    """自然なブログ設定"""
    
    # ブログの人格設定
    BLOG_PERSONAS = {
        "tech_blogger": {
            "name": "山田太郎",
            "bio": "フリーランスエンジニア。プログラミングとAI技術に興味があります。",
            "avatar": "/images/avatar-tech.jpg",
            "writing_style": "technical",
            "categories": ["プログラミング", "AI", "副業", "技術解説"],
            "tone": "professional"
        },
        "lifestyle_blogger": {
            "name": "田中花子",
            "bio": "2児の母。ライフハック、投資、育児について発信しています。",
            "avatar": "/images/avatar-lifestyle.jpg", 
            "writing_style": "friendly",
            "categories": ["ライフスタイル", "投資", "育児", "節約"],
            "tone": "friendly"
        },
        "business_blogger": {
            "name": "佐藤次郎",
            "bio": "起業家・投資家。ビジネスと投資の実体験をシェアします。",
            "avatar": "/images/avatar-business.jpg",
            "writing_style": "authoritative", 
            "categories": ["ビジネス", "起業", "投資", "マーケティング"],
            "tone": "professional"
        }
    }
    
    # 自然な投稿パターン
    POSTING_PATTERNS = [
        {"time": "07:30", "probability": 0.3},  # 朝の投稿
        {"time": "12:00", "probability": 0.2},  # 昼休み投稿
        {"time": "19:00", "probability": 0.4},  # 夜の投稿
        {"time": "22:30", "probability": 0.3},  # 夜更かし投稿
    ]
    
    # 人間らしい要素
    HUMAN_ELEMENTS = [
        "今日は忙しくて更新が遅くなりました💦",
        "コーヒーを飲みながら書いています☕",
        "読者の皆様、いつもありがとうございます！",
        "最近話題の〇〇について調べてみました",
        "実体験を元に書きました",
        "長文になってしまいました😅",
        "参考になれば嬉しいです！",
        "また質問があればコメントください"
    ]

class NaturalBlogDatabase:
    """自然なブログのデータベース"""
    
    def __init__(self, db_path: str = "data/natural_blog.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """データベース初期化"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 記事テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS natural_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                author_name TEXT,
                author_bio TEXT,
                category TEXT,
                tags TEXT,
                featured_image TEXT,
                published_at TIMESTAMP,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                comments_count INTEGER DEFAULT 0,
                reading_time INTEGER,
                is_featured BOOLEAN DEFAULT FALSE,
                meta_title TEXT,
                meta_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # コメントテーブル（ダミーコメント用）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dummy_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                author_name TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES natural_articles (id)
            )
        ''')
        
        # カテゴリテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

class NaturalContentProcessor:
    """コンテンツを自然に見せる処理"""
    
    def __init__(self, persona_key: str = "tech_blogger"):
        self.persona = NaturalBlogConfig.BLOG_PERSONAS[persona_key]
    
    def humanize_content(self, raw_content: str, keyword: str) -> Dict:
        """AI生成コンテンツを人間らしく加工"""
        
        # タイトルを自然に
        title = self._humanize_title(raw_content, keyword)
        
        # 導入文を追加
        intro = self._create_natural_intro()
        
        # 本文を自然に加工
        content = self._process_content(raw_content)
        
        # 締めの文章を追加
        outro = self._create_natural_outro()
        
        # 完成したコンテンツ
        final_content = f"{intro}\n\n{content}\n\n{outro}"
        
        return {
            'title': title,
            'content': final_content,
            'excerpt': self._create_excerpt(final_content),
            'reading_time': self._calculate_reading_time(final_content),
            'tags': self._generate_natural_tags(keyword),
            'category': random.choice(self.persona['categories'])
        }
    
    def _humanize_title(self, content: str, keyword: str) -> str:
        """タイトルを自然に"""
        # 元のタイトルを取得
        lines = content.split('\n')
        original_title = ""
        for line in lines:
            if line.startswith('# '):
                original_title = line[2:].strip()
                break
        
        # 人間らしいタイトルパターン
        patterns = [
            f"【実体験】{keyword}で失敗しない方法",
            f"{keyword}を始めて3ヶ月の成果報告",
            f"初心者が{keyword}で月10万稼いだ話",
            f"{keyword}の真実｜業界人が語る本当のところ",
            f"【2024年最新】{keyword}完全攻略法",
            f"{keyword}で人生変わった話｜体験談",
            f"なぜ{keyword}が今注目されているのか",
            f"{keyword}のメリット・デメリットを正直レビュー",
        ]
        
        return random.choice(patterns)
    
    def _create_natural_intro(self) -> str:
        """自然な導入文を作成"""
        intros = [
            f"こんにちは、{self.persona['name']}です。",
            f"お疲れ様です！{self.persona['name']}です。",
            f"いつも記事を読んでくださり、ありがとうございます。",
            f"今日は時間ができたので、久しぶりに記事を書いてみました。",
            f"最近よく質問をいただく内容について書いてみました。"
        ]
        
        human_elements = random.sample(NaturalBlogConfig.HUMAN_ELEMENTS, 1)
        
        return f"{random.choice(intros)}\n\n{human_elements[0]}"
    
    def _create_natural_outro(self) -> str:
        """自然な締めの文章"""
        outros = [
            "いかがでしたでしょうか？\n\n今回の内容が少しでも参考になれば嬉しいです。",
            "長文を最後まで読んでいただき、ありがとうございました！",
            "また何か気になることがあれば、コメントで教えてください。",
            "次回も役立つ情報をお届けできるよう頑張ります！",
            "この記事が役立ったら、ぜひシェアしてもらえると嬉しいです🙏"
        ]
        
        return random.choice(outros)
    
    def _process_content(self, content: str) -> str:
        """本文を自然に加工"""
        # AIっぽい表現を人間らしく変更
        replacements = {
            "ということになります": "ということですね",
            "重要です": "大切だと思います",
            "おすすめします": "個人的にはおすすめです",
            "効果的です": "効果があると感じました",
            "必要不可欠": "必要だと思います",
            "メリットがあります": "良い点があります",
        }
        
        processed = content
        for old, new in replacements.items():
            processed = processed.replace(old, new)
        
        # 個人的な体験談を挿入
        experience_insertions = [
            "\n\n実際に私も試してみましたが、思った以上に効果がありました。\n",
            "\n\n私の場合は少し時間がかかりましたが、コツコツ続けることで結果が出ました。\n",
            "\n\n最初は半信半疑でしたが、やってみると意外と簡単でした。\n",
        ]
        
        # ランダムに体験談を挿入
        if random.random() > 0.5:
            sections = processed.split('\n\n')
            if len(sections) > 2:
                insert_pos = len(sections) // 2
                sections.insert(insert_pos, random.choice(experience_insertions))
                processed = '\n\n'.join(sections)
        
        return processed
    
    def _create_excerpt(self, content: str) -> str:
        """記事の抜粋を作成"""
        # 最初の段落を抜粋として使用
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip() and len(para.strip()) > 50:
                excerpt = para.strip()[:150]
                return excerpt + "..." if len(excerpt) == 150 else excerpt
        
        return "最新の記事をお届けします。"
    
    def _calculate_reading_time(self, content: str) -> int:
        """読了時間を計算（分）"""
        word_count = len(content)
        # 日本語の平均読書速度（1分間約400-600文字）
        reading_time = max(1, word_count // 500)
        return reading_time
    
    def _generate_natural_tags(self, keyword: str) -> List[str]:
        """自然なタグを生成"""
        base_tags = keyword.split()
        additional_tags = [
            "初心者向け", "実体験", "おすすめ", "レビュー", "解説",
            "まとめ", "比較", "ランキング", "コツ", "方法"
        ]
        
        tags = base_tags + random.sample(additional_tags, 2)
        return tags[:5]

class NaturalBlogGenerator:
    """自然なブログ生成システム"""
    
    def __init__(self, persona_key: str = "tech_blogger"):
        self.persona_key = persona_key
        self.persona = NaturalBlogConfig.BLOG_PERSONAS[persona_key]
        self.db = NaturalBlogDatabase()
        self.processor = NaturalContentProcessor(persona_key)
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/natural_blog.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def generate_natural_article(self, keyword: str) -> bool:
        """自然な記事を生成・保存"""
        try:
            # 基本的な記事を生成（既存のシステムを使用）
            raw_content = self._generate_raw_content(keyword)
            
            # 自然な記事に加工
            natural_article = self.processor.humanize_content(raw_content, keyword)
            
            # データベースに保存
            article_id = self._save_natural_article(natural_article)
            
            # ダミーコメントを生成
            self._generate_dummy_comments(article_id)
            
            self.logger.info(f"自然な記事を生成: {natural_article['title']}")
            return True
            
        except Exception as e:
            self.logger.error(f"記事生成エラー: {e}")
            return False
    
    def _generate_raw_content(self, keyword: str) -> str:
        """基本記事を生成（デモ用）"""
        return f"""# {keyword}について詳しく解説

## はじめに

{keyword}は現在注目されているトピックです。この記事では、{keyword}について詳しく解説します。

## {keyword}の基本

{keyword}の基本的な概念について説明します。

### 重要なポイント

1. 基本を理解する
2. 実践的に取り組む
3. 継続することが大切

## {keyword}の実践方法

具体的な方法について説明します。

### ステップ1: 準備
まず必要な準備を整えましょう。

### ステップ2: 実行
計画に基づいて実行します。

## まとめ

{keyword}について解説しました。ぜひ参考にしてください。
"""
    
    def _save_natural_article(self, article_data: Dict) -> int:
        """自然な記事をデータベースに保存"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # スラッグ生成
        slug = self._generate_slug(article_data['title'])
        
        # 投稿時間を自然にランダム化
        published_at = self._get_natural_publish_time()
        
        cursor.execute('''
            INSERT INTO natural_articles (
                slug, title, content, excerpt, author_name, author_bio,
                category, tags, published_at, reading_time,
                meta_title, meta_description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            slug,
            article_data['title'],
            article_data['content'],
            article_data['excerpt'],
            self.persona['name'],
            self.persona['bio'],
            article_data['category'],
            json.dumps(article_data['tags']),
            published_at,
            article_data['reading_time'],
            article_data['title'],
            article_data['excerpt']
        ))
        
        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return article_id
    
    def _generate_slug(self, title: str) -> str:
        """URLスラッグを生成"""
        slug = title.lower()
        slug = ''.join(c if c.isalnum() or c in '- ' else '' for c in slug)
        slug = slug.replace(' ', '-')
        slug = slug[:50]
        
        # ユニーク性のためタイムスタンプ追加
        timestamp = datetime.now().strftime('%m%d')
        return f"{slug}-{timestamp}"
    
    def _get_natural_publish_time(self) -> datetime:
        """自然な投稿時間を生成"""
        now = datetime.now()
        
        # ランダムに過去1-7日以内
        days_back = random.randint(0, 7)
        
        # 自然な投稿時間を選択
        posting_times = ["09:30", "12:15", "19:45", "22:30"]
        time_str = random.choice(posting_times)
        hour, minute = map(int, time_str.split(':'))
        
        publish_time = now - timedelta(days=days_back)
        publish_time = publish_time.replace(hour=hour, minute=minute, second=0)
        
        return publish_time
    
    def _generate_dummy_comments(self, article_id: int):
        """ダミーコメントを生成"""
        if random.random() > 0.7:  # 70%の確率でコメント生成
            return
        
        comment_templates = [
            "とても参考になりました！ありがとうございます。",
            "私も同じような経験があります。共感できる記事でした。",
            "詳しい解説をありがとうございます。実際に試してみます！",
            "初心者にも分かりやすい内容で助かりました。",
            "次回の記事も楽しみにしています。",
            "具体的な方法が書かれていて実践的ですね。"
        ]
        
        commenter_names = [
            "田中", "佐藤", "高橋", "山田", "中村", "小林", "加藤", "吉田"
        ]
        
        comment_count = random.randint(0, 3)
        
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for _ in range(comment_count):
            cursor.execute('''
                INSERT INTO dummy_comments (article_id, author_name, content)
                VALUES (?, ?, ?)
            ''', (
                article_id,
                random.choice(commenter_names) + "さん",
                random.choice(comment_templates)
            ))
        
        conn.commit()
        conn.close()

def create_natural_blog_website():
    """自然なブログサイトを生成"""
    
    # HTMLテンプレート
    BLOG_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ blog_title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.6; color: #333; background: #f8f9fa;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        
        /* ヘッダー */
        .header { background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .nav { padding: 20px 0; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.8em; font-weight: bold; color: #2c3e50; }
        .nav-menu { display: flex; list-style: none; }
        .nav-menu li { margin-left: 30px; }
        .nav-menu a { text-decoration: none; color: #666; transition: color 0.3s; }
        .nav-menu a:hover { color: #3498db; }
        
        /* メインコンテンツ */
        .main { padding: 40px 0; }
        .article-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 40px; }
        
        /* 記事リスト */
        .article-list { }
        .article-card { 
            background: white; border-radius: 10px; overflow: hidden; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px;
            transition: transform 0.3s ease;
        }
        .article-card:hover { transform: translateY(-5px); }
        .article-image { width: 100%; height: 200px; background: #ddd; }
        .article-body { padding: 25px; }
        .article-meta { 
            display: flex; align-items: center; color: #666; font-size: 0.9em; 
            margin-bottom: 15px;
        }
        .author-avatar { 
            width: 30px; height: 30px; border-radius: 50%; 
            background: #3498db; margin-right: 10px;
        }
        .article-title { 
            font-size: 1.4em; font-weight: bold; margin-bottom: 15px;
            color: #2c3e50;
        }
        .article-title a { text-decoration: none; color: inherit; }
        .article-title a:hover { color: #3498db; }
        .article-excerpt { color: #666; margin-bottom: 15px; }
        .article-tags { }
        .tag { 
            display: inline-block; background: #ecf0f1; padding: 4px 8px; 
            border-radius: 4px; font-size: 0.8em; color: #555; margin-right: 8px;
        }
        
        /* サイドバー */
        .sidebar { }
        .widget { 
            background: white; border-radius: 10px; padding: 25px; 
            margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .widget h3 { margin-bottom: 20px; color: #2c3e50; }
        .widget ul { list-style: none; }
        .widget li { margin-bottom: 10px; }
        .widget a { text-decoration: none; color: #666; }
        .widget a:hover { color: #3498db; }
        
        /* プロフィール */
        .profile-avatar { 
            width: 80px; height: 80px; border-radius: 50%; 
            background: #3498db; margin: 0 auto 15px; display: block;
        }
        .profile-name { text-align: center; font-weight: bold; margin-bottom: 10px; }
        .profile-bio { text-align: center; color: #666; font-size: 0.9em; }
        
        /* フッター */
        .footer { 
            background: #2c3e50; color: white; text-align: center; 
            padding: 40px 0; margin-top: 60px;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <div class="logo">{{ author_name }}のブログ</div>
                <ul class="nav-menu">
                    <li><a href="#home">ホーム</a></li>
                    <li><a href="#about">プロフィール</a></li>
                    <li><a href="#contact">お問い合わせ</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main class="main">
        <div class="container">
            <div class="article-grid">
                <div class="article-list">
                    {% for article in articles %}
                    <article class="article-card">
                        <div class="article-image"></div>
                        <div class="article-body">
                            <div class="article-meta">
                                <div class="author-avatar"></div>
                                <span>{{ article.author_name }} • {{ article.published_at }} • {{ article.reading_time }}分で読める</span>
                            </div>
                            <h2 class="article-title">
                                <a href="#article-{{ article.id }}">{{ article.title }}</a>
                            </h2>
                            <p class="article-excerpt">{{ article.excerpt }}</p>
                            <div class="article-tags">
                                {% for tag in article.tags %}
                                <span class="tag"># {{ tag }}</span>
                                {% endfor %}
                            </div>
                        </div>
                    </article>
                    {% endfor %}
                </div>
                
                <aside class="sidebar">
                    <!-- プロフィール -->
                    <div class="widget">
                        <h3>プロフィール</h3>
                        <div class="profile-avatar"></div>
                        <div class="profile-name">{{ author_name }}</div>
                        <div class="profile-bio">{{ author_bio }}</div>
                    </div>
                    
                    <!-- 人気記事 -->
                    <div class="widget">
                        <h3>人気の記事</h3>
                        <ul>
                            <li><a href="#">プログラミング学習のコツ</a></li>
                            <li><a href="#">副業で月10万円稼ぐ方法</a></li>
                            <li><a href="#">投資初心者が知るべきこと</a></li>
                        </ul>
                    </div>
                    
                    <!-- カテゴリー -->
                    <div class="widget">
                        <h3>カテゴリー</h3>
                        <ul>
                            {% for category in categories %}
                            <li><a href="#">{{ category }}</a></li>
                            {% endfor %}
                        </ul>
                    </div>
                </aside>
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {{ author_name }}のブログ. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
    '''
    
    # データベースから記事取得（デモ用）
    articles = [
        {
            'id': 1,
            'title': '【実体験】プログラミングで副業月10万達成した方法',
            'excerpt': 'プログラミング未経験から始めて、3ヶ月で副業月10万円を達成した実体験をシェアします。',
            'author_name': '山田太郎',
            'published_at': '2024年8月25日',
            'reading_time': 5,
            'tags': ['プログラミング', '副業', '実体験']
        },
        {
            'id': 2,
            'title': 'AI技術の最新動向｜2024年注目のサービス3選',
            'excerpt': '今年注目のAI技術と実用的なサービスを、エンジニア目線で解説します。',
            'author_name': '山田太郎',
            'published_at': '2024年8月20日',
            'reading_time': 7,
            'tags': ['AI', '技術解説', '最新情報']
        }
    ]
    
    # テンプレート処理（簡易版）
    template = BLOG_TEMPLATE
    template = template.replace('{{ blog_title }}', '山田太郎のテックブログ')
    template = template.replace('{{ author_name }}', '山田太郎')
    template = template.replace('{{ author_bio }}', 'フリーランスエンジニア。プログラミングとAI技術について発信しています。')
    
    # 記事リスト生成
    articles_html = ""
    for article in articles:
        tags_html = ""
        for tag in article['tags']:
            tags_html += f'<span class="tag"># {tag}</span>'
        
        articles_html += f'''
        <article class="article-card">
            <div class="article-image"></div>
            <div class="article-body">
                <div class="article-meta">
                    <div class="author-avatar"></div>
                    <span>{article['author_name']} • {article['published_at']} • {article['reading_time']}分で読める</span>
                </div>
                <h2 class="article-title">
                    <a href="#article-{article['id']}">{article['title']}</a>
                </h2>
                <p class="article-excerpt">{article['excerpt']}</p>
                <div class="article-tags">{tags_html}</div>
            </div>
        </article>
        '''
    
    # カテゴリー生成
    categories = ['プログラミング', 'AI', '副業', '技術解説']
    categories_html = ""
    for category in categories:
        categories_html += f'<li><a href="#">{category}</a></li>'
    
    # 最終HTML生成
    final_html = template.replace('{% for article in articles %}{% endfor %}', '').replace('{% for category in categories %}{% endfor %}', '')
    final_html = final_html.replace('{% for article in articles %}', '').replace('{% endfor %}', '')
    final_html = final_html.replace('{% for category in categories %}', '').replace('{% endfor %}', '')
    
    # 記事とカテゴリーを挿入
    final_html = final_html.replace('<div class="article-list">', f'<div class="article-list">{articles_html}')
    final_html = final_html.replace('<ul>\n                            {% for category in categories %}', f'<ul>{categories_html}')
    
    return final_html

def main():
    """メイン処理"""
    print("🎭 自然なブログシステム")
    print("=" * 40)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['generate', 'website', 'demo'], default='demo')
    parser.add_argument('--persona', choices=['tech_blogger', 'lifestyle_blogger', 'business_blogger'], default='tech_blogger')
    parser.add_argument('--keyword', type=str, help='記事のキーワード')
    
    args = parser.parse_args()
    
    if args.mode == 'generate':
        # 自然な記事を生成
        generator = NaturalBlogGenerator(args.persona)
        keyword = args.keyword or "プログラミング 副業"
        generator.generate_natural_article(keyword)
        
    elif args.mode == 'website':
        # 自然なブログサイトを生成
        html = create_natural_blog_website()
        
        # ファイルに保存
        os.makedirs('natural_blog', exist_ok=True)
        with open('natural_blog/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ 自然なブログサイトを生成しました")
        print("📂 場所: natural_blog/index.html")
        
        # ブラウザで開く
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath("natural_blog/index.html")}')
        
    else:  # demo
        # デモサイト生成
        html = create_natural_blog_website()
        
        os.makedirs('natural_blog', exist_ok=True)
        with open('natural_blog/index.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("✅ 自然なブログのデモを生成しました")
        print("📂 natural_blog/index.html をブラウザで開いてください")
        
        # 自動で開く
        import webbrowser
        webbrowser.open(f'file://{os.path.abspath("natural_blog/index.html")}')

if __name__ == "__main__":
    main()