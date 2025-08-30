#!/usr/bin/env python3
"""
WordPress自動デプロイメントシステム
ドメイン取得後、すぐに収益化可能なブログを構築
"""

import os
import json
import requests
import base64
from datetime import datetime
import sqlite3

class WordPressDeployment:
    """WordPress自動デプロイメント"""
    
    def __init__(self, site_url, username, password):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.password = password
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        
        # 認証ヘッダー
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
    
    def deploy_stealth_articles(self):
        """ステルスブログ記事をWordPressに自動投稿"""
        print("🚀 WordPress自動デプロイメント開始")
        
        # データベースから記事を取得
        articles = self._get_stealth_articles()
        
        deployed_count = 0
        for article in articles:
            try:
                # WordPress投稿データを作成
                post_data = self._create_wordpress_post(article)
                
                # WordPressに投稿
                response = requests.post(
                    f"{self.api_url}/posts",
                    headers=self.headers,
                    json=post_data
                )
                
                if response.status_code == 201:
                    post_id = response.json()['id']
                    print(f"✅ 投稿成功: {article['title']} (ID: {post_id})")
                    deployed_count += 1
                else:
                    print(f"❌ 投稿失敗: {article['title']}")
                    print(f"エラー: {response.text}")
                
            except Exception as e:
                print(f"❌ エラー: {e}")
        
        print(f"\n🎉 デプロイメント完了: {deployed_count}記事を投稿しました")
    
    def _get_stealth_articles(self):
        """ステルス記事をデータベースから取得"""
        db_path = "data/stealth_blog.db"
        
        if not os.path.exists(db_path):
            print("❌ ステルスブログデータベースが見つかりません")
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, content, persona_key, mood, published_at
            FROM stealth_articles 
            ORDER BY created_at DESC
        ''')
        
        articles = []
        for row in cursor.fetchall():
            title, content, persona, mood, published_at = row
            articles.append({
                'title': title,
                'content': content,
                'persona': persona,
                'mood': mood,
                'published_at': published_at
            })
        
        conn.close()
        return articles
    
    def _create_wordpress_post(self, article):
        """WordPress投稿データを作成"""
        
        # アフィリエイトリンクを挿入
        content_with_affiliate = self._insert_affiliate_links(article['content'])
        
        # SEO最適化されたコンテンツ
        optimized_content = self._optimize_for_seo(content_with_affiliate)
        
        # 投稿データ
        post_data = {
            'title': article['title'],
            'content': optimized_content,
            'status': 'publish',  # すぐに公開
            'author': 1,  # 管理者
            'excerpt': self._create_excerpt(article['content']),
            'meta': {
                '_yoast_wpseo_metadesc': self._create_meta_description(article['title']),
                '_yoast_wpseo_title': article['title']
            }
        }
        
        return post_data
    
    def _insert_affiliate_links(self, content):
        """アフィリエイトリンクを自動挿入"""
        
        # 高収益アフィリエイトリンク
        affiliate_links = {
            'エックスサーバー': {
                'url': 'https://px.a8.net/svt/ejp?a8mat=3HBQKR+5KQHX6+CO4+6BMG1',
                'text': '高速・安定のエックスサーバー'
            },
            'ConoHa WING': {
                'url': 'https://px.a8.net/svt/ejp?a8mat=3HBQKR+6HZGVM+50+2HHVZN',
                'text': '表示速度最速のConoHa WING'
            },
            '楽天カード': {
                'url': 'https://px.a8.net/svt/ejp?a8mat=3HBQKR+A1QHQY+2P4+66WOX',
                'text': '年会費無料の楽天カード'
            },
            'DMM FX': {
                'url': 'https://px.a8.net/svt/ejp?a8mat=3HBQKR+3YHHVM+1WP2+669JL',
                'text': '取引手数料無料のDMM FX'
            }
        }
        
        # コンテンツに自然にアフィリエイトリンクを挿入
        enhanced_content = content
        
        # 記事の中間と最後にアフィリエイトを挿入
        sections = enhanced_content.split('\n\n')
        if len(sections) > 3:
            # 中間に挿入
            middle_pos = len(sections) // 2
            affiliate_html = self._create_affiliate_box(
                affiliate_links['エックスサーバー']
            )
            sections.insert(middle_pos, affiliate_html)
            
            # 最後に挿入
            outro_affiliate = self._create_affiliate_box(
                affiliate_links['楽天カード']
            )
            sections.append(outro_affiliate)
        
        return '\n\n'.join(sections)
    
    def _create_affiliate_box(self, affiliate):
        """アフィリエイトボックスHTML生成"""
        return f'''
