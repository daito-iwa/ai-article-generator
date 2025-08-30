#!/usr/bin/env python3
"""
GitHub Pages 完全無料デプロイメント
GitHubアカウントだけで即収益化ブログを公開
"""

import os
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

class GitHubPagesDeployment:
    """GitHub Pages無料デプロイメント"""
    
    def __init__(self, repo_name="ai-auto-blog"):
        self.repo_name = repo_name
        self.docs_dir = "docs"  # GitHub Pagesのソースフォルダ
        self.site_url = f"https://username.github.io/{repo_name}"
        
    def create_github_pages_site(self):
        """GitHub Pages用サイトを作成"""
        print("🌐 GitHub Pages無料ブログサイト生成中...")
        
        # docsディレクトリ作成
        os.makedirs(self.docs_dir, exist_ok=True)
        
        # 記事データを取得
        articles = self._get_stealth_articles()
        
        # メインページ生成
        self._create_index_page(articles)
        
        # 個別記事ページ生成
        self._create_article_pages(articles)
        
        # CSS・JS生成
        self._create_assets()
        
        # GitHub Pages設定ファイル
        self._create_github_config()
        
        # デプロイ手順書生成
        self._create_deployment_guide()
        
        print(f"\n✅ GitHub Pagesサイト生成完了！")
        print(f"📁 場所: {self.docs_dir}/")
        print(f"🌐 公開予定URL: https://YOUR-USERNAME.github.io/{self.repo_name}")
    
    def _get_stealth_articles(self):
        """ステルス記事を取得"""
        db_path = "data/stealth_blog.db"
        
        if not os.path.exists(db_path):
            # デモ記事を生成
            return self._create_demo_articles()
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, content, persona_key, mood, published_at
            FROM stealth_articles 
            ORDER BY created_at DESC
        ''')
        
        articles = []
        personas = {
            "tech_engineer": "T.K",
            "lifestyle_mom": "M.Y",
            "business_consultant": "S.J", 
            "finance_expert": "K.H",
            "health_blogger": "R.N",
            "creative_freelancer": "A.M",
            "travel_writer": "Y.S",
            "student_blogger": "H.T"
        }
        
        for row in cursor.fetchall():
            title, content, persona, mood, published_at = row
            articles.append({
                'title': title,
                'content': content,
                'author': personas.get(persona, persona),
                'persona': persona,
                'date': published_at,
                'slug': self._create_slug(title)
            })
        
        conn.close()
        return articles
    
    def _create_demo_articles(self):
        """デモ記事を作成"""
        return [
            {
                'title': '【完全無料】GitHub Pagesでブログ収益化する方法',
                'content': '''# 【完全無料】GitHub Pagesでブログ収益化する方法

こんにちは。今回はGitHub Pagesを使って完全無料でブログを作り、収益化する方法をご紹介します。

## GitHub Pagesとは？

GitHub Pagesは、GitHubが提供する無料のウェブサイトホスティングサービスです。

### メリット
- **完全無料**：一切費用がかかりません
- **高速表示**：GitHubのCDNで高速配信
- **SSL対応**：自動でHTTPS対応
- **独自ドメイン対応**：後から独自ドメインも設定可能

## 収益化方法

### 1. Google AdSense
記事内に広告コードを配置することで、ページビューに応じて収益を得られます。

### 2. アフィリエイト
以下のような高収益案件を記事内で紹介：

#### おすすめサービス
- **プログラミングスクール**：1件成約で10,000円〜30,000円
- **転職エージェント**：1件成約で5,000円〜15,000円  
- **投資サービス**：1件成約で3,000円〜10,000円

<div style="border: 2px solid #e74c3c; padding: 15px; margin: 20px 0; border-radius: 8px; background: #fdf2f2;">
<h4 style="color: #e74c3c;">🎯 高収益アフィリエイト例</h4>
<p><strong>DMM WEBCAMP</strong> - プログラミング学習で人生変える</p>
<p>成約単価: <strong>30,000円</strong></p>
<a href="#affiliate-link" style="background: #e74c3c; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">詳細を見る</a>
</div>

## まとめ

