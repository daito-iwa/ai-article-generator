#!/usr/bin/env python3
"""
GitHub Pages Note風サイト用自動投稿システム（Ollama版）
完全無料でAI記事を自動生成・投稿
"""

import json
import os
import random
import time
from datetime import datetime, timedelta
import requests
import base64
import schedule
import logging
import subprocess

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_post_ollama.log'),
        logging.StreamHandler()
    ]
)

class OllamaAutoPostSystem:
    def __init__(self):
        """Ollama自動投稿システムの初期化"""
        self.github_repo = "daito-iwa/ai-article-generator"
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        
        # Ollamaが起動しているか確認
        self.check_ollama()
        
        # 超大規模トレンドキーワード（全ジャンル対応）
        self.trend_keywords = {
            "エンタメ": [
                "芸能ニュース", "映画レビュー", "音楽トレンド", "アニメ", "ドラマ", "バラエティ",
                "YouTube", "TikTok", "インスタ映え", "アイドル", "K-POP", "Netflix",
                "ゲーム実況", "漫画", "小説", "舞台", "コンサート", "フェス"
            ],
            "ライフスタイル": [
                "健康管理", "ダイエット", "美容", "スキンケア", "ファッション", "料理レシピ",
                "旅行", "グルメ", "カフェ", "インテリア", "ガーデニング", "ペット",
                "子育て", "教育", "習い事", "趣味", "読書", "写真撮影"
            ],
            "ビジネス": [
                "副業", "転職", "起業", "投資", "株式", "仮想通貨", "不動産",
                "マーケティング", "営業", "リーダーシップ", "時間管理", "生産性向上",
                "リモートワーク", "フリーランス", "資格取得", "スキルアップ"
            ],
            "テクノロジー": [
                "AI", "ChatGPT", "プログラミング", "Python", "JavaScript", "React",
                "機械学習", "ブロックチェーン", "メタバース", "AR/VR", "IoT", "5G",
                "クラウド", "セキュリティ", "アプリ開発", "ウェブデザイン", "ガジェット"
            ],
            "社会・時事": [
                "政治", "経済", "環境問題", "社会問題", "国際情勢", "地域活性化",
                "SDGs", "働き方改革", "少子高齢化", "災害対策", "医療", "科学技術"
            ],
            "季節・イベント": [
                "春", "夏", "秋", "冬", "お正月", "バレンタイン", "ホワイトデー",
                "桜", "ゴールデンウィーク", "梅雨", "夏祭り", "お盆", "ハロウィン",
                "クリスマス", "年末年始", "入学式", "卒業式", "母の日", "父の日"
            ]
        }
        
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
                "topics": ["美容", "健康", "料理", "ファッション", "旅行", "グルメ"],
                "tone": "カジュアルで共感的"
            },
            "entertainment_writer": {
                "name": "E.R",
                "role": "エンタメ",
                "avatar": "ER",
                "style": "熱量があり、最新トレンドを詳しく解説",
                "topics": ["映画", "音楽", "アニメ", "ドラマ", "芸能", "ゲーム"],
                "tone": "エネルギッシュで親近感がある"
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
    
    def check_ollama(self):
        """Ollamaが起動しているか確認"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code != 200:
                raise Exception("Ollamaが起動していません")
            
            models = response.json().get('models', [])
            if not models:
                logging.warning("Ollamaモデルがインストールされていません。インストールします...")
                self.install_ollama_model()
            else:
                logging.info(f"利用可能なモデル: {[m['name'] for m in models]}")
                
        except requests.exceptions.ConnectionError:
            logging.error("Ollamaが起動していません。起動します...")
            self.start_ollama()
    
    def start_ollama(self):
        """Ollamaを起動"""
        try:
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info("Ollamaを起動しました。少し待ちます...")
            time.sleep(5)
            self.install_ollama_model()
        except Exception as e:
            logging.error(f"Ollamaの起動に失敗しました: {e}")
            logging.error("手動でOllamaを起動してください: ollama serve")
            exit(1)
    
    def install_ollama_model(self):
        """Ollamaモデルをインストール"""
        logging.info("llama3.2モデルをインストール中...")
        try:
            subprocess.run(["ollama", "pull", "llama3.2"], check=True)
            logging.info("モデルのインストールが完了しました")
        except Exception as e:
            logging.error(f"モデルのインストールに失敗しました: {e}")
    
    def get_trending_topics(self) -> list:
        """トレンドトピックを取得（全ジャンルからランダム選択）"""
        # 全ジャンルから合計10個選択
        all_topics = []
        for genre, topics in self.trend_keywords.items():
            all_topics.extend([(topic, genre) for topic in topics])
        
        # ランダムに10個選択
        selected = random.sample(all_topics, min(10, len(all_topics)))
        
        # 時期に応じた季節トピックを優先追加
        month = datetime.now().month
        seasonal_topics = []
        
        if month in [12, 1, 2]:  # 冬
            seasonal_topics = [("冬のファッション", "ライフスタイル"), ("お正月料理", "ライフスタイル")]
        elif month in [3, 4, 5]:  # 春
            seasonal_topics = [("桜スポット", "ライフスタイル"), ("新生活", "ライフスタイル")]
        elif month in [6, 7, 8]:  # 夏
            seasonal_topics = [("夏祭り", "季節・イベント"), ("夏バテ対策", "ライフスタイル")]
        elif month in [9, 10, 11]:  # 秋
            seasonal_topics = [("紅葉スポット", "ライフスタイル"), ("ハロウィン", "季節・イベント")]
        
        # 季節トピックがあれば優先して追加
        for topic, genre in seasonal_topics:
            if len(selected) < 10:
                selected.append((topic, genre))
        
        return selected
    
    def select_persona(self, topic: str) -> dict:
        """トピックに基づいて適切なペルソナを選択"""
        topic_lower = topic.lower()
        
        # キーワードマッチング
        if any(keyword in topic_lower for keyword in ["プログラミング", "python", "javascript", "api", "開発", "docker", "react"]):
            return self.personas["tech_engineer"]
        elif any(keyword in topic_lower for keyword in ["ビジネス", "起業", "マーケティング", "戦略", "dx"]):
            return self.personas["business_consultant"]
        elif any(keyword in topic_lower for keyword in ["投資", "株", "仮想通貨", "資産", "nft"]):
            return self.personas["finance_analyst"]
        elif any(keyword in topic_lower for keyword in ["デザイン", "ui", "ux", "クリエイティブ"]):
            return self.personas["creative_designer"]
        else:
            return self.personas["lifestyle_blogger"]
    
    def generate_article_with_ollama(self, topic: str, persona: dict) -> dict:
        """Ollamaを使って記事を生成"""
        prompt = f"""
あなたは「{persona['name']}」という{persona['role']}です。
以下の特徴で記事を書いてください：
- スタイル: {persona['style']}
- トーン: {persona['tone']}

「{topic}」について、2000文字程度の実用的な記事を書いてください。

以下のJSON形式で返してください：
{{
    "title": "魅力的なタイトル（50文字以内）",
    "summary": "記事の概要（120文字程度）",
    "content": "## はじめに\\n\\n記事の内容...\\n\\n## セクション1\\n\\n...\\n\\n## まとめ\\n\\n...",
    "tags": ["タグ1", "タグ2", "タグ3"],
    "category": "カテゴリ名"
}}

注意：
- contentはMarkdown形式で書く
- 実用的なコード例や具体例を含める
- SEOを意識したキーワードを自然に含める
"""
        
        try:
            # Ollama APIを呼び出し
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '{}')
                
                # JSONをパース
                try:
                    article_data = json.loads(content)
                except json.JSONDecodeError:
                    # JSONパースエラーの場合、手動で構造を作成
                    logging.warning("JSON解析エラー。デフォルト構造を使用します。")
                    article_data = self.create_default_article(topic, persona)
                
                # メタデータを追加
                article_data.update({
                    "author": persona['name'],
                    "author_role": persona['role'],
                    "author_avatar": persona['avatar'],
                    "publish_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "id": f"auto_{int(time.time())}",
                    "views": 0,
                    "likes": 0,
                    "comments": 0
                })
                
                return article_data
            else:
                logging.error(f"Ollama APIエラー: {response.status_code}")
                return self.create_default_article(topic, persona)
                
        except Exception as e:
            logging.error(f"記事生成エラー: {e}")
            return self.create_default_article(topic, persona)
    
    def create_default_article(self, topic: str, persona: dict) -> dict:
        """デフォルトの記事構造を作成"""
        return {
            "title": f"{topic}の基礎知識と実践方法",
            "summary": f"{topic}について、初心者にも分かりやすく解説します。実践的なテクニックと最新情報をお届けします。",
            "content": f"""## はじめに

{topic}は、現代において非常に重要なテーマです。この記事では、初心者の方にも分かりやすく、実践的な内容をお伝えします。

## {topic}の基本

まず、{topic}の基本的な概念から説明します。

### ポイント1：基礎を理解する

{topic}を理解するには、以下の点が重要です：

- 基本的な概念の理解
- 実践的なアプローチ
- 継続的な学習

## 実践的なテクニック

次に、実際に活用できるテクニックを紹介します。

### 1. 計画を立てる

しっかりとした計画が成功の鍵です。

### 2. 小さく始める

最初は小さなステップから始めましょう。

### 3. 継続する

継続は力なり。毎日少しずつ進めていきましょう。

## まとめ

{topic}について、基本から実践まで解説しました。ぜひ今日から始めてみてください。

質問やコメントがあれば、お気軽にどうぞ！""",
            "tags": [topic.split()[0], persona['topics'][0], "初心者向け"],
            "category": persona['topics'][0],
            "author": persona['name'],
            "author_role": persona['role'],
            "author_avatar": persona['avatar'],
            "publish_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "id": f"auto_{int(time.time())}",
            "views": 0,
            "likes": 0,
            "comments": 0
        }
    
    def update_articles_json(self, new_article: dict):
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
        return True
    
    def post_article(self):
        """記事を投稿する（メイン処理）"""
        logging.info("=== 自動投稿開始（Ollama版） ===")
        
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
        article = self.generate_article_with_ollama(topic, persona)
        
        if article:
            # JSONファイルを更新
            success = self.update_articles_json(article)
            
            if success:
                logging.info(f"✅ 投稿完了: {article['title']}")
                
                # GitHubへのコミット（オプション）
                if self.github_token:
                    self.commit_to_github(article)
            else:
                logging.error("❌ 投稿失敗")
        else:
            logging.error("記事の生成に失敗しました")
    
    def commit_to_github(self, article: dict):
        """GitHubにコミット（トークンがある場合のみ）"""
        try:
            # git add
            subprocess.run(["git", "add", "data/articles.json"], check=True)
            
            # git commit
            commit_message = f"🤖 AI自動投稿: {article['title']}"
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # git push
            subprocess.run(["git", "push", "origin", "main"], check=True)
            
            logging.info("GitHubへのプッシュが完了しました")
        except Exception as e:
            logging.warning(f"GitHubへのプッシュに失敗しました（手動でプッシュしてください）: {e}")
    
    def run_once(self):
        """1回だけ実行（テスト用）"""
        self.post_article()
    
    def run_continuous(self):
        """継続的に実行（1日3回：朝・昼・夜）"""
        logging.info("自動投稿を開始します（1日3回：8:00/14:00/20:00）")
        
        # スケジュール設定
        schedule.clear()  # 既存のスケジュールをクリア
        
        # 1日3回の投稿スケジュール
        schedule.every().day.at("08:00").do(self.post_article)  # 朝
        schedule.every().day.at("14:00").do(self.post_article)  # 昼
        schedule.every().day.at("20:00").do(self.post_article)  # 夜
        
        logging.info("📅 投稿スケジュール設定完了:")
        logging.info("   - 朝: 8:00")
        logging.info("   - 昼: 14:00") 
        logging.info("   - 夜: 20:00")
        
        # 初回実行（即座に投稿）
        logging.info("初回記事を投稿します...")
        self.post_article()
        
        # スケジュール実行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにスケジュールチェック
    
    def run_daily_burst(self):
        """1日限定で大量投稿（SEOブースト用）"""
        logging.info("🚀 1日限定大量投稿モード（SEOブースト）")
        logging.info("📊 2時間ごとに投稿（計12記事/日）")
        
        post_count = 0
        max_posts = 12
        
        while post_count < max_posts:
            logging.info(f"📝 投稿 {post_count + 1}/{max_posts}")
            self.post_article()
            post_count += 1
            
            if post_count < max_posts:
                logging.info("⏰ 2時間待機中...")
                time.sleep(2 * 60 * 60)  # 2時間待機
        
        logging.info("✅ 1日限定大量投稿完了！")


def main():
    """メイン関数"""
    print("""
╔══════════════════════════════════════════╗
║     ViralHub 自動投稿システム 2024       ║
║     SEO最適化でアクセス爆増！            ║
╚══════════════════════════════════════════╝
    """)
    
    print("🎯 モードを選択してください:")
    print("1️⃣  通常モード（1日3回投稿）")
    print("2️⃣  SEOブーストモード（1日12記事）") 
    print("3️⃣  テスト（1記事のみ）")
    
    try:
        mode = input("\n番号を入力 (1-3): ").strip()
        
        # システム初期化
        auto_post = OllamaAutoPostSystem()
        
        if mode == "1":
            print("\n🎯 通常モード開始（1日3回投稿）")
            print("⏰ 投稿時間: 8:00/14:00/20:00")
            print("📊 月間約90記事でSEO強化！")
            print("停止するには Ctrl+C を押してください\n")
            auto_post.run_continuous()
            
        elif mode == "2":
            print("\n🚀 SEOブーストモード開始！")
            print("⚡ 2時間ごとに投稿（1日12記事）")
            print("📈 検索上位獲得を目指します！")
            print("停止するには Ctrl+C を押してください\n")
            auto_post.run_daily_burst()
            
        elif mode == "3":
            print("\n🧪 テストモード（1記事のみ）")
            auto_post.run_once()
            print("✅ テスト完了！")
            
        else:
            print("❌ 無効な選択です。1-3の番号を入力してください。")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  自動投稿を停止しました。")
        print("📊 ViralHubで記事をチェック: https://daito-iwa.github.io/ai-article-generator/")
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        print(f"\n❌ エラー: {e}")


if __name__ == "__main__":
    main()