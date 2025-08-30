#!/usr/bin/env python3
"""
AI記事自動生成システム - メインエントリーポイント
コマンドライン引数に基づいて各機能を実行する
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from keyword_research import KeywordResearcher
from article_generator import ArticleGenerator, ArticleConfig
from seo_optimizer import SEOOptimizer
from publisher import WordPressPublisher, PublishConfig, MultiPlatformPublisher

# ログ設定
def setup_logging(log_level: str = "INFO"):
    """ログ設定"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log'),
            logging.StreamHandler()
        ]
    )

logger = logging.getLogger(__name__)

class AIArticleSystem:
    """AI記事自動生成システムメインクラス"""
    
    def __init__(self, config_path: str = "config/api_keys.json"):
        """初期化"""
        self.config = self._load_config(config_path)
        self.keyword_researcher = KeywordResearcher()
        
        # ArticleGenerator初期化
        self.article_generator = ArticleGenerator(
            openai_api_key=self.config.get('openai_api_key'),
            anthropic_api_key=self.config.get('anthropic_api_key')
        )
        
        self.seo_optimizer = SEOOptimizer()
        
        # WordPress Publisher（設定がある場合）
        self.publisher = None
        wp_config = self.config.get('wordpress', {})
        if all(key in wp_config for key in ['url', 'username', 'password']):
            try:
                self.publisher = WordPressPublisher(
                    wp_config['url'],
                    wp_config['username'],
                    wp_config['password']
                )
            except Exception as e:
                logger.warning(f"WordPress接続失敗: {e}")
    
    def _load_config(self, config_path: str) -> Dict:
        """設定ファイル読み込み"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def research_keywords(self, limit: int = 10, category: str = None) -> List:
        """キーワードリサーチを実行"""
        logger.info("キーワードリサーチ開始")
        
        keywords = self.keyword_researcher.get_trending_keywords(
            category=category, 
            limit=limit
        )
        
        if not keywords:
            logger.warning("キーワードが取得できませんでした")
            return []
        
        # 結果保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = f"output/keywords_{timestamp}.csv"
        json_file = f"output/keywords_{timestamp}.json"
        
        self.keyword_researcher.export_to_csv(keywords, csv_file)
        self.keyword_researcher.save_keyword_data(keywords, json_file)
        
        logger.info(f"{len(keywords)}個のキーワードを取得し、{csv_file}, {json_file}に保存しました")
        
        # 上位キーワード表示
        for i, keyword_data in enumerate(keywords[:5], 1):
            print(f"{i}. {keyword_data.main_keyword} (トレンドスコア: {keyword_data.trend_score:.1f})")
        
        return keywords
    
    def generate_article(self, keyword: str, length: int = 1500) -> Optional:
        """記事生成を実行"""
        logger.info(f"記事生成開始: {keyword}")
        
        # 記事生成設定
        config = ArticleConfig(
            min_length=length,
            max_length=length + 500,
            model="gpt-4",
            temperature=0.7
        )
        
        # 記事生成
        article = self.article_generator.generate_article(keyword)
        
        if not article:
            logger.error("記事生成に失敗しました")
            return None
        
        # SEO最適化
        logger.info("SEO最適化実行")
        analysis = self.seo_optimizer.analyze_article(
            article.title,
            article.content,
            article.meta_description,
            keyword
        )
        
        optimized = self.seo_optimizer.optimize_article(
            article.title,
            article.content,
            article.meta_description,
            keyword
        )
        
        # 最適化結果を記事に反映
        article.title = optimized['title']
        article.content = optimized['content'] 
        article.meta_description = optimized['meta_description']
        article.seo_score = analysis.overall_seo_score
        
        # 記事保存
        self.article_generator.save_article(article)
        
        logger.info(f"記事生成完了 - SEOスコア: {article.seo_score:.1f}/100")
        
        # 結果表示
        print(f"\\nタイトル: {article.title}")
        print(f"文字数: {article.word_count}")
        print(f"キーワード密度: {article.keyword_density:.2f}%")
        print(f"SEOスコア: {article.seo_score:.1f}/100")
        
        return article
    
    def publish_article(self, keyword: str, status: str = "draft") -> bool:
        """記事生成 + 投稿を実行"""
        if not self.publisher:
            logger.error("WordPress設定が不完全です")
            return False
        
        logger.info(f"記事生成・投稿開始: {keyword}")
        
        # 記事生成
        article = self.generate_article(keyword)
        if not article:
            return False
        
        # 投稿設定
        config = PublishConfig(
            status=status,
            excerpt=article.meta_description
        )
        
        # WordPress投稿
        result = self.publisher.publish_article(
            article.title,
            article.content,
            config
        )
        
        if result.success:
            logger.info(f"投稿成功: {result.post_url}")
            print(f"投稿成功: {result.post_url}")
            return True
        else:
            logger.error(f"投稿失敗: {result.message}")
            print(f"投稿失敗: {result.message}")
            return False
    
    def batch_generate(self, keywords: List[str], status: str = "draft") -> None:
        """複数記事の一括生成・投稿"""
        logger.info(f"{len(keywords)}記事の一括処理開始")
        
        results = []
        
        for i, keyword in enumerate(keywords, 1):
            print(f"\\n[{i}/{len(keywords)}] 処理中: {keyword}")
            
            try:
                if self.publisher:
                    success = self.publish_article(keyword, status)
                else:
                    article = self.generate_article(keyword)
                    success = article is not None
                
                results.append({
                    'keyword': keyword,
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                })
                
                # API制限対策
                import time
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"処理エラー {keyword}: {e}")
                results.append({
                    'keyword': keyword,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # 結果サマリー
        success_count = sum(1 for r in results if r['success'])
        print(f"\\n一括処理完了: {success_count}/{len(keywords)} 成功")
        
        # ログ保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"output/batch_results_{timestamp}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"一括処理ログ保存: {log_file}")
    
    def analyze_seo(self, title: str, content_file: str, keyword: str) -> None:
        """SEO分析のみ実行"""
        try:
            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"ファイル読み込みエラー: {e}")
            return
        
        logger.info(f"SEO分析開始: {keyword}")
        
        analysis = self.seo_optimizer.analyze_article(
            title, content, "", keyword
        )
        
        # 結果表示
        print(f"\\n=== SEO分析結果 ===")
        print(f"総合スコア: {analysis.overall_seo_score:.1f}/100")
        print(f"タイトルスコア: {analysis.title_score:.1f}/100")
        print(f"見出し構造スコア: {analysis.heading_structure_score:.1f}/100")
        print(f"キーワード密度スコア: {analysis.keyword_density_score:.1f}/100")
        print(f"読みやすさスコア: {analysis.readability_score:.1f}/100")
        
        print("\\n=== 推奨事項 ===")
        for rec in analysis.recommendations[:5]:
            print(f"- {rec}")
        
        print("\\n=== 警告 ===")
        for warn in analysis.warnings[:5]:
            print(f"- {warn}")
        
        # レポート保存
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"output/seo_analysis_{timestamp}.json"
        self.seo_optimizer.save_analysis_report(analysis, report_file)
        
        print(f"\\n詳細レポート: {report_file}")

def main():
    """メイン実行"""
    parser = argparse.ArgumentParser(description='AI記事自動生成システム')
    subparsers = parser.add_subparsers(dest='command', help='実行コマンド')
    
    # キーワードリサーチコマンド
    research_parser = subparsers.add_parser('research', help='キーワードリサーチ実行')
    research_parser.add_argument('--limit', type=int, default=10, help='取得キーワード数')
    research_parser.add_argument('--category', type=str, help='カテゴリ指定')
    
    # 記事生成コマンド
    generate_parser = subparsers.add_parser('generate', help='記事生成実行')
    generate_parser.add_argument('keyword', type=str, help='ターゲットキーワード')
    generate_parser.add_argument('--length', type=int, default=1500, help='記事の長さ')
    
    # 投稿コマンド  
    publish_parser = subparsers.add_parser('publish', help='記事生成・投稿実行')
    publish_parser.add_argument('keyword', type=str, help='ターゲットキーワード')
    publish_parser.add_argument('--status', default='draft', choices=['draft', 'publish'], help='投稿ステータス')
    
    # 一括処理コマンド
    batch_parser = subparsers.add_parser('batch', help='一括記事生成')
    batch_parser.add_argument('keywords', nargs='+', help='キーワードリスト')
    batch_parser.add_argument('--status', default='draft', choices=['draft', 'publish'], help='投稿ステータス')
    
    # SEO分析コマンド
    seo_parser = subparsers.add_parser('analyze', help='SEO分析実行')
    seo_parser.add_argument('title', type=str, help='記事タイトル')
    seo_parser.add_argument('content_file', type=str, help='コンテンツファイルパス')
    seo_parser.add_argument('keyword', type=str, help='ターゲットキーワード')
    
    # テストコマンド
    test_parser = subparsers.add_parser('test', help='システムテスト実行')
    
    # 共通オプション
    parser.add_argument('--config', default='config/api_keys.json', help='設定ファイルパス')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help='ログレベル')
    
    args = parser.parse_args()
    
    # ログ設定
    setup_logging(args.log_level)
    
    # 出力ディレクトリ作成
    os.makedirs('output', exist_ok=True)
    
    # システム初期化
    system = AIArticleSystem(args.config)
    
    try:
        if args.command == 'research':
            system.research_keywords(args.limit, args.category)
        
        elif args.command == 'generate':
            system.generate_article(args.keyword, args.length)
        
        elif args.command == 'publish':
            system.publish_article(args.keyword, args.status)
        
        elif args.command == 'batch':
            system.batch_generate(args.keywords, args.status)
        
        elif args.command == 'analyze':
            system.analyze_seo(args.title, args.content_file, args.keyword)
        
        elif args.command == 'test':
            from test_system import SystemTester
            tester = SystemTester(args.config)
            results = tester.run_all_tests()
            sys.exit(0 if results['overall_success'] else 1)
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        logger.info("処理が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"実行エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()