GitHub Pagesを使えば、完全無料でプロ級のブログが作成できます。収益化も十分可能なので、ぜひ挑戦してみてください！''',
                'author': 'T.K',
                'persona': 'tech_engineer',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slug': 'github-pages-monetization'
            },
            {
                'title': '副業ブログで月10万円稼ぐロードマップ',
                'content': '''# 副業ブログで月10万円稼ぐロードマップ

こんにちは。今回は副業でブログを始めて、月10万円の収益を目指すための具体的なロードマップをお伝えします。

## 収益化までの期間

実際の目安をお伝えします：

### 1ヶ月目：基盤構築
- ブログ開設
- 記事を10本投稿
- Google AdSense申請
- **目標収益：0円**

### 3ヶ月目：収益化開始  
- 記事数50本到達
- 検索流入が増加開始
- アフィリエイト初成約
- **目標収益：3万円**

### 6ヶ月目：安定収益
- 記事数100本到達
- 月間10万PV達成
- 複数のアフィリエイト成約
- **目標収益：10万円**

## 高収益ジャンル

### 1. 転職・就職 (成約単価: 3,000円〜15,000円)
- 転職エージェント紹介
- 就活サイト紹介
- スキルアップサービス

### 2. 投資・金融 (成約単価: 5,000円〜20,000円)
- 証券会社口座開設
- FX口座開設
- 仮想通貨取引所

### 3. プログラミング (成約単価: 10,000円〜30,000円)
- プログラミングスクール
- 学習サイト
- 転職支援サービス

<div style="background: #f8f9fa; padding: 20px; margin: 20px 0; border-left: 4px solid #28a745;">
<h4 style="color: #28a745;">💰 収益化のコツ</h4>
<ul>
<li>読者の悩みを解決する記事を書く</li>
<li>実体験を混ぜて信頼性を高める</li>
<li>SEOキーワードを意識したタイトル</li>
<li>アフィリエイトは自然に紹介</li>
</ul>
</div>

## まとめ

副業ブログは継続すれば必ず結果が出ます。最初は大変ですが、月10万円の副収入があれば生活がかなり楽になります。ぜひ挑戦してみてください！''',
                'author': 'M.Y',
                'persona': 'lifestyle_mom',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slug': 'blog-monetization-roadmap'
            },
            {
                'title': 'AI自動ブログで不労所得を作る方法',
                'content': '''# AI自動ブログで不労所得を作る方法

こんにちは。今回はAIを活用して記事を自動生成し、不労所得を作る最新の方法をご紹介します。

## AI自動ブログの仕組み

### 従来のブログ vs AI自動ブログ

**従来のブログ**
- 記事作成に3-5時間/記事
- ネタ切れのリスク
- 継続が困難

**AI自動ブログ**  
- 記事作成が完全自動化
- 無限にコンテンツ生成可能
- 24時間365日稼働

## 収益モデル

### 1. スケールメリット
- 1日10記事自動投稿可能
- 月300記事で検索流入を独占
- 競合を圧倒する記事数

### 2. 多様な収益源
- **Google AdSense**：月20万円〜
- **アフィリエイト**：月50万円〜  
- **記事販売**：月10万円〜
- **SEOコンサル**：月30万円〜

## 実際の成果事例

<div style="background: #e8f5e9; padding: 20px; margin: 20px 0; border-radius: 8px;">
<h4 style="color: #2e7d32;">📊 3ヶ月後の実績</h4>
<ul style="color: #2e7d32;">
<li><strong>記事数</strong>：900記事自動投稿</li>
<li><strong>月間PV</strong>：50万PV達成</li>
<li><strong>月間収益</strong>：80万円</li>
<li><strong>作業時間</strong>：週1時間（システム管理のみ）</li>
</ul>
</div>

## 技術的な仕組み

### AIライティング
- GPT-4による高品質記事生成
- SEOキーワード自動最適化
- 複数の専門分野に対応

### 自動投稿システム
- WordPress REST API連携
- スケジュール投稿
- アフィリエイトリンク自動挿入

## 今後の展望

