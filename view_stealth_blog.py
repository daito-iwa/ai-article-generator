#!/usr/bin/env python3
"""
ステルスブログの記事を表示して自然な見た目を確認
"""

import sqlite3
import json
from datetime import datetime

def view_stealth_articles():
    """ステルス記事を表示"""
    db_path = "data/stealth_blog.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, content, persona_key, mood, 
                   writing_session_duration, published_at, authenticity_markers
            FROM stealth_articles 
            ORDER BY created_at DESC
        ''')
        
        articles = cursor.fetchall()
        conn.close()
        
        print("🕵️ ステルスブログの記事一覧")
        print("=" * 60)
        
        for i, article in enumerate(articles, 1):
            title, content, persona, mood, duration, published_at, markers = article
            
            print(f"\n【記事 {i}】")
            print(f"タイトル: {title}")
            print(f"ペルソナ: {persona}")
            print(f"気分: {mood}")
            print(f"執筆時間: {duration}分")
            print(f"投稿日時: {published_at}")
            if markers:
                print(f"真正性マーカー: {json.loads(markers)}")
            print("-" * 50)
            print(content[:500] + "..." if len(content) > 500 else content)
            print("=" * 60)
        
        # HTMLブログも生成
        create_natural_blog_html(articles)
        
    except Exception as e:
        print(f"エラー: {e}")
        print("データベースが存在しない、または記事がありません")

def create_natural_blog_html(articles):
    """自然な見た目のHTMLブログを生成"""
    
    html = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name=\"viewport\" content="width=device-width, initial-scale=1.0">
    <title>ナチュラルライフブログ</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif;
            line-height: 1.7; color: #333; background: #fafafa;
        }
        .container { max-width: 1000px; margin: 0 auto; padding: 0 20px; }
        
        /* ヘッダー */
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; padding: 50px 0; text-align: center; 
        }
        .header h1 { font-size: 2.8em; margin-bottom: 10px; font-weight: 300; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        
        /* メインコンテンツ */
        .main { padding: 50px 0; }
        .articles-grid { display: grid; gap: 40px; }
        
        /* 記事カード */
        .article-card { 
            background: white; border-radius: 15px; overflow: hidden;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12); 
            transition: all 0.3s ease;
        }
        .article-card:hover { 
            transform: translateY(-10px); 
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
        }
        
        .article-header { padding: 30px 30px 20px; }
        .article-meta { 
            display: flex; align-items: center; margin-bottom: 15px;
            color: #666; font-size: 0.9em;
        }
        .author-badge {
            display: inline-flex; align-items: center;
            background: #f1f3f4; border-radius: 20px;
            padding: 5px 12px; margin-right: 15px;
        }
        .author-avatar {
            width: 24px; height: 24px; border-radius: 50%;
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            margin-right: 8px;
        }
        
        .article-title { 
            font-size: 1.6em; font-weight: 600; margin-bottom: 15px;
            color: #2c3e50; line-height: 1.4;
        }
        .article-content { padding: 0 30px 30px; }
        .article-excerpt { 
            color: #555; line-height: 1.8; margin-bottom: 20px;
            font-size: 1.05em;
        }
        
        .mood-indicator {
            display: inline-block; padding: 4px 10px;
            border-radius: 20px; font-size: 0.8em;
            background: #e8f4fd; color: #1976d2;
            margin-left: 10px;
        }
        
        .writing-stats {
            display: flex; gap: 20px; margin-top: 20px;
            font-size: 0.85em; color: #666;
        }
        
        .stat-item {
            display: flex; align-items: center;
            background: #f8f9fa; padding: 5px 10px; border-radius: 15px;
        }
        
        /* フッター */
        .footer { 
            background: #2c3e50; color: white; text-align: center;
            padding: 40px 0; margin-top: 80px;
        }
        
        /* レスポンシブ */
        @media (max-width: 768px) {
            .header h1 { font-size: 2.2em; }
            .article-header, .article-content { padding: 20px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>ナチュラルライフブログ</h1>
            <p>日々の生活をより良くするヒントをお届けします</p>
        </div>
    </header>
    
    <main class="main">
        <div class="container">
            <div class="articles-grid">'''
    
    for article in articles:
        title, content, persona, mood, duration, published_at, markers = article
        
        # ペルソナ名をマッピング
        persona_names = {
            "tech_engineer": "T.K",
            "lifestyle_mom": "M.Y", 
            "business_consultant": "S.J",
            "finance_expert": "K.H",
            "health_blogger": "R.N",
            "creative_freelancer": "A.M",
            "travel_writer": "Y.S",
            "student_blogger": "H.T"
        }
        author_name = persona_names.get(persona, persona)
        
        # 気分を日本語に
        mood_jp = {
            "motivated": "やる気", "fresh_start": "新鮮", "focused": "集中",
            "productive": "生産的", "steady": "安定", "mid_week": "中盤",
            "tired": "疲れ", "pushing_through": "頑張り", "relieved": "安心",
            "weekend_prep": "週末準備", "relaxed": "リラックス", "weekend_mode": "週末",
            "reflective": "内省", "prep_mode": "準備", "energetic": "元気",
            "thoughtful": "思慮深い", "nostalgic": "懐かしい", "excited": "興奮",
            "calm": "穏やか"
        }.get(mood, mood)
        
        # 抜粋を作成
        lines = content.split('\n')
        excerpt = ""
        for line in lines:
            if line.strip() and not line.startswith('#'):
                excerpt = line.strip()[:200]
                break
        if not excerpt:
            excerpt = "最新の記事をお届けします。"
        
        # 投稿日をフォーマット
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            date_str = pub_date.strftime('%Y年%m月%d日')
        except:
            date_str = "最近"
        
        html += f'''
                <article class="article-card">
                    <div class="article-header">
                        <div class="article-meta">
                            <div class="author-badge">
                                <div class="author-avatar"></div>
                                <span>{author_name}</span>
                            </div>
                            <span>{date_str}</span>
                            <span class="mood-indicator">{mood_jp}モード</span>
                        </div>
                        <h2 class="article-title">{title}</h2>
                    </div>
                    <div class="article-content">
                        <div class="article-excerpt">{excerpt}...</div>
                        <div class="writing-stats">
                            <div class="stat-item">📝 執筆時間: {duration}分</div>
                            <div class="stat-item">🎯 {persona.replace('_', ' ').title()}スタイル</div>
                        </div>
                    </div>
                </article>'''
    
    html += '''
            </div>
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 ナチュラルライフブログ - 自然な日々をお届けします</p>
        </div>
    </footer>
</body>
</html>'''
    
    # HTMLファイルを保存
    with open('stealth_blog_demo.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ 自然な見た目のブログを生成しました")
    print(f"📁 ファイル: stealth_blog_demo.html")
    
    # ブラウザで開く
    import webbrowser
    import os
    webbrowser.open(f'file://{os.path.abspath("stealth_blog_demo.html")}')

if __name__ == "__main__":
    view_stealth_articles()