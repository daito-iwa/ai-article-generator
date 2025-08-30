#!/usr/bin/env python3
"""
自動投稿モジュール
WordPress REST API、その他CMSへの記事投稿機能を提供
"""

import json
import logging
import time
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import requests
from requests.auth import HTTPBasicAuth
import schedule
from PIL import Image
import io

logger = logging.getLogger(__name__)

@dataclass
class PublishConfig:
    """投稿設定"""
    status: str = "draft"  # draft, publish, private
    category_ids: List[int] = None
    tag_ids: List[int] = None
    featured_media_id: Optional[int] = None
    excerpt: str = ""
    author_id: int = 1
    schedule_date: Optional[str] = None  # ISO format
    allow_comments: bool = True

@dataclass
class PublishResult:
    """投稿結果"""
    success: bool
    post_id: Optional[int]
    post_url: Optional[str]
    message: str
    published_at: str
    platform: str

@dataclass
class MediaFile:
    """メディアファイル情報"""
    filename: str
    content: bytes
    mime_type: str
    alt_text: str = ""
    caption: str = ""

class WordPressPublisher:
    """WordPress自動投稿クラス"""
    
    def __init__(self, 
                 site_url: str, 
                 username: str, 
                 password: str,
                 timeout: int = 30):
        """
        初期化
        
        Args:
            site_url: WordPressサイトURL
            username: ユーザー名
            password: アプリケーションパスワード
            timeout: タイムアウト時間
        """
        self.site_url = site_url.rstrip('/')
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.auth = HTTPBasicAuth(username, password)
        self.timeout = timeout
        self.session = requests.Session()
        self.session.auth = self.auth
        
        # API接続テスト
        if not self._test_connection():
            raise ConnectionError("WordPress APIへの接続に失敗しました")
    
    def _test_connection(self) -> bool:
        """API接続テスト"""
        try:
            response = self.session.get(f"{self.api_base}/users/me", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"WordPress API接続テストエラー: {e}")
            return False
    
    def publish_article(self, 
                       title: str, 
                       content: str,
                       config: PublishConfig = PublishConfig()) -> PublishResult:
        """
        記事を投稿
        
        Args:
            title: 記事タイトル
            content: 記事内容
            config: 投稿設定
            
        Returns:
            PublishResult
        """
        try:
            logger.info(f"WordPress投稿開始: {title}")
            
            # 投稿データ準備
            post_data = {
                'title': title,
                'content': content,
                'status': config.status,
                'excerpt': config.excerpt,
                'author': config.author_id,
                'comment_status': 'open' if config.allow_comments else 'closed'
            }
            
            # カテゴリ設定
            if config.category_ids:
                post_data['categories'] = config.category_ids
            
            # タグ設定
            if config.tag_ids:
                post_data['tags'] = config.tag_ids
            
            # アイキャッチ画像設定
            if config.featured_media_id:
                post_data['featured_media'] = config.featured_media_id
            
            # 投稿日時設定
            if config.schedule_date:
                post_data['date'] = config.schedule_date
                if config.status == 'draft':
                    post_data['status'] = 'future'
            
            # API経由で投稿
            response = self.session.post(
                f"{self.api_base}/posts",
                json=post_data,
                timeout=self.timeout
            )
            
            if response.status_code in [201, 200]:
                post_data = response.json()
                post_id = post_data.get('id')
                post_url = post_data.get('link')
                
                logger.info(f"WordPress投稿成功: ID={post_id}")
                
                return PublishResult(
                    success=True,
                    post_id=post_id,
                    post_url=post_url,
                    message="投稿が成功しました",
                    published_at=datetime.now().isoformat(),
                    platform="WordPress"
                )
            else:
                error_msg = f"投稿失敗: {response.status_code} - {response.text}"
                logger.error(error_msg)
                
                return PublishResult(
                    success=False,
                    post_id=None,
                    post_url=None,
                    message=error_msg,
                    published_at=datetime.now().isoformat(),
                    platform="WordPress"
                )
                
        except Exception as e:
            error_msg = f"WordPress投稿エラー: {e}"
            logger.error(error_msg)
            
            return PublishResult(
                success=False,
                post_id=None,
                post_url=None,
                message=error_msg,
                published_at=datetime.now().isoformat(),
                platform="WordPress"
            )
    
    def upload_media(self, media_file: MediaFile) -> Optional[int]:
        """
        メディアファイルをアップロード
        
        Args:
            media_file: アップロードするメディアファイル
            
        Returns:
            アップロードされたメディアID or None
        """
        try:
            logger.info(f"メディアアップロード開始: {media_file.filename}")
            
            # ファイルデータ準備
            files = {
                'file': (media_file.filename, media_file.content, media_file.mime_type)
            }
            
            # メタデータ
            data = {
                'alt_text': media_file.alt_text,
                'caption': media_file.caption
            }
            
            # メディアアップロード
            response = self.session.post(
                f"{self.api_base}/media",
                files=files,
                data=data,
                timeout=self.timeout * 2  # アップロードは時間がかかる
            )
            
            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data.get('id')
                logger.info(f"メディアアップロード成功: ID={media_id}")
                return media_id
            else:
                logger.error(f"メディアアップロード失敗: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"メディアアップロードエラー: {e}")
            return None
    
    def get_categories(self) -> List[Dict]:
        """カテゴリ一覧取得"""
        try:
            response = self.session.get(f"{self.api_base}/categories", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"カテゴリ取得エラー: {e}")
            return []
    
    def get_tags(self) -> List[Dict]:
        """タグ一覧取得"""
        try:
            response = self.session.get(f"{self.api_base}/tags", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"タグ取得エラー: {e}")
            return []
    
    def create_category(self, name: str, description: str = "", parent: int = 0) -> Optional[int]:
        """
        新しいカテゴリを作成
        
        Args:
            name: カテゴリ名
            description: 説明
            parent: 親カテゴリID
            
        Returns:
            作成されたカテゴリID or None
        """
        try:
            data = {
                'name': name,
                'description': description,
                'parent': parent
            }
            
            response = self.session.post(
                f"{self.api_base}/categories",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                category_data = response.json()
                return category_data.get('id')
            return None
            
        except Exception as e:
            logger.error(f"カテゴリ作成エラー: {e}")
            return None
    
    def create_tag(self, name: str, description: str = "") -> Optional[int]:
        """
        新しいタグを作成
        
        Args:
            name: タグ名
            description: 説明
            
        Returns:
            作成されたタグID or None
        """
        try:
            data = {
                'name': name,
                'description': description
            }
            
            response = self.session.post(
                f"{self.api_base}/tags",
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 201:
                tag_data = response.json()
                return tag_data.get('id')
            return None
            
        except Exception as e:
            logger.error(f"タグ作成エラー: {e}")
            return None
    
    def update_post(self, post_id: int, updates: Dict) -> bool:
        """
        投稿を更新
        
        Args:
            post_id: 投稿ID
            updates: 更新内容
            
        Returns:
            更新成功可否
        """
        try:
            response = self.session.post(
                f"{self.api_base}/posts/{post_id}",
                json=updates,
                timeout=self.timeout
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"投稿更新エラー: {e}")
            return False

class UnsplashImageFetcher:
    """Unsplash画像取得クラス"""
    
    def __init__(self, access_key: str):
        """
        初期化
        
        Args:
            access_key: Unsplash APIアクセスキー
        """
        self.access_key = access_key
        self.api_base = "https://api.unsplash.com"
    
    def fetch_image_for_keyword(self, 
                               keyword: str, 
                               width: int = 1200, 
                               height: int = 800) -> Optional[MediaFile]:
        """
        キーワードに基づいて画像を取得
        
        Args:
            keyword: 検索キーワード
            width: 画像幅
            height: 画像高さ
            
        Returns:
            MediaFile or None
        """
        try:
            logger.info(f"Unsplash画像検索: {keyword}")
            
            # 画像検索
            search_url = f"{self.api_base}/search/photos"
            params = {
                'query': keyword,
                'per_page': 1,
                'orientation': 'landscape'
            }
            headers = {
                'Authorization': f'Client-ID {self.access_key}'
            }
            
            response = requests.get(search_url, params=params, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"Unsplash検索エラー: {response.status_code}")
                return None
            
            data = response.json()
            if not data.get('results'):
                logger.warning(f"画像が見つかりません: {keyword}")
                return None
            
            photo = data['results'][0]
            
            # 画像URL取得
            image_url = photo['urls']['raw'] + f"&w={width}&h={height}&fit=crop"
            
            # 画像ダウンロード
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error("画像ダウンロードエラー")
                return None
            
            # ファイル名とalt属性生成
            filename = f"{keyword.replace(' ', '_')}.jpg"
            alt_text = photo.get('alt_description', keyword)
            caption = f"Photo by {photo['user']['name']} on Unsplash"
            
            return MediaFile(
                filename=filename,
                content=image_response.content,
                mime_type='image/jpeg',
                alt_text=alt_text,
                caption=caption
            )
            
        except Exception as e:
            logger.error(f"Unsplash画像取得エラー: {e}")
            return None

class PublishingScheduler:
    """投稿スケジューラークラス"""
    
    def __init__(self, publisher: WordPressPublisher):
        """
        初期化
        
        Args:
            publisher: WordPressPublisher インスタンス
        """
        self.publisher = publisher
        self.scheduled_posts = []
    
    def schedule_post(self, 
                     title: str, 
                     content: str, 
                     config: PublishConfig, 
                     publish_time: str):
        """
        投稿をスケジュール
        
        Args:
            title: 記事タイトル
            content: 記事内容
            config: 投稿設定
            publish_time: 投稿時刻 (HH:MM形式)
        """
        try:
            post_data = {
                'title': title,
                'content': content,
                'config': config
            }
            
            self.scheduled_posts.append(post_data)
            
            # スケジュール登録
            schedule.every().day.at(publish_time).do(
                self._execute_scheduled_post, post_data
            )
            
            logger.info(f"投稿スケジュール登録: {title} at {publish_time}")
            
        except Exception as e:
            logger.error(f"スケジュール登録エラー: {e}")
    
    def _execute_scheduled_post(self, post_data: Dict):
        """スケジュールされた投稿を実行"""
        try:
            result = self.publisher.publish_article(
                post_data['title'],
                post_data['content'],
                post_data['config']
            )
            
            if result.success:
                logger.info(f"スケジュール投稿成功: {post_data['title']}")
            else:
                logger.error(f"スケジュール投稿失敗: {result.message}")
                
        except Exception as e:
            logger.error(f"スケジュール投稿エラー: {e}")
    
    def run_scheduler(self):
        """スケジューラーを実行"""
        logger.info("投稿スケジューラー開始")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1分ごとにチェック

class MultiPlatformPublisher:
    """マルチプラットフォーム投稿クラス"""
    
    def __init__(self):
        """初期化"""
        self.publishers = {}
        self.image_fetcher = None
    
    def add_wordpress_publisher(self, 
                               name: str, 
                               site_url: str, 
                               username: str, 
                               password: str):
        """WordPressサイトを追加"""
        try:
            publisher = WordPressPublisher(site_url, username, password)
            self.publishers[name] = publisher
            logger.info(f"WordPressサイト追加: {name}")
        except Exception as e:
            logger.error(f"WordPressサイト追加エラー: {e}")
    
    def add_image_fetcher(self, unsplash_key: str):
        """Unsplash画像取得機能を追加"""
        self.image_fetcher = UnsplashImageFetcher(unsplash_key)
    
    def publish_to_all(self, 
                      title: str, 
                      content: str, 
                      config: PublishConfig,
                      keyword: str = "") -> List[PublishResult]:
        """
        全プラットフォームに投稿
        
        Args:
            title: 記事タイトル
            content: 記事内容
            config: 投稿設定
            keyword: アイキャッチ画像用キーワード
            
        Returns:
            投稿結果リスト
        """
        results = []
        
        # アイキャッチ画像取得
        featured_media_id = None
        if self.image_fetcher and keyword:
            media_file = self.image_fetcher.fetch_image_for_keyword(keyword)
            if media_file:
                # 最初のサイトにアップロード（簡略化）
                first_publisher = next(iter(self.publishers.values()))
                featured_media_id = first_publisher.upload_media(media_file)
                if featured_media_id:
                    config.featured_media_id = featured_media_id
        
        # 各プラットフォームに投稿
        for name, publisher in self.publishers.items():
            try:
                logger.info(f"{name}への投稿開始")
                result = publisher.publish_article(title, content, config)
                results.append(result)
                
                # API制限対策
                time.sleep(2)
                
            except Exception as e:
                error_result = PublishResult(
                    success=False,
                    post_id=None,
                    post_url=None,
                    message=f"{name}投稿エラー: {e}",
                    published_at=datetime.now().isoformat(),
                    platform=name
                )
                results.append(error_result)
        
        return results
    
    def save_publish_log(self, results: List[PublishResult], filename: str = None):
        """投稿ログを保存"""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output/publish_log_{timestamp}.json"
            
            log_data = {
                'publish_date': datetime.now().isoformat(),
                'results': []
            }
            
            for result in results:
                log_data['results'].append({
                    'success': result.success,
                    'post_id': result.post_id,
                    'post_url': result.post_url,
                    'message': result.message,
                    'published_at': result.published_at,
                    'platform': result.platform
                })
            
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"投稿ログ保存完了: {filename}")
            
        except Exception as e:
            logger.error(f"投稿ログ保存エラー: {e}")

def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        # 設定（実際の使用時は設定ファイルから読み込み）
        wp_config = {
            'site_url': 'https://your-site.com',
            'username': 'your-username',
            'password': 'your-app-password'
        }
        
        # WordPressパブリッシャー初期化
        publisher = WordPressPublisher(
            wp_config['site_url'],
            wp_config['username'], 
            wp_config['password']
        )
        
        # テスト投稿
        test_title = "テスト記事タイトル"
        test_content = """
# テスト記事

これはテスト投稿です。

## 見出し1
内容1

## 見出し2  
内容2

## まとめ
テスト記事の投稿テストでした。
"""
        
        # 投稿設定
        config = PublishConfig(
            status="draft",  # 下書きとして投稿
            excerpt="これはテスト記事の抜粋です。"
        )
        
        # 投稿実行
        result = publisher.publish_article(test_title, test_content, config)
        
        if result.success:
            print(f"投稿成功!")
            print(f"投稿ID: {result.post_id}")
            print(f"投稿URL: {result.post_url}")
        else:
            print(f"投稿失敗: {result.message}")
            
    except Exception as e:
        logger.error(f"メイン実行エラー: {e}")
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()