AI技術の進化により、さらに高品質な記事が自動生成可能になります。早めに始めることで先行者利益を得られます。

## まとめ

AI自動ブログは、従来のブログの限界を突破する革新的な手法です。不労所得を作りたい方は、ぜひ検討してみてください。''',
                'author': 'S.J', 
                'persona': 'business_consultant',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'slug': 'ai-auto-blog-passive-income'
            }
        ]
    
    def _create_index_page(self, articles):
        """メインページ作成"""
        html = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI自動収益ブログ - 完全無料で月収50万円を目指す</title>
    <meta name="description" content="GitHub Pagesを使った完全無料ブログで収益化。AI自動記事生成システムで月収50万円を目指すブログ運営術を公開。">
    <link rel="stylesheet" href="assets/style.css">
    
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX" crossorigin="anonymous"></script>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="logo">🤖 AI自動収益ブログ</h1>
            <p class="tagline">完全無料 × AI自動化で月収50万円を目指す</p>
            <nav class="nav">
                <a href="#about">ブログについて</a>
                <a href="#monetization">収益化方法</a>
                <a href="#contact">お問い合わせ</a>
            </nav>
        </div>
    </header>

    <!-- Google AdSense 自動広告 -->
    <div class="ad-banner">
        <ins class="adsbygoogle"
             style="display:block"
             data-ad-client="ca-pub-XXXXXXXXXX"
             data-ad-slot="XXXXXXXXXX"
             data-ad-format="auto"></ins>
        <script>(adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
    </div>

    <main class="main">
        <div class="container">
            <section class="hero">
                <h2>🚀 完全無料でブログ収益化を実現</h2>
                <p>GitHub Pages + AI自動記事生成で、初期費用0円から月収50万円を目指すブログ運営術を完全公開！</p>
                
                <div class="stats">
                    <div class="stat-item">
                        <span class="stat-number">0円</span>
                        <span class="stat-label">初期費用</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">50万円</span>
                        <span class="stat-label">目標月収</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">24時間</span>
                        <span class="stat-label">AI自動稼働</span>
                    </div>
                </div>
            </section>

            <section class="articles">
                <h2>📝 最新記事</h2>
                <div class="articles-grid">'''
        
        # 記事カード生成
        for article in articles[:6]:
            html += f'''
                    <article class="article-card">
                        <div class="article-header">
                            <span class="author">{article['author']}</span>
                            <span class="date">{article['date']}</span>
                        </div>
                        <h3><a href="articles/{article['slug']}.html">{article['title']}</a></h3>
                        <div class="excerpt">{self._create_excerpt(article['content'])}</div>
                        <a href="articles/{article['slug']}.html" class="read-more">続きを読む →</a>
                    </article>'''
        
        html += '''
                </div>
            </section>

            <!-- 収益化セクション -->
            <section id="monetization" class="monetization">
                <h2>💰 収益化戦略</h2>
                <div class="monetization-grid">
                    <div class="monetization-card">
                        <h3>🎯 Google AdSense</h3>
                        <p>ページビューに応じた広告収益</p>
                        <div class="revenue">月収: <strong>5万円〜20万円</strong></div>
                    </div>
                    <div class="monetization-card">
                        <h3>🔗 アフィリエイト</h3>
                        <p>高単価商品の紹介収益</p>
                        <div class="revenue">月収: <strong>10万円〜50万円</strong></div>
                    </div>
                    <div class="monetization-card">
                        <h3>📊 SEOコンサル</h3>
                        <p>実績を活かしたコンサル収益</p>
                        <div class="revenue">月収: <strong>20万円〜100万円</strong></div>
                    </div>
                </div>
            </section>

            <!-- Google AdSense 記事下広告 -->
            <div class="ad-container">
                <ins class="adsbygoogle"
                     style="display:block"
                     data-ad-client="ca-pub-XXXXXXXXXX"
                     data-ad-slot="XXXXXXXXXX"
                     data-ad-format="auto"></ins>
                <script>(adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
            </div>

            <!-- 高収益アフィリエイト -->
            <section class="affiliate-section">
                <h2>🎯 おすすめサービス</h2>
                <div class="affiliate-grid">
                    <div class="affiliate-card">
                        <h3>プログラミング学習</h3>
                        <p>未経験から転職成功まで完全サポート</p>
                        <p class="price">成約報酬: <strong>30,000円</strong></p>
                        <a href="#affiliate-programming" class="affiliate-btn">詳細を見る</a>
                    </div>
                    <div class="affiliate-card">
                        <h3>転職エージェント</h3>
                        <p>年収アップ転職を完全サポート</p>
                        <p class="price">成約報酬: <strong>15,000円</strong></p>
                        <a href="#affiliate-job" class="affiliate-btn">詳細を見る</a>
                    </div>
                    <div class="affiliate-card">
                        <h3>投資・資産運用</h3>
                        <p>初心者でも安心の投資サポート</p>
                        <p class="price">成約報酬: <strong>10,000円</strong></p>
                        <a href="#affiliate-invest" class="affiliate-btn">詳細を見る</a>
                    </div>
                </div>
            </section>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 AI自動収益ブログ. GitHub Pagesで完全無料運営中</p>
            <p>Powered by AI Article Generation System</p>
        </div>
    </footer>

    <script src="assets/script.js"></script>
</body>
</html>'''
        
        with open(f"{self.docs_dir}/index.html", 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _create_article_pages(self, articles):
        """個別記事ページ作成"""
        articles_dir = os.path.join(self.docs_dir, "articles")
        os.makedirs(articles_dir, exist_ok=True)
        
        for article in articles:
            content_html = self._markdown_to_html(article['content'])
            
            html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} | AI自動収益ブログ</title>
    <meta name="description" content="{self._create_excerpt(article['content'])}">
    <link rel="stylesheet" href="../assets/style.css">
    
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX" crossorigin="anonymous"></script>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1 class="logo"><a href="../index.html">🤖 AI自動収益ブログ</a></h1>
        </div>
    </header>

    <main class="article-main">
        <div class="container">
            <article class="article">
                <div class="article-header">
                    <h1>{article['title']}</h1>
                    <div class="article-meta">
                        <span class="author">著者: {article['author']}</span>
                        <span class="date">投稿日: {article['date']}</span>
                    </div>
                </div>

                <!-- 記事上部広告 -->
                <div class="ad-container">
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-XXXXXXXXXX"
                         data-ad-slot="XXXXXXXXXX"
                         data-ad-format="auto"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
                </div>

                <div class="article-content">
                    {content_html}
                </div>

                <!-- 記事下部広告 -->
                <div class="ad-container">
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-XXXXXXXXXX"
                         data-ad-slot="XXXXXXXXXX"
                         data-ad-format="auto"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({{}}); </script>
                </div>
            </article>

            <div class="back-to-home">
                <a href="../index.html">← トップページに戻る</a>
            </div>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 AI自動収益ブログ. GitHub Pagesで完全無料運営中</p>
        </div>
    </footer>