<div style="border: 2px solid #f0f0f0; padding: 20px; margin: 20px 0; border-radius: 10px; background: #fafafa;">
    <h4 style="color: #2c3e50; margin-bottom: 10px;">おすすめサービス</h4>
    <p style="margin-bottom: 15px;">当サイトでも利用している信頼性の高いサービスです。</p>
    <a href="{affiliate['url']}" target="_blank" style="display: inline-block; background: #3498db; color: white; padding: 12px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
        {affiliate['text']}
    </a>
</div>
'''
    
    def _optimize_for_seo(self, content):
        """SEO最適化処理"""
        
        # AdSense広告を記事中に自動挿入
        adsense_code = '''
<div style="text-align: center; margin: 30px 0;">
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-XXXXXXXXXXXXXXXXXX"
         data-ad-slot="XXXXXXXXXX"
         data-ad-format="auto"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</div>
'''
        
        # 記事の中間に広告を挿入
        sections = content.split('\n\n')
        if len(sections) > 4:
            middle = len(sections) // 2
            sections.insert(middle, adsense_code)
        
        return '\n\n'.join(sections)
    
    def _create_excerpt(self, content):
        """記事抜粋を作成"""
        # HTMLタグを除去して最初の120文字
        import re
        clean_text = re.sub(r'<[^>]+>', '', content)
        lines = clean_text.split('\n')
        
        excerpt = ''
        for line in lines:
            if line.strip() and not line.startswith('#'):
                excerpt = line.strip()[:120]
                break
        
        return excerpt + '...' if len(excerpt) == 120 else excerpt
    
    def _create_meta_description(self, title):
        """メタディスクリプション作成"""
        descriptions = [
            f"{title}について詳しく解説します。実体験をもとにしたおすすめの方法をご紹介。",
            f"{title}の最新情報をまとめました。初心者にも分かりやすく説明します。",
            f"{title}で失敗しないコツをお教えします。実際に試した結果をご報告。"
        ]
        
        import random
        return random.choice(descriptions)
    
    def setup_wordpress_automation(self):
        """WordPress自動化設定"""
        print("⚙️ WordPress自動化セットアップ")
        
        # 必要なプラグインリスト
        required_plugins = [
            'yoast-seo',           # SEO対策
            'wp-super-cache',      # キャッシュ
            'contact-form-7',      # お問い合わせフォーム
            'google-analytics',    # アナリティクス
            'advanced-ads',        # 広告管理
        ]
        
        print("推奨プラグイン:")
        for plugin in required_plugins:
            print(f"- {plugin}")
        
        # テーマ推奨設定
        recommended_settings = {
            'theme': 'Cocoon (無料・高機能)',
            'permalink': '/%postname%/',
            'timezone': 'Asia/Tokyo',
            'date_format': 'Y年n月j日',
            'start_of_week': 1  # 月曜日
        }
        
        print("\n推奨設定:")
        for setting, value in recommended_settings.items():
            print(f"- {setting}: {value}")

def main():
    """メイン処理"""
    print("🌐 WordPress自動デプロイメントシステム")
    print("=" * 50)
    
    # 設定例（実際のサイト情報に変更してください）
    SITE_CONFIG = {
        'url': 'https://your-domain.com',  # ← ここを変更
        'username': 'admin',               # ← ここを変更  
        'password': 'your-app-password'    # ← ここを変更
    }
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['deploy', 'setup', 'demo'], default='demo')
    parser.add_argument('--url', help='WordPressサイトURL')
    parser.add_argument('--user', help='WordPressユーザー名')
    parser.add_argument('--password', help='WordPressパスワード')
    
    args = parser.parse_args()
    
    if args.mode == 'demo':
        print("📝 デプロイメントデモ")
        print("\n実際のデプロイには以下を実行:")
        print("python3 wordpress_deployment.py --mode deploy --url https://your-site.com --user admin --password your-password")
        
        # セットアップガイドを表示
        deployer = WordPressDeployment("demo.com", "demo", "demo")
        deployer.setup_wordpress_automation()
        
    elif args.mode == 'setup':
        print("⚙️ WordPress設定ガイド")
        deployer = WordPressDeployment("demo.com", "demo", "demo")  
        deployer.setup_wordpress_automation()
        
    else:  # deploy
        if not all([args.url, args.user, args.password]):
            print("❌ エラー: --url, --user, --password を指定してください")
            return
        
        deployer = WordPressDeployment(args.url, args.user, args.password)
        deployer.deploy_stealth_articles()

if __name__ == "__main__":
    main()