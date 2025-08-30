#!/usr/bin/env python3
"""
自動記事生成スクリプト
指定されたキーワードリストから自動で記事を生成
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime
import logging

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from article_generator import ArticleGenerator, ArticleConfig
from keyword_research import KeywordResearcher
from seo_optimizer import SEOOptimizer

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoArticleGenerator:
    """自動記事生成クラス"""
    
    def __init__(self, config_path: str = "config/api_keys.json"):
        """初期化"""
        self.config = self._load_config(config_path)
        
        # 各コンポーネント初期化
        self.article_generator = ArticleGenerator(
            openai_api_key=self.config.get('openai_api_key'),
            anthropic_api_key=self.config.get('anthropic_api_key')
        )
        
        self.keyword_researcher = KeywordResearcher()
        self.seo_optimizer = SEOOptimizer()
        
        # 出力ディレクトリ作成
        os.makedirs('output/auto_generated', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """設定ファイル読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def generate_from_keywords_file(self, keywords_file: str, 
                                  delay: int = 30,
                                  include_affiliate: bool = True) -> list:
        """
        キーワードファイルから記事を自動生成
        
        Args:
            keywords_file: キーワードファイルパス（1行1キーワード）
            delay: 記事生成間隔（秒）
            include_affiliate: アフィリエイトリンクを含めるか
            
        Returns:
            生成された記事リスト
        """
        try:
            # キーワード読み込み
            with open(keywords_file, 'r', encoding='utf-8') as f:
                keywords = [line.strip() for line in f if line.strip()]
            
            logger.info(f"{len(keywords)}個のキーワードを読み込みました")
            
            generated_articles = []
            
            for i, keyword in enumerate(keywords, 1):
                logger.info(f"[{i}/{len(keywords)}] '{keyword}' の記事を生成中...")
                
                try:
                    # 記事生成
                    article = self._generate_single_article(
                        keyword, 
                        include_affiliate=include_affiliate
                    )
                    
                    if article:
                        generated_articles.append({
                            'keyword': keyword,
                            'title': article.title,
                            'file_path': self._save_article(article, keyword),
                            'word_count': article.word_count,
                            'seo_score': article.seo_score
                        })
                        logger.info(f"✅ 記事生成成功: {article.title}")
                    else:
                        logger.error(f"❌ 記事生成失敗: {keyword}")
                    
                    # API制限回避のための待機
                    if i < len(keywords):
                        logger.info(f"次の記事生成まで{delay}秒待機...")
                        time.sleep(delay)
                        
                except Exception as e:
                    logger.error(f"記事生成エラー ({keyword}): {e}")
                    continue
            
            # 結果サマリー保存
            self._save_summary(generated_articles)
            
            return generated_articles
            
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {e}")
            return []
    
    def generate_trending_articles(self, count: int = 5, 
                                 category: str = None,
                                 delay: int = 30) -> list:
        """
        トレンドキーワードから記事を自動生成
        
        Args:
            count: 生成する記事数
            category: カテゴリ指定
            delay: 記事生成間隔（秒）
            
        Returns:
            生成された記事リスト
        """
        logger.info("トレンドキーワードを取得中...")
        
        # トレンドキーワード取得
        trending_keywords = self.keyword_researcher.get_trending_keywords(
            limit=count,
            category=category
        )
        
        if not trending_keywords:
            logger.error("トレンドキーワードが取得できませんでした")
            return []
        
        # キーワードリスト作成
        keywords = [kw.main_keyword for kw in trending_keywords[:count]]
        
        # 一時ファイルに保存
        temp_file = 'temp_trending_keywords.txt'
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(keywords))
        
        # 記事生成
        result = self.generate_from_keywords_file(temp_file, delay=delay)
        
        # 一時ファイル削除
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return result
    
    def _generate_single_article(self, keyword: str, 
                               include_affiliate: bool = True) -> object:
        """単一記事生成"""
        try:
            # 記事設定
            config = ArticleConfig(
                min_length=1500,
                max_length=2000,
                temperature=0.7,
                model="gpt-4",
                include_faq=True
            )
            
            self.article_generator.config = config
            
            # 記事生成
            article = self.article_generator.generate_article(keyword)
            
            if article and include_affiliate:
                # アフィリエイトリンク追加
                article.content = self._add_affiliate_links(
                    article.content, 
                    keyword
                )
            
            return article
            
        except Exception as e:
            logger.error(f"記事生成エラー: {e}")
            return None
    
    def _add_affiliate_links(self, content: str, keyword: str) -> str:
        """アフィリエイトリンクを追加"""
        # シンプルなアフィリエイトセクション
        affiliate_section = """

## おすすめのツール・サービス

### 1. エックスサーバー
国内シェアNo.1の高速レンタルサーバー。WordPressの動作も快適です。
[→ エックスサーバーの詳細はこちら](https://px.a8.net/svt/ejp?a8mat=XXX)

### 2. ConoHa WING
表示速度国内No.1のレンタルサーバー。初心者にも使いやすい管理画面が特徴です。
[→ ConoHa WINGの詳細はこちら](https://px.a8.net/svt/ejp?a8mat=YYY)

"""
        
        # まとめの前に挿入
        if "## まとめ" in content:
            content = content.replace("## まとめ", affiliate_section + "## まとめ")
        else:
            content += affiliate_section
        
        return content
    
    def _save_article(self, article: object, keyword: str) -> str:
        """記事を保存"""
        try:
            # ファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_keyword = keyword.replace(' ', '_').replace('/', '_')[:30]
            filename = f"output/auto_generated/{timestamp}_{safe_keyword}.md"
            
            # マークダウン形式で保存
            content = f"""# {article.title}

{article.content}

---
**メタ情報**
- 生成日時: {article.generated_at}
- 文字数: {article.word_count}
- SEOスコア: {article.seo_score:.1f}
- キーワード: {', '.join(article.keywords)}
"""
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # JSON形式でも保存
            json_filename = filename.replace('.md', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'title': article.title,
                    'content': article.content,
                    'meta_description': article.meta_description,
                    'keywords': article.keywords,
                    'word_count': article.word_count,
                    'seo_score': article.seo_score,
                    'generated_at': article.generated_at
                }, f, ensure_ascii=False, indent=2)
            
            return filename
            
        except Exception as e:
            logger.error(f"記事保存エラー: {e}")
            return ""
    
    def _save_summary(self, articles: list):
        """生成結果のサマリーを保存"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = f"logs/generation_summary_{timestamp}.json"
            
            summary = {
                'generated_at': datetime.now().isoformat(),
                'total_articles': len(articles),
                'success_count': len([a for a in articles if a.get('file_path')]),
                'average_word_count': sum(a.get('word_count', 0) for a in articles) / len(articles) if articles else 0,
                'average_seo_score': sum(a.get('seo_score', 0) for a in articles) / len(articles) if articles else 0,
                'articles': articles
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"サマリー保存完了: {summary_file}")
            
            # コンソールにも表示
            print("\n=== 生成結果サマリー ===")
            print(f"総記事数: {summary['total_articles']}")
            print(f"成功: {summary['success_count']}")
            print(f"平均文字数: {summary['average_word_count']:.0f}")
            print(f"平均SEOスコア: {summary['average_seo_score']:.1f}")
            
        except Exception as e:
            logger.error(f"サマリー保存エラー: {e}")

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='自動記事生成ツール')
    
    parser.add_argument(
        '--mode', 
        choices=['file', 'trending'], 
        default='trending',
        help='生成モード: file=キーワードファイルから, trending=トレンドから'
    )
    
    parser.add_argument(
        '--keywords-file',
        help='キーワードファイルパス（fileモード時）'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=5,
        help='生成する記事数（trendingモード時）'
    )
    
    parser.add_argument(
        '--category',
        help='カテゴリ指定（trendingモード時）'
    )
    
    parser.add_argument(
        '--delay',
        type=int,
        default=30,
        help='記事生成間隔（秒）'
    )
    
    parser.add_argument(
        '--no-affiliate',
        action='store_true',
        help='アフィリエイトリンクを含めない'
    )
    
    args = parser.parse_args()
    
    # 生成器初期化
    generator = AutoArticleGenerator()
    
    if args.mode == 'file':
        if not args.keywords_file:
            print("エラー: --keywords-file を指定してください")
            return
        
        generator.generate_from_keywords_file(
            args.keywords_file,
            delay=args.delay,
            include_affiliate=not args.no_affiliate
        )
    
    else:  # trending mode
        generator.generate_trending_articles(
            count=args.count,
            category=args.category,
            delay=args.delay
        )

if __name__ == "__main__":
    main()