</body>
</html>'''
            
            with open(f"{articles_dir}/{article['slug']}.html", 'w', encoding='utf-8') as f:
                f.write(html)
    
    def _create_assets(self):
        """CSS・JSファイル作成"""
        assets_dir = os.path.join(self.docs_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # CSS
        css = '''
/* AI自動収益ブログ専用CSS */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* ヘッダー */
.header {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    padding: 20px 0;
    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
}

.logo {
    font-size: 2em;
    font-weight: bold;
    background: linear-gradient(45deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 5px;
}

.logo a {
    color: inherit;
    text-decoration: none;
}

.tagline {
    color: #666;
    font-size: 1.1em;
    margin-bottom: 15px;
}

.nav a {
    margin-right: 30px;
    text-decoration: none;
    color: #666;
    font-weight: 500;
    transition: color 0.3s;
}

.nav a:hover {
    color: #667eea;
}

/* メインコンテンツ */
.main {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    margin: 40px 0;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 60px 40px;
    text-align: center;
}

.hero h2 {
    font-size: 2.5em;
    margin-bottom: 20px;
}

.hero p {
    font-size: 1.3em;
    margin-bottom: 40px;
    opacity: 0.9;
}

.stats {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 40px;
}

.stat-item {
    text-align: center;
}

.stat-number {
    display: block;
    font-size: 2.5em;
    font-weight: bold;
    color: #ffd700;
}

.stat-label {
    font-size: 1em;
    opacity: 0.8;
}

/* 記事グリッド */
.articles {
    padding: 60px 40px;
}

.articles h2 {
    font-size: 2.2em;
    margin-bottom: 40px;
    text-align: center;
    color: #2c3e50;
}

.articles-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 30px;
}

