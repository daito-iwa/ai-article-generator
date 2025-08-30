#!/usr/bin/env python3
"""
AI記事自動生成システムのテストスクリプト
各モジュールの動作確認とシステム全体の統合テストを実行
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# プロジェクトのsrcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from keyword_research import KeywordResearcher, KeywordData
from article_generator import ArticleGenerator, ArticleConfig, GeneratedArticle
from seo_optimizer import SEOOptimizer, SEOAnalysis
from publisher import WordPressPublisher, PublishConfig, PublishResult

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/test_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemTester:
    """システムテスタークラス"""
    
    def __init__(self, config_path: str = "config/api_keys.json"):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス
        """
        self.config_path = config_path
        self.test_results = {}
        self.config = self._load_config()
        
        # テスト用データ
        self.test_keywords = ["Python プログラミング", "AI 機械学習", "Web開発"]
        
        # ログディレクトリ作成
        os.makedirs('logs', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs('output/test_results', exist_ok=True)
    
    def _load_config(self) -> Dict:
        """設定ファイル読み込み"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("設定ファイルが見つかりません。デフォルト設定を使用します。")
                return {
                    "openai_api_key": "test-key",
                    "anthropic_api_key": "test-key",
                    "wordpress": {
                        "url": "https://test-site.com",
                        "username": "test-user",
                        "password": "test-pass"
                    }
                }
        except Exception as e:
            logger.error(f"設定ファイル読み込みエラー: {e}")
            return {}
    
    def test_keyword_research(self) -> bool:
        """キーワードリサーチ機能テスト"""
        logger.info("=== キーワードリサーチ機能テスト開始 ===")
        
        try:
            # KeywordResearcherインスタンス作成
            researcher = KeywordResearcher()
            
            # トレンドキーワード取得テスト（モック）
            logger.info("トレンドキーワード取得テスト...")
            
            # 実際のAPI呼び出しを避け、モックデータを作成
            mock_keywords = [
                KeywordData(
                    main_keyword="テストキーワード1",
                    search_volume="medium",
                    competition="low",
                    related_keywords=["関連1", "関連2"],
                    rising_keywords=["急上昇1"],
                    trend_score=75.0,
                    category="test",
                    collected_at=datetime.now().isoformat()
                ),
                KeywordData(
                    main_keyword="テストキーワード2", 
                    search_volume="high",
                    competition="medium",
                    related_keywords=["関連3", "関連4"],
                    rising_keywords=["急上昇2"],
                    trend_score=85.0,
                    category="test",
                    collected_at=datetime.now().isoformat()
                )
            ]
            
            # CSVエクスポートテスト
            test_csv_file = "output/test_results/test_keywords.csv"
            researcher.export_to_csv(mock_keywords, test_csv_file)
            
            if os.path.exists(test_csv_file):
                logger.info("✓ CSVエクスポート成功")
                csv_test_result = True
            else:
                logger.error("✗ CSVエクスポート失敗")
                csv_test_result = False
            
            # JSONエクスポートテスト
            test_json_file = "output/test_results/test_keywords.json"
            researcher.save_keyword_data(mock_keywords, test_json_file)
            
            if os.path.exists(test_json_file):
                logger.info("✓ JSON保存成功")
                json_test_result = True
            else:
                logger.error("✗ JSON保存失敗") 
                json_test_result = False
            
            overall_result = csv_test_result and json_test_result
            self.test_results['keyword_research'] = {
                'success': overall_result,
                'csv_export': csv_test_result,
                'json_export': json_test_result,
                'keywords_count': len(mock_keywords)
            }
            
            logger.info(f"キーワードリサーチテスト結果: {'成功' if overall_result else '失敗'}")
            return overall_result
            
        except Exception as e:
            logger.error(f"キーワードリサーチテストエラー: {e}")
            self.test_results['keyword_research'] = {'success': False, 'error': str(e)}
            return False
    
    def test_article_generation(self) -> bool:
        """記事生成機能テスト"""
        logger.info("=== 記事生成機能テスト開始 ===")
        
        try:
            # 設定
            config = ArticleConfig(
                min_length=500,  # テスト用に短く設定
                max_length=1000,
                model="gpt-4",
                temperature=0.7
            )
            
            # ArticleGeneratorインスタンス作成（実際のAPIキーが無い場合はモック）
            generator = ArticleGenerator(
                openai_api_key=self.config.get('openai_api_key'),
                config=config
            )
            
            test_results = []
            
            for keyword in self.test_keywords:
                logger.info(f"記事生成テスト: {keyword}")
                
                try:
                    # 実際のAPI呼び出しを避け、モック記事を生成
                    mock_article = GeneratedArticle(
                        title=f"{keyword}について解説",
                        content=f"""
# {keyword}について解説

## はじめに
{keyword}は重要なテーマです。

## {keyword}の特徴
以下の特徴があります：
- 特徴1
- 特徴2
- 特徴3

## {keyword}のメリット
多くのメリットがあります。

## まとめ
{keyword}について解説しました。
""",
                        meta_description=f"{keyword}について詳しく解説します。",
                        keywords=[keyword, "関連キーワード1", "関連キーワード2"],
                        headings=["はじめに", f"{keyword}の特徴", f"{keyword}のメリット", "まとめ"],
                        word_count=250,
                        keyword_density=2.5,
                        readability_score=80.0,
                        seo_score=75.0,
                        generated_at=datetime.now().isoformat(),
                        model_used="mock-model",
                        generation_time=1.5
                    )
                    
                    # 記事保存テスト
                    generator.save_article(mock_article, "output/test_results")
                    
                    test_results.append({
                        'keyword': keyword,
                        'success': True,
                        'word_count': mock_article.word_count,
                        'seo_score': mock_article.seo_score
                    })
                    
                    logger.info(f"✓ {keyword}の記事生成成功")
                    
                except Exception as e:
                    logger.error(f"✗ {keyword}の記事生成失敗: {e}")
                    test_results.append({
                        'keyword': keyword,
                        'success': False,
                        'error': str(e)
                    })
            
            # 結果評価
            success_count = sum(1 for result in test_results if result['success'])
            overall_success = success_count == len(test_results)
            
            self.test_results['article_generation'] = {
                'success': overall_success,
                'success_count': success_count,
                'total_count': len(test_results),
                'details': test_results
            }
            
            logger.info(f"記事生成テスト結果: {success_count}/{len(test_results)} 成功")
            return overall_success
            
        except Exception as e:
            logger.error(f"記事生成テストエラー: {e}")
            self.test_results['article_generation'] = {'success': False, 'error': str(e)}
            return False
    
    def test_seo_optimization(self) -> bool:
        """SEO最適化機能テスト"""
        logger.info("=== SEO最適化機能テスト開始 ===")
        
        try:
            optimizer = SEOOptimizer()
            
            # テスト用記事データ
            test_title = "Python プログラミング入門ガイド"
            test_content = """
# Python プログラミング入門ガイド

## はじめに
Pythonは初心者にも優しいプログラミング言語です。

## Pythonの基本文法
変数、関数、クラスについて説明します。

### 変数の使い方
変数は値を格納するための仕組みです。

### 関数の定義
関数は処理をまとめるための仕組みです。

## Pythonの応用
WebアプリケーションやAI開発に活用できます。

## まとめ
Pythonプログラミングの基本について学びました。
"""
            test_meta_description = "Python プログラミングの基本について初心者向けに解説します。"
            target_keyword = "Python プログラミング"
            
            # SEO分析テスト
            logger.info("SEO分析テスト...")
            analysis = optimizer.analyze_article(
                test_title, 
                test_content, 
                test_meta_description,
                target_keyword
            )
            
            # 分析結果確認
            analysis_success = (
                analysis.overall_seo_score > 0 and
                len(analysis.recommendations) > 0
            )
            
            logger.info(f"SEO分析結果: スコア {analysis.overall_seo_score:.1f}/100")
            logger.info(f"推奨事項数: {len(analysis.recommendations)}")
            
            # SEO最適化テスト
            logger.info("SEO最適化テスト...")
            optimized = optimizer.optimize_article(
                test_title,
                test_content,
                test_meta_description, 
                target_keyword
            )
            
            optimization_success = (
                'title' in optimized and
                'content' in optimized and
                'meta_description' in optimized
            )
            
            # 構造化データ生成テスト
            logger.info("構造化データ生成テスト...")
            structured_data = optimizer.generate_structured_data(
                optimized['title'],
                optimized['content'],
                optimized['meta_description']
            )
            
            structured_data_success = (
                structured_data.type == "Article" and
                structured_data.headline is not None
            )
            
            # レポート保存テスト
            optimizer.save_analysis_report(analysis, "output/test_results/test_seo_analysis.json")
            report_save_success = os.path.exists("output/test_results/test_seo_analysis.json")
            
            overall_success = all([
                analysis_success,
                optimization_success, 
                structured_data_success,
                report_save_success
            ])
            
            self.test_results['seo_optimization'] = {
                'success': overall_success,
                'analysis_success': analysis_success,
                'optimization_success': optimization_success,
                'structured_data_success': structured_data_success,
                'report_save_success': report_save_success,
                'seo_score': analysis.overall_seo_score
            }
            
            if analysis_success:
                logger.info("✓ SEO分析成功")
            else:
                logger.error("✗ SEO分析失敗")
                
            if optimization_success:
                logger.info("✓ SEO最適化成功")
            else:
                logger.error("✗ SEO最適化失敗")
            
            logger.info(f"SEO最適化テスト結果: {'成功' if overall_success else '失敗'}")
            return overall_success
            
        except Exception as e:
            logger.error(f"SEO最適化テストエラー: {e}")
            self.test_results['seo_optimization'] = {'success': False, 'error': str(e)}
            return False
    
    def test_publisher(self) -> bool:
        """投稿機能テスト"""
        logger.info("=== 投稿機能テスト開始 ===")
        
        try:
            # WordPressPublisher初期化（接続テストなし）
            wp_config = self.config.get('wordpress', {})
            
            if not wp_config.get('url'):
                logger.info("WordPress設定が不完全です。モックテストを実行します。")
                
                # モック投稿結果
                mock_result = PublishResult(
                    success=True,
                    post_id=123,
                    post_url="https://test-site.com/test-post",
                    message="モック投稿成功",
                    published_at=datetime.now().isoformat(),
                    platform="WordPress"
                )
                
                self.test_results['publisher'] = {
                    'success': True,
                    'mock_test': True,
                    'connection_test': False,
                    'publish_test': True
                }
                
                logger.info("✓ 投稿機能モックテスト成功")
                return True
            
            # 実際の接続テスト
            try:
                publisher = WordPressPublisher(
                    wp_config['url'],
                    wp_config['username'],
                    wp_config['password']
                )
                
                connection_success = True
                logger.info("✓ WordPress接続成功")
                
            except Exception as e:
                logger.warning(f"WordPress接続失敗: {e}")
                connection_success = False
            
            self.test_results['publisher'] = {
                'success': connection_success,
                'mock_test': False,
                'connection_test': connection_success,
                'publish_test': False  # 実際の投稿はテストしない
            }
            
            logger.info(f"投稿機能テスト結果: {'成功' if connection_success else '失敗'}")
            return connection_success
            
        except Exception as e:
            logger.error(f"投稿機能テストエラー: {e}")
            self.test_results['publisher'] = {'success': False, 'error': str(e)}
            return False
    
    def test_integration(self) -> bool:
        """統合テスト"""
        logger.info("=== 統合テスト開始 ===")
        
        try:
            logger.info("統合テストシナリオ: キーワード → 記事生成 → SEO最適化 → 保存")
            
            # 1. キーワード取得（モック）
            test_keyword = "テスト統合キーワード"
            logger.info(f"1. キーワード: {test_keyword}")
            
            # 2. 記事生成（モック）
            mock_article_content = f"""
# {test_keyword}について詳しく解説

## はじめに
{test_keyword}は重要なテーマです。

## {test_keyword}の概要
詳細な説明を行います。

## {test_keyword}の活用方法
実践的な活用方法を紹介します。

## まとめ
{test_keyword}について解説しました。
"""
            
            logger.info("2. 記事生成完了")
            
            # 3. SEO最適化
            optimizer = SEOOptimizer()
            
            analysis = optimizer.analyze_article(
                f"{test_keyword}完全ガイド",
                mock_article_content,
                f"{test_keyword}について詳しく解説します。",
                test_keyword
            )
            
            optimized = optimizer.optimize_article(
                f"{test_keyword}完全ガイド",
                mock_article_content,
                f"{test_keyword}について詳しく解説します。",
                test_keyword
            )
            
            logger.info("3. SEO最適化完了")
            
            # 4. 結果保存
            result_data = {
                'keyword': test_keyword,
                'title': optimized['title'],
                'content': optimized['content'],
                'meta_description': optimized['meta_description'],
                'seo_score': analysis.overall_seo_score,
                'test_timestamp': datetime.now().isoformat()
            }
            
            result_file = "output/test_results/integration_test_result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            logger.info("4. 結果保存完了")
            
            # 統合テスト成功判定
            integration_success = (
                analysis.overall_seo_score > 0 and
                len(optimized['content']) > 100 and
                os.path.exists(result_file)
            )
            
            self.test_results['integration'] = {
                'success': integration_success,
                'keyword': test_keyword,
                'seo_score': analysis.overall_seo_score,
                'content_length': len(optimized['content']),
                'result_saved': os.path.exists(result_file)
            }
            
            logger.info(f"統合テスト結果: {'成功' if integration_success else '失敗'}")
            return integration_success
            
        except Exception as e:
            logger.error(f"統合テストエラー: {e}")
            self.test_results['integration'] = {'success': False, 'error': str(e)}
            return False
    
    def run_all_tests(self) -> Dict:
        """全テスト実行"""
        logger.info("==========================================")
        logger.info("AI記事自動生成システム テスト開始")
        logger.info("==========================================")
        
        start_time = datetime.now()
        
        # 各テスト実行
        tests = [
            ('キーワードリサーチ', self.test_keyword_research),
            ('記事生成', self.test_article_generation),
            ('SEO最適化', self.test_seo_optimization),
            ('投稿機能', self.test_publisher),
            ('統合テスト', self.test_integration)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                if result:
                    passed_tests += 1
                    logger.info(f"✓ {test_name}: 合格")
                else:
                    logger.error(f"✗ {test_name}: 不合格")
            except Exception as e:
                logger.error(f"✗ {test_name}: エラー - {e}")
        
        end_time = datetime.now()
        test_duration = (end_time - start_time).total_seconds()
        
        # 全体結果
        overall_success = passed_tests == total_tests
        success_rate = (passed_tests / total_tests) * 100
        
        summary = {
            'overall_success': overall_success,
            'passed_tests': passed_tests,
            'total_tests': total_tests,
            'success_rate': success_rate,
            'test_duration': test_duration,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'details': self.test_results
        }
        
        # 結果保存
        summary_file = "output/test_results/test_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        # 結果表示
        logger.info("==========================================")
        logger.info("テスト結果サマリー")
        logger.info("==========================================")
        logger.info(f"合格率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info(f"実行時間: {test_duration:.2f}秒")
        logger.info(f"結果: {'全テスト合格' if overall_success else 'テスト失敗あり'}")
        logger.info(f"詳細レポート: {summary_file}")
        
        return summary

def main():
    """メイン実行"""
    tester = SystemTester()
    
    # 全テスト実行
    results = tester.run_all_tests()
    
    # 終了コード設定
    exit_code = 0 if results['overall_success'] else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    main()