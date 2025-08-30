#!/usr/bin/env python3
"""
GitHub Pages Note風サイト用自動投稿システム
トレンドに基づいて毎日自動的に記事を生成し、GitHubに投稿
"""

import json
import os
import random
import time
from datetime import datetime, timedelta
import pytrends
from pytrends.request import TrendReq
import openai
from typing import Dict, List, Optional
import requests
import base64
import schedule
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_post.log'),
        logging.StreamHandler()
    ]
)

class GitHubAutoPostSystem:
    def __init__(self, config_path: str = "config/auto_post_config.json"):
        """GitHub自動投稿システムの初期化"""
        self.config = self.load_config(config_path)
        self.github_repo = self.config['github']['repository']
        self.github_token = self.config['github']['token']
        self.openai_api_key = self.config['openai']['api_key']
        
        # OpenAI設定
        openai.api_key = self.openai_api_key
        
        # トレンドAPI初期化
        self.pytrends = TrendReq(hl='ja-JP', tz=360)
        
        # ペルソナ定義（匿名化済み）
        self.personas = {
            "tech_engineer": {
                "name": "T.K",
                "role": "AIエンジニア",
                "avatar": "TK",
                "style": "技術的で実践的、コード例を多用",
                "topics": ["プログラミング", "AI", "Web開発", "クラウド"],
                "tone": "専門的だが分かりやすい"
            },
            "lifestyle_blogger": {
                "name": "M.Y",
                "role": "ライフスタイル",
                "avatar": "MY",
                "style": "親しみやすく、実体験を交えた内容",
                "topics": ["副業", "ライフハック", "健康", "トレンド"],
                "tone": "カジュアルで共感的"
            },
            "business_consultant": {
                "name": "S.J",
                "role": "ビジネス",
                "avatar": "SJ",
                "style": "戦略的で実用的、データドリブン",
                "topics": ["ビジネス", "マーケティング", "起業", "投資"],
                "tone": "プロフェッショナルで説得力がある"
            },
            "creative_designer": {
                "name": "A.M",
                "role": "クリエイティブ",
                "avatar": "AM",
                "style": "創造的でビジュアル重視",
                "topics": ["デザイン", "UI/UX", "アート", "クリエイティブ"],
                "tone": "インスピレーショナルで感性的"
            },
            "finance_analyst": {
                "name": "K.H",
                "role": "金融アナリスト",
                "avatar": "KH",
                "style": "分析的でデータ重視",
                "topics": ["投資", "仮想通貨", "経済", "資産運用"],
                "tone": "論理的で信頼性重視"
            }
        }
        
        # 記事データを保存
        self.articles_data = []
        
    def load_config(self, config_path: str) -> dict:
        """設定ファイルをロード"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # デフォルト設定
            default_config = {
                "github": {
                    "repository": "daito-iwa/ai-article-generator",
                    "token": os.environ.get('GITHUB_TOKEN', ''),
                    "branch": "main"
                },
                "openai": {
                    "api_key": os.environ.get('OPENAI_API_KEY', ''),
                    "model": "gpt-4o-mini",
                    "temperature": 0.8
                },
                "posting": {
                    "daily_posts": 3,
                    "post_times": ["09:00", "14:00", "19:00"],
                    "categories": ["プログラミング", "AI・機械学習", "ビジネス", "投資・副業", "デザイン"]
                }
            }
            
            # ディレクトリがなければ作成
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # 設定ファイルを保存
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            logging.info(f"デフォルト設定ファイルを作成しました: {config_path}")
            return default_config
    
    def get_trending_topics(self) -> List[str]:
        """Google Trendsから日本のトレンドトピックを取得"""
        try:
            # 日本のトレンドを取得
            trending_searches = self.pytrends.trending_searches(pn='japan')
            topics = trending_searches[0].tolist()[:10]  # 上位10件
            
            # プログラミング関連のキーワードも追加
            tech_keywords = ["ChatGPT", "Python", "React", "AI", "GitHub", "Docker", "JavaScript"]
            mixed_topics = topics[:5] + random.sample(tech_keywords, 2)
            
            logging.info(f"トレンドトピック取得: {mixed_topics}")
            return mixed_topics
            
        except Exception as e:
            logging.error(f"トレンド取得エラー: {e}")
            # フォールバックトピック
            return ["AI活用", "副業", "プログラミング学習", "投資", "リモートワーク"]
    
    def select_persona(self, topic: str) -> Dict:
        """トピックに基づいて適切なペルソナを選択"""
        topic_lower = topic.lower()
        
        # キーワードマッチング
        if any(keyword in topic_lower for keyword in ["プログラミング", "python", "javascript", "api", "開発"]):
            return self.personas["tech_engineer"]
        elif any(keyword in topic_lower for keyword in ["ビジネス", "起業", "マーケティング", "戦略"]):
            return self.personas["business_consultant"]
        elif any(keyword in topic_lower for keyword in ["投資", "株", "仮想通貨", "資産"]):
            return self.personas["finance_analyst"]
        elif any(keyword in topic_lower for keyword in ["デザイン", "ui", "ux", "クリエイティブ"]):
            return self.personas["creative_designer"]
        else:
            return self.personas["lifestyle_blogger"]
    
    def generate_article_with_ai(self, topic: str, persona: Dict) -> Dict:
        """AIを使って記事を生成"""
        prompt = f"""