.article-card {
    background: white;
    border-radius: 15px;
    padding: 25px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.article-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.article-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
    font-size: 0.9em;
    color: #666;
}

.author {
    background: #667eea;
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 500;
}

.article-card h3 {
    margin-bottom: 15px;
    font-size: 1.4em;
    line-height: 1.3;
}

.article-card h3 a {
    color: #2c3e50;
    text-decoration: none;
}

.article-card h3 a:hover {
    color: #667eea;
}

.excerpt {
    color: #666;
    margin-bottom: 15px;
    line-height: 1.7;
}

.read-more {
    color: #667eea;
    text-decoration: none;
    font-weight: 600;
    transition: color 0.3s;
}

.read-more:hover {
    color: #764ba2;
}

/* 収益化セクション */
.monetization {
    background: #f8f9fa;
    padding: 60px 40px;
}

.monetization h2 {
    text-align: center;
    font-size: 2.2em;
    margin-bottom: 40px;
    color: #2c3e50;
}

.monetization-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.monetization-card {
    background: white;
    padding: 30px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.monetization-card h3 {
    font-size: 1.5em;
    margin-bottom: 15px;
    color: #2c3e50;
}

.revenue {
    margin-top: 15px;
    font-size: 1.2em;
    color: #27ae60;
}

.revenue strong {
    font-size: 1.3em;
}

/* アフィリエイトセクション */
.affiliate-section {
    padding: 60px 40px;
    background: white;
}

.affiliate-section h2 {
    text-align: center;
    font-size: 2.2em;
    margin-bottom: 40px;
    color: #2c3e50;
}

.affiliate-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.affiliate-card {
    border: 2px solid #e74c3c;
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    background: #fdf2f2;
    transition: transform 0.3s ease;
}

.affiliate-card:hover {
    transform: translateY(-5px);
}

.affiliate-card h3 {
    color: #e74c3c;
    margin-bottom: 15px;
}

.price {
    font-size: 1.2em;
    margin: 15px 0;
}

.price strong {
    color: #e74c3c;
    font-size: 1.3em;
}

.affiliate-btn {
    display: inline-block;
    background: #e74c3c;
    color: white;
    padding: 12px 25px;
    border-radius: 25px;
    text-decoration: none;
    font-weight: 600;
    transition: background 0.3s;
}

.affiliate-btn:hover {
    background: #c0392b;
}

/* 広告エリア */
.ad-banner, .ad-container {
    text-align: center;
    margin: 30px 0;
    padding: 20px;
}

/* 個別記事ページ */
.article-main {
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(10px);
    margin: 40px 0;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.article {
    padding: 60px 40px;
}

.article-header h1 {
    font-size: 2.2em;
    margin-bottom: 20px;
    color: #2c3e50;
    line-height: 1.3;
}

.article-meta {
    margin-bottom: 40px;
    color: #666;
}

.article-meta span {
    margin-right: 20px;
}

.article-content {
    font-size: 1.1em;
    line-height: 1.8;
}

.article-content h2 {
    margin: 40px 0 20px;
    color: #2c3e50;
    font-size: 1.8em;
}

.article-content h3 {
    margin: 30px 0 15px;
    color: #34495e;
    font-size: 1.4em;
}

.article-content p {
    margin-bottom: 20px;
}

.article-content ul, .article-content ol {
    margin: 20px 0;
    padding-left: 30px;
}

.article-content li {
    margin-bottom: 10px;
}

.back-to-home {
    text-align: center;
    padding: 20px;
}

.back-to-home a {
    color: #667eea;
    text-decoration: none;
    font-size: 1.1em;
    font-weight: 600;
}

/* フッター */
.footer {
    background: rgba(44, 62, 80, 0.9);
    color: white;
    text-align: center;
    padding: 40px 0;
    margin-top: 40px;
}

.footer p {
    margin-bottom: 10px;
    opacity: 0.8;
}

/* レスポンシブ */
@media (max-width: 768px) {
    .hero h2 {
        font-size: 1.8em;
    }
    
    .hero p {
        font-size: 1.1em;
    }
    
    .stats {
        flex-direction: column;
        gap: 20px;
    }
    
    .articles, .monetization, .affiliate-section, .article {
        padding: 40px 20px;
    }
    
    .articles-grid, .monetization-grid, .affiliate-grid {
        grid-template-columns: 1fr;
    }
}
'''
        
        with open(f"{assets_dir}/style.css", 'w', encoding='utf-8') as f:
            f.write(css)
        
        # JavaScript
        js = '''
// AI自動収益ブログ専用JavaScript

// Google AdSense自動読み込み
document.addEventListener('DOMContentLoaded', function() {
    // AdSense広告の遅延読み込み
    const ads = document.querySelectorAll('.adsbygoogle');
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                try {
                    (adsbygoogle = window.adsbygoogle || []).push({});
                }} catch(e) {{
                    console.log('AdSense読み込みエラー:', e);
                }
                observer.unobserve(entry.target);
            }
        });
    });
    
    ads.forEach(function(ad) {
        observer.observe(ad);
    });
});

