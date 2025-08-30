#!/usr/bin/env python3
"""
ステルス自動ブログシステム
完全に人間が書いているように見せる高度な自動化
"""

import os
import sys
import json
import random
import time
import sqlite3
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class StealthBlogAutomation:
    """ステルス自動ブログシステム"""
    
    def __init__(self):
        self.setup_logging()
        self.personas = self._load_personas()
        self.current_persona = random.choice(list(self.personas.keys()))
        self.db_path = "data/stealth_blog.db"
        self.init_database()
    
    def setup_logging(self):
        """ログ設定"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - STEALTH - %(message)s',
            handlers=[
                logging.FileHandler('logs/stealth_blog.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_personas(self) -> Dict:
        """複数のブロガー人格を定義"""
        return {
            "tech_engineer": {
                "name": "T.K",
                "age": 28,
                "job": "フリーランスエンジニア",
                "personality": "論理的、実践的、親しみやすい",
                "writing_patterns": [
                    "実際に〇〇を試してみました",
                    "個人的な経験ですが",
                    "エンジニア目線で言うと",
                    "コードも公開しているので参考に"
                ],
                "post_times": ["09:30", "19:45", "22:30"],
                "topics": ["プログラミング", "AI", "副業", "技術トレンド"],
                "tone_variations": {
                    "excited": "これは本当にすごい！",
                    "thoughtful": "じっくり考えてみると...",
                    "casual": "最近よく聞かれるので書いてみました",
                    "professional": "技術的な観点から解説します"
                }
            },
            
            "lifestyle_mom": {
                "name": "M.Y",
                "age": 32,
                "job": "育児しながらブログ運営",
                "personality": "共感的、実用的、暖かい",
                "writing_patterns": [
                    "子育て中のママ目線で",
                    "実際にやってみた結果",
                    "忙しいママでもできる",
                    "家族も喜んでくれました"
                ],
                "post_times": ["10:00", "14:30", "21:00"],
                "topics": ["育児", "節約", "投資", "ライフハック"],
                "tone_variations": {
                    "encouraging": "一緒に頑張りましょう！",
                    "sharing": "私の経験をシェアします",
                    "practical": "実際に役立った方法",
                    "grateful": "皆さんのおかげです"
                }
            },
            
            "business_consultant": {
                "name": "S.J",
                "age": 35,
                "job": "経営コンサルタント",
                "personality": "分析的、戦略的、信頼性重視",
                "writing_patterns": [
                    "データを見ると明らかです",
                    "戦略的に考えると",
                    "事例を見ると",
                    "結果を数字で示すと"
                ],
                "post_times": ["07:00", "12:00", "18:00"],
                "topics": ["ビジネス", "投資", "起業", "マーケティング"],
                "tone_variations": {
                    "analytical": "分析してみましょう",
                    "strategic": "戦略的なアプローチ",
                    "results_focused": "実際の成果は...",
                    "advisory": "私のアドバイスとして"
                }
            },
            
            "finance_expert": {
                "name": "K.H",
                "age": 40,
                "job": "金融アドバイザー",
                "personality": "慎重、分析的、長期視点",
                "writing_patterns": [
                    "リスク管理の観点から",
                    "長期的に見ると",
                    "実際の運用データでは",
                    "安全性を重視すると"
                ],
                "post_times": ["08:00", "13:30", "20:00"],
                "topics": ["投資", "資産運用", "保険", "税金"],
                "tone_variations": {
                    "cautious": "慎重に検討すると",
                    "data_driven": "データから見ると",
                    "protective": "リスクを抑えるなら",
                    "educational": "基本から説明すると"
                }
            },
            
            "health_blogger": {
                "name": "R.N",
                "age": 29,
                "job": "健康管理士",
                "personality": "健康意識、実践的、優しい",
                "writing_patterns": [
                    "健康の観点から",
                    "実際に試してみると",
                    "体調管理として",
                    "継続することで"
                ],
                "post_times": ["06:30", "12:30", "19:30"],
                "topics": ["健康", "ダイエット", "運動", "栄養"],
                "tone_variations": {
                    "encouraging": "一緒に頑張りましょう",
                    "scientific": "医学的に見ると",
                    "practical": "日常で実践できる",
                    "supportive": "無理せず続けることが大切"
                }
            },
            
            "creative_freelancer": {
                "name": "A.M",
                "age": 26,
                "job": "フリーランスデザイナー",
                "personality": "創造的、自由、感性豊か",
                "writing_patterns": [
                    "デザイナー目線で",
                    "クリエイティブな発想で",
                    "美的センスから言うと",
                    "表現方法として"
                ],
                "post_times": ["10:00", "15:00", "22:00"],
                "topics": ["デザイン", "アート", "副業", "クリエイティブ"],
                "tone_variations": {
                    "artistic": "美的な観点から",
                    "innovative": "新しいアプローチとして",
                    "expressive": "表現力を高めるには",
                    "inspiring": "インスピレーションを得るために"
                }
            },
            
            "travel_writer": {
                "name": "Y.S",
                "age": 33,
                "job": "旅行ライター",
                "personality": "冒険的、好奇心旺盛、国際的",
                "writing_patterns": [
                    "旅先での経験から",
                    "現地で学んだことは",
                    "文化の違いを感じたのは",
                    "実際に訪れてみると"
                ],
                "post_times": ["09:00", "16:00", "21:30"],
                "topics": ["旅行", "文化", "語学", "ライフスタイル"],
                "tone_variations": {
                    "adventurous": "新しい発見として",
                    "cultural": "文化的な視点から",
                    "experiential": "体験を通して",
                    "global": "世界的に見ると"
                }
            },
            
            "student_blogger": {
                "name": "H.T",
                "age": 22,
                "job": "大学生",
                "personality": "学習意欲、若い視点、コスト意識",
                "writing_patterns": [
                    "学生の立場から",
                    "勉強しながら気づいたのは",
                    "同世代の友人と話していて",
                    "将来を考えると"
                ],
                "post_times": ["11:00", "17:00", "23:00"],
                "topics": ["勉強", "就活", "節約", "将来設計"],
                "tone_variations": {
                    "youthful": "若い世代として",
                    "learning": "学びながら感じるのは",
                    "budget_conscious": "お金をかけずに",
                    "future_focused": "将来のために"
                }
            }
        }
    
    def init_database(self):
        """データベース初期化"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ステルス記事テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stealth_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                persona_key TEXT NOT NULL,
                mood TEXT,
                writing_session_duration INTEGER,
                published_at TIMESTAMP,
                engagement_score INTEGER DEFAULT 0,
                authenticity_markers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 投稿履歴テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posting_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                persona_key TEXT,
                post_date DATE,
                post_time TIME,
                topics_covered TEXT,
                mood TEXT,
                interaction_type TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_stealth_article(self, topic_hint: str = None) -> Dict:
        """完全にステルスな記事を生成"""
        
        # 今日の気分とコンディションを決定
        mood = self._determine_daily_mood()
        persona = self.personas[self.current_persona]
        
        # トピックを自然に選択
        topic = topic_hint or self._select_natural_topic(persona, mood)
        
        # ライティングセッションをシミュレート
        writing_session = self._simulate_writing_session(persona, mood)
        
        # 記事を段階的に生成（人間らしく）
        article = self._generate_article_stages(topic, persona, mood, writing_session)
        
        # authenticity markersを追加
        article = self._add_authenticity_markers(article, persona, writing_session)
        
        # データベースに保存
        self._save_stealth_article(article, persona['name'], mood, writing_session)
        
        self.logger.info(f"ステルス記事生成完了: {article['title']} (気分: {mood})")
        
        return article
    
    def _determine_daily_mood(self) -> str:
        """その日の気分を決定（リアルな要因を考慮）"""
        
        # 曜日による気分変動
        weekday = datetime.now().weekday()
        mood_by_day = {
            0: ["motivated", "fresh_start"],  # 月曜日
            1: ["focused", "productive"],      # 火曜日  
            2: ["steady", "mid_week"],        # 水曜日
            3: ["tired", "pushing_through"],   # 木曜日
            4: ["relieved", "weekend_prep"],   # 金曜日
            5: ["relaxed", "weekend_mode"],    # 土曜日
            6: ["reflective", "prep_mode"]     # 日曜日
        }
        
        base_moods = mood_by_day.get(weekday, ["neutral"])
        
        # ランダム要因も追加
        random_moods = ["energetic", "thoughtful", "nostalgic", "excited", "calm"]
        
        # 80%で曜日ベース、20%でランダム
        if random.random() < 0.8:
            return random.choice(base_moods)
        else:
            return random.choice(random_moods)
    
    def _select_natural_topic(self, persona: Dict, mood: str) -> str:
        """自然なトピック選択"""
        
        # その人の専門分野から選択
        base_topics = persona["topics"]
        
        # 気分によってトピックを調整
        mood_topic_mapping = {
            "motivated": ["新しい挑戦", "スキルアップ", "目標達成"],
            "thoughtful": ["深い考察", "振り返り", "学びの共有"],
            "excited": ["最新情報", "新発見", "おすすめ"],
            "tired": ["効率化", "時短術", "楽になる方法"],
            "nostalgic": ["経験談", "失敗から学んだこと", "昔との比較"]
        }
        
        mood_topics = mood_topic_mapping.get(mood, ["日常の気づき"])
        
        # トピックを組み合わせて自然なものを作成
        base = random.choice(base_topics)
        mood_element = random.choice(mood_topics)
        
        topic_patterns = [
            f"{base}で{mood_element}",
            f"{mood_element}から見る{base}",
            f"{base}初心者が知るべき{mood_element}"
        ]
        
        return random.choice(topic_patterns)
    
    def _simulate_writing_session(self, persona: Dict, mood: str) -> Dict:
        """人間らしいライティングセッションをシミュレート"""
        
        # 書く時間帯の決定
        preferred_times = persona["post_times"]
        current_time = datetime.now()
        
        # その人らしい書く時間を選択
        session_start = random.choice(preferred_times)
        
        # 気分による書く時間の変動
        mood_duration_mapping = {
            "motivated": (45, 90),      # やる気がある時は長め
            "tired": (20, 40),          # 疲れている時は短め
            "excited": (30, 60),        # 興奮している時は集中
            "thoughtful": (60, 120),    # 深く考える時は時間をかける
        }
        
        min_duration, max_duration = mood_duration_mapping.get(mood, (30, 60))
        writing_duration = random.randint(min_duration, max_duration)
        
        # 休憩パターン
        break_count = writing_duration // 25  # ポモドーロ風
        
        return {
            "start_time": session_start,
            "duration_minutes": writing_duration,
            "break_count": break_count,
            "mood": mood,
            "interruptions": random.randint(0, 2)  # 現実的な中断
        }
    
    def _generate_article_stages(self, topic: str, persona: Dict, mood: str, session: Dict) -> Dict:
        """段階的に記事を生成（人間の書き方をシミュレート）"""
        
        # 第1段階: アウトライン
        outline = self._create_human_outline(topic, persona, mood)
        
        # 第2段階: 導入文
        intro = self._write_natural_intro(topic, persona, mood)
        
        # 第3段階: 本文
        body = self._write_natural_body(topic, persona, mood, outline)
        
        # 第4段階: まとめ
        conclusion = self._write_natural_conclusion(topic, persona, mood)
        
        # タイトルを最後に決定（人間らしい流れ）
        title = self._create_catchy_title(topic, persona, mood, intro + body)
        
        return {
            "title": title,
            "content": f"{intro}\n\n{body}\n\n{conclusion}",
            "outline": outline,
            "writing_session": session,
            "persona": persona['name'],
            "mood": mood,
            "topic": topic
        }
    
    def _create_human_outline(self, topic: str, persona: Dict, mood: str) -> List[str]:
        """人間らしいアウトライン作成"""
        
        # その人らしいアプローチ
        if "engineer" in persona['name'].lower():
            outline_style = [
                "問題の定義",
                "技術的な解決策",
                "実装方法",
                "実際の結果",
                "今後の改善点"
            ]
        elif "ママ" in persona['name']:
            outline_style = [
                "きっかけ・動機",
                "実際にやってみた方法",
                "子育てとの両立",
                "家族の反応",
                "他のママへのアドバイス"
            ]
        else:  # ビジネス系
            outline_style = [
                "現状の問題認識",
                "市場データの分析",
                "戦略的なアプローチ",
                "実装プロセス",
                "成果と今後の展望"
            ]
        
        return outline_style
    
    def _write_natural_intro(self, topic: str, persona: Dict, mood: str) -> str:
        """自然な導入文を作成"""
        
        # その人らしい書き出し
        persona_intros = persona["writing_patterns"]
        mood_modifier = persona["tone_variations"].get(mood, "")
        
        # 時事的な要素を追加
        season = self._get_seasonal_context()
        time_context = self._get_time_context()
        
        intros = [
            f"こんにちは。{season}",
            f"{time_context}、{random.choice(persona_intros)}。",
            f"{mood_modifier} 今回は{topic}について書いてみます。"
        ]
        
        return "\n\n".join(intros)
    
    def _write_natural_body(self, topic: str, persona: Dict, mood: str, outline: List[str]) -> str:
        """自然な本文を作成"""
        
        body_sections = []
        
        for i, section_title in enumerate(outline):
            # 各セクションを人間らしく展開
            section_content = f"## {section_title}\n\n"
            
            # その人らしい体験談を挿入
            personal_experience = random.choice(persona["writing_patterns"])
            section_content += f"{personal_experience}、{section_title.lower()}について考えてみました。\n\n"
            
            # 具体的な内容（デモ版）
            section_content += f"{section_title}のポイントは以下の通りです：\n\n"
            section_content += f"1. 基本的な考え方\n"
            section_content += f"2. 実践的なアプローチ\n"
            section_content += f"3. 注意すべき点\n\n"
            
            # 人間らしい感情的なコメント
            if i == len(outline) // 2:  # 中間で感想を挟む
                emotions = [
                    "ここまで書いていて思ったのですが、",
                    "実際にやってみると分かるのですが、",
                    "最初は不安でしたが、"
                ]
                section_content += f"{random.choice(emotions)}意外と簡単でした。\n\n"
            
            body_sections.append(section_content)
        
        return "\n".join(body_sections)
    
    def _write_natural_conclusion(self, topic: str, persona: Dict, mood: str) -> str:
        """自然なまとめを作成"""
        
        conclusions = [
            f"## まとめ\n\n{topic}について、私の体験をもとに書いてみました。",
            f"最後まで読んでいただき、ありがとうございました！",
            f"何か質問があれば、コメントで教えてください。",
            f"次回も役立つ情報をシェアしたいと思います。"
        ]
        
        return "\n\n".join(conclusions)
    
    def _create_catchy_title(self, topic: str, persona: Dict, mood: str, content: str) -> str:
        """魅力的なタイトルを作成"""
        
        # その人らしいタイトルパターン
        title_patterns = {
            "tech_engineer": [
                f"【実装済み】{topic}の効率的な方法",
                f"{topic}で躓いた話と解決策",
                f"エンジニアが選ぶ{topic}のベストプラクティス"
            ],
            "lifestyle_mom": [
                f"【ママ目線】{topic}を3ヶ月試した結果",
                f"忙しいママでもできる{topic}",
                f"{topic}で家族が喜んだ話"
            ],
            "business_consultant": [
                f"【データ分析】{topic}の市場動向",
                f"{topic}で売上が20%向上した事例",
                f"経営者が知るべき{topic}の真実"
            ]
        }
        
        # 現在のペルソナに合わせてタイトル選択
        persona_key = [k for k, v in self.personas.items() if v['name'] == persona['name']][0]
        patterns = title_patterns.get(persona_key, [f"{topic}について考えてみた"])
        
        return random.choice(patterns)
    
    def _add_authenticity_markers(self, article: Dict, persona: Dict, session: Dict) -> Dict:
        """authenticity markers（真正性の証拠）を追加"""
        
        markers = []
        
        # 時間的なリアリティ
        if session["duration_minutes"] > 60:
            markers.append("長文記事")
            article["content"] += "\n\n長くなってしまいましたが、最後まで読んでいただきありがとうございます！"
        
        # 中断の痕跡
        if session["interruptions"] > 0:
            article["content"] = article["content"].replace("実際に", "（子供が起きたので中断😅）実際に", 1)
        
        # その人らしい癖
        personal_quirks = {
            "tech_engineer": ["コードも載せようと思いましたが", "GitHubに上げておきます"],
            "lifestyle_mom": ["家族に相談したところ", "みんなも気に入ってくれました"],
            "business_consultant": ["事例を見ると", "数字で示すと"],
            "finance_expert": ["リスクを考慮すると", "ポートフォリオに組み入れる際は"],
            "health_blogger": ["実際に体験してみて", "継続が一番大切です"],
            "creative_freelancer": ["作品として残したい", "クリエイティブな視点で"],
            "travel_writer": ["現地で体験したことですが", "文化の違いを感じました"],
            "student_blogger": ["同期の友人たちと", "将来を考えると不安ですが"]
        }
        
        persona_key = [k for k, v in self.personas.items() if v['name'] == persona['name']][0]
        quirks = personal_quirks.get(persona_key, [])
        
        if quirks:
            quirk = random.choice(quirks)
            article["content"] += f"\n\n{quirk}、この内容はかなり効果的だと思います。"
        
        article["authenticity_markers"] = markers
        return article
    
    def _get_seasonal_context(self) -> str:
        """季節的なコンテキスト"""
        month = datetime.now().month
        
        seasonal_contexts = {
            12: "年末でバタバタしていますが",
            1: "新年あけましておめでとうございます",
            2: "寒い日が続きますね",
            3: "春が近づいてきましたね",
            4: "新年度が始まりましたね",
            5: "GWはいかがでしたか？",
            6: "梅雨の季節ですね",
            7: "夏本番ですね",
            8: "暑い日が続きますね",
            9: "秋の気配を感じます",
            10: "涼しくなってきましたね",
            11: "紅葉が美しい季節ですね"
        }
        
        return seasonal_contexts.get(month, "")
    
    def _get_time_context(self) -> str:
        """時間的なコンテキスト"""
        hour = datetime.now().hour
        
        if 5 <= hour < 10:
            return "朝の時間を使って"
        elif 10 <= hour < 14:
            return "午前中に"
        elif 14 <= hour < 18:
            return "午後の時間に"
        elif 18 <= hour < 22:
            return "夜の時間を使って"
        else:
            return "遅い時間ですが"
    
    def _save_stealth_article(self, article: Dict, persona_name: str, mood: str, session: Dict):
        """ステルス記事をデータベースに保存"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # スラッグ生成
        slug = article['title'].lower().replace(' ', '-').replace('【', '').replace('】', '')
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')[:50]
        
        cursor.execute('''
            INSERT INTO stealth_articles (
                slug, title, content, persona_key, mood, 
                writing_session_duration, published_at, authenticity_markers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            slug,
            article['title'],
            article['content'],
            self.current_persona,
            mood,
            session['duration_minutes'],
            datetime.now(),
            json.dumps(article.get('authenticity_markers', []))
        ))
        
        conn.commit()
        conn.close()
    
    def setup_stealth_automation(self):
        """ステルス自動化のスケジュール設定"""
        
        # 自然な投稿パターンを設定
        posting_patterns = [
            {"day": "monday", "time": "09:30", "persona": "tech_engineer"},
            {"day": "monday", "time": "13:30", "persona": "finance_expert"},
            {"day": "tuesday", "time": "06:30", "persona": "health_blogger"},
            {"day": "tuesday", "time": "19:45", "persona": "creative_freelancer"},  
            {"day": "wednesday", "time": "10:00", "persona": "lifestyle_mom"},
            {"day": "wednesday", "time": "16:00", "persona": "travel_writer"},
            {"day": "thursday", "time": "11:00", "persona": "student_blogger"},
            {"day": "thursday", "time": "21:00", "persona": "business_consultant"},
            {"day": "friday", "time": "07:00", "persona": "finance_expert"},
            {"day": "friday", "time": "15:00", "persona": "creative_freelancer"},
            {"day": "saturday", "time": "09:00", "persona": "travel_writer"},
            {"day": "saturday", "time": "18:00", "persona": "health_blogger"},
            {"day": "sunday", "time": "12:30", "persona": "lifestyle_mom"},
            {"day": "sunday", "time": "23:00", "persona": "student_blogger"},
        ]
        
        # スケジュール登録
        for pattern in posting_patterns:
            getattr(schedule.every(), pattern["day"]).at(pattern["time"]).do(
                self._scheduled_post, pattern["persona"]
            )
        
        self.logger.info("ステルス自動化スケジュール設定完了")
    
    def _scheduled_post(self, persona_key: str):
        """スケジュール投稿"""
        self.current_persona = persona_key
        
        # 20%の確率で投稿をスキップ（人間らしい不規則性）
        if random.random() < 0.2:
            self.logger.info(f"投稿スキップ（人間らしい不規則性）: {persona_key}")
            return
        
        # 記事生成・投稿
        article = self.generate_stealth_article()
        self.logger.info(f"自動投稿完了: {article['title']}")

def main():
    """メイン処理"""
    print("🕵️ ステルス自動ブログシステム")
    print("=" * 50)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['generate', 'schedule', 'demo'], default='demo')
    parser.add_argument('--persona', choices=['tech_engineer', 'lifestyle_mom', 'business_consultant'])
    
    args = parser.parse_args()
    
    stealth = StealthBlogAutomation()
    
    if args.mode == 'generate':
        # 1記事生成
        if args.persona:
            stealth.current_persona = args.persona
        
        article = stealth.generate_stealth_article()
        print(f"\n✅ 生成完了:")
        print(f"タイトル: {article['title']}")
        print(f"ペルソナ: {article['persona']}")
        print(f"気分: {article['mood']}")
        
    elif args.mode == 'schedule':
        # 自動化スケジュール開始
        stealth.setup_stealth_automation()
        print("⏰ ステルス自動化を開始しました")
        print("停止: Ctrl+C")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    else:  # demo
        # デモ記事を6つ生成（多様な投稿者）
        print("📝 デモ記事を生成中...")
        
        personas = ['tech_engineer', 'lifestyle_mom', 'business_consultant', 
                   'finance_expert', 'health_blogger', 'creative_freelancer']
        for persona in personas:
            stealth.current_persona = persona
            article = stealth.generate_stealth_article()
            print(f"✅ {article['persona']}: {article['title']}")
            time.sleep(2)  # 人間らしい間隔

if __name__ == "__main__":
    main()