あなたは「{persona['name']}」という{persona['role']}です。
以下の特徴で記事を書いてください：
- スタイル: {persona['style']}
- トーン: {persona['tone']}

トピック「{topic}」について、2000-3000文字程度の記事を書いてください。

記事の構成:
1. 魅力的なタイトル（SEO最適化、50文字以内）
2. 記事の概要（120文字程度）
3. 本文（Markdown形式）
   - 導入
   - メインコンテンツ（3-4セクション）
   - 実用的なコード例や具体例
   - まとめ
4. タグ（3-5個）

JSON形式で返してください：
{{
    "title": "記事タイトル",
    "summary": "記事の概要",
    "content": "Markdown形式の本文",
    "tags": ["タグ1", "タグ2", "タグ3"],
    "category": "カテゴリ名"
}}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config['openai']['model'],
                messages=[
                    {"role": "system", "content": "あなたは専門的な記事を書くライターです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config['openai']['temperature']
            )
            
            content = response.choices[0].message.content
            article_data = json.loads(content)
            
            # メタデータを追加
            article_data.update({
                "author": persona['name'],
                "author_role": persona['role'],
                "author_avatar": persona['avatar'],
                "publish_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "id": f"auto_{int(time.time())}",
                "views": random.randint(100, 1000),
                "likes": random.randint(10, 100),
                "comments": random.randint(0, 20)
            })
            
            return article_data
            
        except Exception as e:
            logging.error(f"記事生成エラー: {e}")
            return None
    
    def update_articles_json(self, new_article: Dict):
        """articles.jsonファイルを更新"""
        articles_file = "data/articles.json"
        
        # 既存の記事を読み込み
        if os.path.exists(articles_file):
            with open(articles_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        else:
            articles = []
        
        # 新しい記事を追加（最新を先頭に）
        articles.insert(0, new_article)
        
        # 最大100記事まで保持
        articles = articles[:100]
        
        # ファイルに保存
        os.makedirs(os.path.dirname(articles_file), exist_ok=True)
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logging.info(f"記事データを更新: {articles_file}")
    
    def update_github_files(self, article: Dict):
        """GitHubのファイルを更新"""
        headers = {
            "Authorization": f"token {self.github_token}",
            "Content-Type": "application/json"
        }
        
        # 1. articles.jsonを更新
        self.update_articles_json(article)
        
        # 2. GitHubにプッシュ
        articles_file_path = "data/articles.json"
        api_url = f"https://api.github.com/repos/{self.github_repo}/contents/{articles_file_path}"
        
        try:
            # 現在のファイルを取得
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                current_file = response.json()
                sha = current_file['sha']
            else:
                sha = None
            
            # ファイルの内容を準備
            with open(articles_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            # コミットデータ
            data = {
                "message": f"🤖 AI自動投稿: {article['title']}",
                "content": encoded_content,
                "branch": self.config['github']['branch']
            }
            
            if sha:
                data['sha'] = sha
            
            # ファイルを更新
            response = requests.put(api_url, json=data, headers=headers)
            
            if response.status_code in [200, 201]:
                logging.info(f"GitHubに記事を投稿しました: {article['title']}")
                return True
            else:
                logging.error(f"GitHub更新エラー: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"GitHub更新エラー: {e}")
            return False
    
    def post_article(self):
        """記事を投稿する（メイン処理）"""
        logging.info("=== 自動投稿開始 ===")
        
        # トレンドトピックを取得
        topics = self.get_trending_topics()
        
        if not topics:
            logging.error("トピックが取得できませんでした")
            return
        
        # ランダムにトピックを選択
        topic = random.choice(topics)
        
        # ペルソナを選択
        persona = self.select_persona(topic)
        
        logging.info(f"トピック: {topic}, ペルソナ: {persona['name']}")
        
        # 記事を生成
        article = self.generate_article_with_ai(topic, persona)
        
        if article:
            # GitHubに投稿
            success = self.update_github_files(article)
            
            if success:
                logging.info(f"✅ 投稿完了: {article['title']}")
                
                # 統計情報を記録
                self.articles_data.append({
                    "title": article['title'],
                    "author": article['author'],
                    "posted_at": datetime.now().isoformat()
                })
            else:
                logging.error("❌ 投稿失敗")
        else:
            logging.error("記事の生成に失敗しました")
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        logging.info("自動投稿スケジューラーを開始します")
        
        # 投稿時間を設定
        for post_time in self.config['posting']['post_times']:
            schedule.every().day.at(post_time).do(self.post_article)
        
        logging.info(f"投稿時間: {self.config['posting']['post_times']}")
        
        # 初回投稿（テスト用）
        if input("今すぐテスト投稿しますか？ (y/n): ").lower() == 'y':
            self.post_article()
        
        # スケジューラーを実行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック
    
    def generate_demo_articles(self, count: int = 5):
        """デモ用の記事を生成"""
        logging.info(f"デモ記事を{count}件生成します")
        
        demo_topics = [
            "ChatGPT APIの活用方法",
            "副業で月10万円稼ぐ方法",
            "React 18の新機能",
            "仮想通貨投資の基礎",
            "UI/UXデザインのトレンド"
        ]
        
        for i in range(count):
            topic = demo_topics[i % len(demo_topics)]
            persona = self.select_persona(topic)
            
            logging.info(f"記事 {i+1}/{count}: {topic}")
            
            article = self.generate_article_with_ai(topic, persona)
            if article:
                self.update_articles_json(article)
                time.sleep(2)  # API制限を考慮
        
        logging.info("デモ記事の生成が完了しました")


def main():
    """メイン関数"""
    print("""
╔══════════════════════════════════════════╗
║     GitHub Pages 自動投稿システム         ║
║     AI記事を毎日自動投稿                 ║
╚══════════════════════════════════════════╝
    """)
    
    # システム初期化
    auto_post = GitHubAutoPostSystem()
    
    # メニュー
    while True:
        print("\n1. 今すぐ記事を投稿")
        print("2. デモ記事を生成（5件）")
        print("3. 自動投稿スケジューラーを開始")
        print("4. 設定を確認")
        print("5. 終了")
        
        choice = input("\n選択してください (1-5): ")
        
        if choice == "1":
            auto_post.post_article()
        elif choice == "2":
            auto_post.generate_demo_articles(5)
        elif choice == "3":
            auto_post.run_scheduler()
        elif choice == "4":
            print("\n=== 現在の設定 ===")
            print(json.dumps(auto_post.config, ensure_ascii=False, indent=2))
        elif choice == "5":
            print("終了します")
            break
        else:
            print("無効な選択です")


if __name__ == "__main__":
    main()