// アフィリエイトクリック追跡
function trackAffiliateClick(service) {
    // Google Analytics イベント送信
    if (typeof gtag !== 'undefined') {
        gtag('event', 'affiliate_click', {
            'event_category': 'affiliate',
            'event_label': service,
            'value': 1
        });
    }
    
    console.log('アフィリエイトクリック:', service);
}

// スムーズスクロール
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
'''
        
        with open(f"{assets_dir}/script.js", 'w', encoding='utf-8') as f:
            f.write(js)
    
    def _create_github_config(self):
        """GitHub Pages設定ファイル作成"""
        
        # _config.yml (Jekyll設定)
        config = '''# GitHub Pages設定
title: "AI自動収益ブログ"
description: "GitHub Pagesで完全無料ブログ収益化"
url: "https://username.github.io"
baseurl: "/ai-auto-blog"

# SEO設定  
lang: ja
author: "AI Blog Team"

# GitHub Pages設定
plugins:
  - jekyll-sitemap
  - jekyll-feed

# 除外ファイル
exclude:
  - README.md
  - LICENSE
'''
        
        with open(f"{self.docs_dir}/_config.yml", 'w', encoding='utf-8') as f:
            f.write(config)
        
        # robots.txt
        robots = '''User-agent: *
Allow: /

Sitemap: https://username.github.io/ai-auto-blog/sitemap.xml
'''
        
        with open(f"{self.docs_dir}/robots.txt", 'w', encoding='utf-8') as f:
            f.write(robots)
        
        # .nojekyll (Jekyll無効化)
        with open(f"{self.docs_dir}/.nojekyll", 'w') as f:
            f.write('')
    
    def _create_deployment_guide(self):
        """デプロイ手順書作成"""
        guide = '''# 🚀 GitHub Pages無料デプロイメントガイド

## ステップ1: GitHubリポジトリ作成

1. GitHub.comにログイン
2. 「New repository」をクリック
3. リポジトリ名: `ai-auto-blog`
4. 「Public」を選択
5. 「Create repository」をクリック

## ステップ2: ファイルアップロード

### 方法A: GitHub Web インターフェース
1. 「uploading an existing file」をクリック
2. `docs/` フォルダ内の全ファイルをドラッグ&ドロップ
3. コミットメッセージ: "Initial commit"
4. 「Commit changes」をクリック

### 方法B: Git コマンド
```bash
git clone https://github.com/YOUR-USERNAME/ai-auto-blog.git
cd ai-auto-blog
cp -r docs/* .
git add .
git commit -m "Initial commit"
git push origin main
```

## ステップ3: GitHub Pages有効化

1. リポジトリの「Settings」タブをクリック
2. 左サイドバーの「Pages」をクリック
3. Source: 「Deploy from a branch」を選択
4. Branch: 「main」を選択
5. Folder: 「/ (root)」を選択
6. 「Save」をクリック

## ステップ4: 公開URL確認

5-10分後に以下URLでアクセス可能：
```
https://YOUR-USERNAME.github.io/ai-auto-blog/
```

## ステップ5: 収益化設定

### Google AdSense
1. [Google AdSense](https://www.google.com/adsense/)に申し込み
2. サイトを追加: `https://YOUR-USERNAME.github.io/ai-auto-blog/`
3. 審査通過後、広告コードを取得
4. `index.html`と記事ページの`ca-pub-XXXXXXXXXX`を実際のコードに置換

### アフィリエイト
1. [A8.net](https://www.a8.net/)に登録
2. 高収益案件と提携
3. 記事内のアフィリエイトリンクを実際のものに置換

## 予想収益

### 3ヶ月後
- **月間PV**: 1万PV
- **AdSense**: 3,000円
- **アフィリエイト**: 15,000円
- **合計**: 18,000円/月

### 6ヶ月後
- **月間PV**: 5万PV  
- **AdSense**: 15,000円
- **アフィリエイト**: 80,000円
- **合計**: 95,000円/月

### 1年後
- **月間PV**: 20万PV
- **AdSense**: 60,000円
- **アフィリエイト**: 300,000円
- **合計**: 360,000円/月

## 自動化スクリプト実行

```bash
# 新しい記事を自動生成
python3 stealth_blog_automation.py --mode generate

# GitHub Pagesサイトを更新
python3 github_pages_deployment.py

# GitHubにプッシュ
git add .
git commit -m "Add new articles"
git push origin main
```

## 成功のポイント

1. **継続的な記事投稿** - 週3-5記事が理想
2. **SEOキーワード狙い** - 検索ボリュームの多いキーワード
3. **高単価アフィリエイト** - 成約単価5,000円以上を狙う
4. **ユーザビリティ向上** - 読みやすいデザインと構成

## トラブルシューティング

### GitHub Pagesが表示されない
- リポジトリがPublicになっているか確認
- ファイルがルートディレクトリにあるか確認
- 5-10分待ってからアクセス

### AdSense審査に通らない
- 最低20記事は必要
- プライバシーポリシーページを追加
- お問い合わせフォームを設置

完全無料で月収50万円も夢ではありません！
'''
        
        with open("DEPLOYMENT_GUIDE.md", 'w', encoding='utf-8') as f:
            f.write(guide)
    
    def _create_slug(self, title):
        """URLスラッグ生成"""
        import re
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        return slug[:50]
    
    def _create_excerpt(self, content):
        """記事抜粋生成"""
        import re
        clean_text = re.sub(r'#+ ', '', content)
        clean_text = re.sub(r'\n+', ' ', clean_text)
        return clean_text[:120] + '...' if len(clean_text) > 120 else clean_text
    
    def _markdown_to_html(self, markdown):
        """簡易Markdown→HTML変換"""
        import re
        
        html = markdown
        
        # 見出し変換
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE) 
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # リスト変換
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*</li>\s*)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
        
        # 太字変換
        html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)
        
        # リンク変換
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
        
        # 段落変換
        paragraphs = html.split('\n\n')
        processed_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            processed_paragraphs.append(para)
        
        return '\n\n'.join(processed_paragraphs)

def main():
    """メイン処理"""
    print("🌐 GitHub Pages 完全無料デプロイメント")
    print("=" * 50)
    
    deployer = GitHubPagesDeployment()
    deployer.create_github_pages_site()
    
    print("\n📋 次のステップ:")
    print("1. DEPLOYMENT_GUIDE.md を読んでGitHubにアップロード")
    print("2. GitHub Pagesを有効化") 
    print("3. Google AdSenseとアフィリエイトの設定")
    print("4. 完全無料で収益化開始！")

if __name__ == "__main__":
    main()