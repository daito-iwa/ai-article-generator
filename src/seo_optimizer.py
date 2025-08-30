#!/usr/bin/env python3
"""
SEO最適化モジュール
記事のSEO要素を分析・最適化し、検索エンジンでのランキング向上を支援する
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

logger = logging.getLogger(__name__)

@dataclass
class SEOAnalysis:
    """SEO分析結果"""
    title_score: float
    meta_description_score: float
    heading_structure_score: float
    keyword_density_score: float
    readability_score: float
    internal_links_score: float
    image_optimization_score: float
    overall_seo_score: float
    recommendations: List[str]
    warnings: List[str]

@dataclass
class CompetitorAnalysis:
    """競合分析結果"""
    competitor_url: str
    title_length: int
    meta_description_length: int
    heading_count: int
    word_count: int
    keyword_density: float
    backlink_count: int
    domain_authority: float

@dataclass  
class StructuredData:
    """構造化データ"""
    type: str  # Article, BlogPosting, etc.
    headline: str
    description: str
    author: str
    date_published: str
    date_modified: str
    keywords: List[str]
    image_url: str

class SEOOptimizer:
    """SEO最適化クラス"""
    
    def __init__(self):
        """初期化"""
        self.target_title_length = 60
        self.target_meta_description_length = 160
        self.optimal_keyword_density_range = (1.0, 3.0)  # パーセント
        self.min_word_count = 300
        self.recommended_word_count = 1500
        
        # NLTK データのダウンロード（初回のみ）
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
    
    def analyze_article(self, 
                       title: str, 
                       content: str, 
                       meta_description: str = "",
                       target_keyword: str = "",
                       target_keywords: List[str] = []) -> SEOAnalysis:
        """
        記事のSEO分析を実行
        
        Args:
            title: 記事タイトル
            content: 記事本文
            meta_description: メタディスクリプション
            target_keyword: メインキーワード
            target_keywords: ターゲットキーワードリスト
            
        Returns:
            SEOAnalysis結果
        """
        try:
            logger.info("SEO分析開始")
            
            recommendations = []
            warnings = []
            
            # タイトル分析
            title_score = self._analyze_title(title, target_keyword, recommendations, warnings)
            
            # メタディスクリプション分析
            meta_score = self._analyze_meta_description(meta_description, target_keyword, recommendations, warnings)
            
            # 見出し構造分析
            heading_score = self._analyze_heading_structure(content, target_keyword, recommendations, warnings)
            
            # キーワード密度分析
            keyword_score = self._analyze_keyword_density(content, target_keyword, target_keywords, recommendations, warnings)
            
            # 読みやすさ分析
            readability_score = self._analyze_readability(content, recommendations, warnings)
            
            # 内部リンク分析
            internal_links_score = self._analyze_internal_links(content, recommendations, warnings)
            
            # 画像最適化分析
            image_score = self._analyze_image_optimization(content, recommendations, warnings)
            
            # 総合SEOスコア計算
            overall_score = self._calculate_overall_score(
                title_score, meta_score, heading_score, keyword_score,
                readability_score, internal_links_score, image_score
            )
            
            logger.info(f"SEO分析完了 - 総合スコア: {overall_score:.1f}/100")
            
            return SEOAnalysis(
                title_score=title_score,
                meta_description_score=meta_score,
                heading_structure_score=heading_score,
                keyword_density_score=keyword_score,
                readability_score=readability_score,
                internal_links_score=internal_links_score,
                image_optimization_score=image_score,
                overall_seo_score=overall_score,
                recommendations=recommendations,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"SEO分析エラー: {e}")
            return SEOAnalysis(0, 0, 0, 0, 0, 0, 0, 0, [], [f"分析エラー: {e}"])
    
    def _analyze_title(self, title: str, target_keyword: str, recommendations: List[str], warnings: List[str]) -> float:
        """タイトル分析"""
        score = 0.0
        
        # 文字数チェック
        title_length = len(title)
        if 30 <= title_length <= 60:
            score += 40
        elif title_length < 30:
            recommendations.append("タイトルが短すぎます。30文字以上にすることを推奨します。")
            score += 20
        else:
            warnings.append(f"タイトルが長すぎます（{title_length}文字）。60文字以内に収めることを推奨します。")
            score += 10
        
        # キーワード含有チェック
        if target_keyword and target_keyword.lower() in title.lower():
            score += 30
            # キーワードの位置をチェック
            keyword_position = title.lower().find(target_keyword.lower())
            if keyword_position <= len(title) * 0.5:  # 前半にある場合
                score += 20
                recommendations.append("キーワードがタイトルの前半に配置されており、良好です。")
            else:
                score += 10
                recommendations.append("キーワードをタイトルの前半に配置することを推奨します。")
        else:
            warnings.append("ターゲットキーワードがタイトルに含まれていません。")
        
        # 魅力的な要素のチェック
        attractive_words = ["方法", "完全ガイド", "徹底解説", "最新", "おすすめ", "比較", "ランキング"]
        if any(word in title for word in attractive_words):
            score += 10
            recommendations.append("魅力的な要素がタイトルに含まれており、クリック率向上が期待できます。")
        
        return min(100.0, score)
    
    def _analyze_meta_description(self, meta_description: str, target_keyword: str, recommendations: List[str], warnings: List[str]) -> float:
        """メタディスクリプション分析"""
        score = 0.0
        
        if not meta_description:
            warnings.append("メタディスクリプションが設定されていません。")
            return 0.0
        
        # 文字数チェック
        desc_length = len(meta_description)
        if 120 <= desc_length <= 160:
            score += 50
            recommendations.append("メタディスクリプションの文字数が適切です。")
        elif desc_length < 120:
            recommendations.append(f"メタディスクリプションが短すぎます（{desc_length}文字）。120文字以上にすることを推奨します。")
            score += 25
        else:
            warnings.append(f"メタディスクリプションが長すぎます（{desc_length}文字）。160文字以内に収めることを推奨します。")
            score += 25
        
        # キーワード含有チェック
        if target_keyword and target_keyword.lower() in meta_description.lower():
            score += 30
            recommendations.append("メタディスクリプションにターゲットキーワードが含まれています。")
        else:
            warnings.append("メタディスクリプションにターゲットキーワードが含まれていません。")
        
        # 行動を促す要素のチェック
        cta_words = ["詳しく", "確認", "チェック", "ご覧", "読む", "学ぶ"]
        if any(word in meta_description for word in cta_words):
            score += 20
            recommendations.append("行動を促す要素が含まれており、クリック率向上が期待できます。")
        
        return min(100.0, score)
    
    def _analyze_heading_structure(self, content: str, target_keyword: str, recommendations: List[str], warnings: List[str]) -> float:
        """見出し構造分析"""
        score = 0.0
        
        # 見出し抽出
        h1_headings = re.findall(r'^# (.+)', content, re.MULTILINE)
        h2_headings = re.findall(r'^## (.+)', content, re.MULTILINE)  
        h3_headings = re.findall(r'^### (.+)', content, re.MULTILINE)
        
        total_headings = len(h1_headings) + len(h2_headings) + len(h3_headings)
        
        # H1チェック
        if len(h1_headings) == 1:
            score += 20
            recommendations.append("H1タグが適切に1つ設定されています。")
        elif len(h1_headings) == 0:
            warnings.append("H1タグが設定されていません。")
        else:
            warnings.append(f"H1タグが複数設定されています（{len(h1_headings)}個）。1つに統一することを推奨します。")
        
        # H2見出し数チェック
        if 3 <= len(h2_headings) <= 6:
            score += 30
            recommendations.append("H2見出し数が適切です。")
        elif len(h2_headings) < 3:
            recommendations.append("H2見出しが少なすぎます。3個以上設定することを推奨します。")
            score += 15
        else:
            recommendations.append("H2見出しが多すぎる可能性があります。読みやすさを重視して調整を検討してください。")
            score += 20
        
        # キーワード含有率チェック
        all_headings = h1_headings + h2_headings + h3_headings
        keyword_in_headings = sum(1 for heading in all_headings if target_keyword.lower() in heading.lower())
        
        if all_headings:
            keyword_ratio = keyword_in_headings / len(all_headings)
            if 0.3 <= keyword_ratio <= 0.6:
                score += 30
                recommendations.append("見出しでのキーワード使用率が適切です。")
            elif keyword_ratio < 0.3:
                recommendations.append("見出しにもっとキーワードを含めることを検討してください。")
                score += 15
            else:
                warnings.append("見出しでのキーワード使用が過度になっています。自然な表現を心がけてください。")
                score += 10
        
        # 階層構造チェック
        if h2_headings and not h3_headings:
            score += 20
        elif h2_headings and h3_headings:
            score += 15
        else:
            recommendations.append("見出し階層をより明確にすることを推奨します。")
            score += 10
        
        return min(100.0, score)
    
    def _analyze_keyword_density(self, content: str, target_keyword: str, target_keywords: List[str], recommendations: List[str], warnings: List[str]) -> float:
        """キーワード密度分析"""
        score = 0.0
        
        if not target_keyword:
            warnings.append("ターゲットキーワードが指定されていません。")
            return 0.0
        
        # 文字数と単語数を計算
        word_count = len(content.replace(' ', ''))
        
        if word_count == 0:
            warnings.append("コンテンツが空です。")
            return 0.0
        
        # メインキーワード密度
        keyword_count = content.lower().count(target_keyword.lower())
        keyword_density = (keyword_count / word_count) * 100
        
        min_density, max_density = self.optimal_keyword_density_range
        
        if min_density <= keyword_density <= max_density:
            score += 60
            recommendations.append(f"メインキーワードの密度が適切です（{keyword_density:.2f}%）。")
        elif keyword_density < min_density:
            recommendations.append(f"キーワード密度が低すぎます（{keyword_density:.2f}%）。{min_density}%以上にすることを推奨します。")
            score += 30
        else:
            warnings.append(f"キーワード密度が高すぎます（{keyword_density:.2f}%）。{max_density}%以下にすることを推奨します。")
            score += 20
        
        # 関連キーワード分析
        if target_keywords:
            related_keyword_score = 0
            for keyword in target_keywords[:5]:  # 上位5つのみ
                related_count = content.lower().count(keyword.lower())
                if related_count > 0:
                    related_keyword_score += 1
            
            related_ratio = related_keyword_score / min(5, len(target_keywords))
            score += related_ratio * 40
            
            recommendations.append(f"関連キーワード使用率: {related_ratio*100:.0f}%")
        
        return min(100.0, score)
    
    def _analyze_readability(self, content: str, recommendations: List[str], warnings: List[str]) -> float:
        """読みやすさ分析"""
        score = 0.0
        
        try:
            # 文と文字数の計算
            sentences = sent_tokenize(content)
            sentence_count = len(sentences)
            word_count = len(content.replace(' ', ''))
            
            if sentence_count == 0:
                warnings.append("文が検出されませんでした。")
                return 0.0
            
            # 平均文字数
            avg_sentence_length = word_count / sentence_count
            
            # 文の長さ評価
            if avg_sentence_length <= 25:
                score += 30
                recommendations.append("文の長さが適切で読みやすいです。")
            elif avg_sentence_length <= 40:
                score += 20
                recommendations.append("文の長さは許容範囲内ですが、もう少し短くすると読みやすくなります。")
            else:
                warnings.append("文が長すぎます。短い文に分割することを推奨します。")
                score += 10
            
            # 段落数評価
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            paragraph_count = len(paragraphs)
            
            if paragraph_count >= 3:
                score += 20
                recommendations.append("適切な段落分けがされています。")
            else:
                recommendations.append("段落をもっと細かく分けることで読みやすさが向上します。")
                score += 10
            
            # リスト構造の有無
            if '・' in content or '1.' in content or '2.' in content:
                score += 20
                recommendations.append("リスト構造が使用されており、読みやすいです。")
            else:
                recommendations.append("箇条書きやリスト構造を使用すると読みやすくなります。")
                score += 10
            
            # 文字数評価
            if word_count >= self.recommended_word_count:
                score += 30
                recommendations.append("十分な文字数があり、詳細な情報提供ができています。")
            elif word_count >= self.min_word_count:
                score += 20
                recommendations.append("文字数は最低基準を満たしていますが、もう少し詳しい情報があると良いでしょう。")
            else:
                warnings.append(f"文字数が不足しています（{word_count}文字）。{self.min_word_count}文字以上を推奨します。")
                score += 5
            
        except Exception as e:
            warnings.append(f"読みやすさ分析でエラーが発生しました: {e}")
            score = 50.0  # デフォルトスコア
        
        return min(100.0, score)
    
    def _analyze_internal_links(self, content: str, recommendations: List[str], warnings: List[str]) -> float:
        """内部リンク分析"""
        score = 0.0
        
        # 内部リンクを検出（簡易的な実装）
        internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        internal_link_count = len(internal_links)
        
        # 適切な内部リンク数（1000文字につき1-2個が目安）
        word_count = len(content.replace(' ', ''))
        recommended_links = max(1, word_count // 1000)
        
        if internal_link_count == 0:
            recommendations.append("内部リンクを追加することで、サイト内回遊率とSEOが向上します。")
            score += 20
        elif internal_link_count <= recommended_links * 2:
            score += 80
            recommendations.append(f"内部リンク数が適切です（{internal_link_count}個）。")
        else:
            warnings.append("内部リンクが多すぎる可能性があります。ユーザー体験を重視してください。")
            score += 40
        
        # 外部リンクの分析
        # 実際の実装では、URLの分析により内部・外部を判定
        external_links = [link for _, link in internal_links if 'http' in link]
        if external_links:
            score += 20
            recommendations.append("外部リンクが適切に設定されています。")
        
        return min(100.0, score)
    
    def _analyze_image_optimization(self, content: str, recommendations: List[str], warnings: List[str]) -> float:
        """画像最適化分析"""
        score = 0.0
        
        # 画像の検出
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        image_count = len(images)
        
        if image_count == 0:
            recommendations.append("画像を追加することで、ユーザーエンゲージメントとSEOが向上します。")
            score += 30
        else:
            score += 40
            recommendations.append(f"{image_count}個の画像が設定されています。")
            
            # alt属性の確認
            images_with_alt = [img for alt_text, _ in images if alt_text.strip()]
            if len(images_with_alt) == image_count:
                score += 60
                recommendations.append("すべての画像にalt属性が設定されています。")
            else:
                missing_alt = image_count - len(images_with_alt)
                warnings.append(f"{missing_alt}個の画像にalt属性がありません。SEO向上のために設定することを推奨します。")
                score += 30
        
        return min(100.0, score)
    
    def _calculate_overall_score(self, *scores: float) -> float:
        """総合SEOスコア計算"""
        # 重み付き平均
        weights = [0.2, 0.15, 0.15, 0.2, 0.15, 0.08, 0.07]  # 各要素の重み
        weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
        return min(100.0, weighted_sum)
    
    def optimize_article(self, 
                        title: str, 
                        content: str, 
                        meta_description: str,
                        target_keyword: str,
                        target_keywords: List[str] = []) -> Dict[str, str]:
        """
        記事のSEO最適化を実行
        
        Args:
            title: 元のタイトル
            content: 元のコンテンツ
            meta_description: 元のメタディスクリプション
            target_keyword: メインキーワード
            target_keywords: 関連キーワード
            
        Returns:
            最適化された記事要素
        """
        try:
            logger.info("記事最適化開始")
            
            # 現在の分析
            analysis = self.analyze_article(title, content, meta_description, target_keyword, target_keywords)
            
            optimized = {
                'title': self._optimize_title(title, target_keyword, analysis),
                'content': self._optimize_content(content, target_keyword, target_keywords, analysis),
                'meta_description': self._optimize_meta_description(meta_description, target_keyword, content)
            }
            
            logger.info("記事最適化完了")
            return optimized
            
        except Exception as e:
            logger.error(f"記事最適化エラー: {e}")
            return {'title': title, 'content': content, 'meta_description': meta_description}
    
    def _optimize_title(self, title: str, target_keyword: str, analysis: SEOAnalysis) -> str:
        """タイトル最適化"""
        optimized_title = title
        
        # キーワードが含まれていない場合は追加
        if target_keyword and target_keyword.lower() not in title.lower():
            if len(title) + len(target_keyword) + 3 <= 60:  # " | " を考慮
                optimized_title = f"{target_keyword} | {title}"
            else:
                # タイトルを短縮してキーワードを追加
                max_title_length = 60 - len(target_keyword) - 3
                optimized_title = f"{target_keyword} | {title[:max_title_length]}..."
        
        # 文字数調整
        if len(optimized_title) > 60:
            optimized_title = optimized_title[:57] + "..."
        
        return optimized_title
    
    def _optimize_content(self, content: str, target_keyword: str, target_keywords: List[str], analysis: SEOAnalysis) -> str:
        """コンテンツ最適化"""
        optimized_content = content
        
        # キーワード密度が低い場合の対応
        if analysis.keyword_density_score < 50:
            # キーワードを自然に追加する位置を特定
            # 実際の実装では、より高度な自然言語処理が必要
            pass
        
        # 見出し構造の改善
        if analysis.heading_structure_score < 70:
            # H2見出しが少ない場合の対応
            if len(re.findall(r'^## (.+)', content, re.MULTILINE)) < 3:
                # 適切な位置に見出しを提案（実装は簡略化）
                pass
        
        return optimized_content
    
    def _optimize_meta_description(self, meta_description: str, target_keyword: str, content: str) -> str:
        """メタディスクリプション最適化"""
        if not meta_description:
            # コンテンツの最初の段落から生成
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
            if paragraphs:
                meta_description = paragraphs[0]
            else:
                meta_description = f"{target_keyword}について詳しく解説します。"
        
        # キーワードが含まれていない場合は追加
        if target_keyword and target_keyword.lower() not in meta_description.lower():
            meta_description = f"{target_keyword} - {meta_description}"
        
        # 文字数調整
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."
        elif len(meta_description) < 120:
            meta_description += "詳細情報とお役立ち情報をご紹介します。"
        
        return meta_description
    
    def generate_structured_data(self, 
                                title: str, 
                                content: str, 
                                meta_description: str,
                                author: str = "編集部",
                                image_url: str = "") -> StructuredData:
        """
        構造化データ生成
        
        Args:
            title: 記事タイトル
            content: 記事内容
            meta_description: メタディスクリプション
            author: 著者名
            image_url: 画像URL
            
        Returns:
            StructuredData
        """
        now = datetime.now().isoformat()
        
        # キーワード抽出（簡易版）
        keywords = self._extract_keywords_from_content(content)
        
        return StructuredData(
            type="Article",
            headline=title,
            description=meta_description,
            author=author,
            date_published=now,
            date_modified=now,
            keywords=keywords,
            image_url=image_url
        )
    
    def _extract_keywords_from_content(self, content: str, limit: int = 10) -> List[str]:
        """コンテンツからキーワード抽出（簡易版）"""
        try:
            # 見出しからキーワード抽出
            headings = re.findall(r'^##+ (.+)', content, re.MULTILINE)
            keywords = []
            
            for heading in headings:
                # 簡易的にスペースで分割
                words = heading.split()
                keywords.extend([word for word in words if len(word) > 2])
            
            # 重複除去と制限
            unique_keywords = list(set(keywords))[:limit]
            return unique_keywords
            
        except Exception as e:
            logger.warning(f"キーワード抽出エラー: {e}")
            return []
    
    def analyze_competitors(self, keyword: str, limit: int = 5) -> List[CompetitorAnalysis]:
        """
        競合サイト分析（簡易版）
        
        Args:
            keyword: 分析キーワード
            limit: 分析サイト数
            
        Returns:
            競合分析結果リスト
        """
        try:
            logger.info(f"競合分析開始: {keyword}")
            
            # 実際の実装では検索API（Google Custom Search等）を使用
            # ここでは簡略化
            competitor_results = []
            
            # サンプル競合サイト（実際はAPI結果を使用）
            sample_competitors = [
                "https://example1.com/article1",
                "https://example2.com/article2",
            ]
            
            for url in sample_competitors[:limit]:
                try:
                    # サイト情報取得（実際はWebスクレイピング）
                    analysis = CompetitorAnalysis(
                        competitor_url=url,
                        title_length=55,  # サンプル値
                        meta_description_length=150,
                        heading_count=4,
                        word_count=1800,
                        keyword_density=2.3,
                        backlink_count=25,
                        domain_authority=65.0
                    )
                    competitor_results.append(analysis)
                    
                except Exception as e:
                    logger.warning(f"競合分析エラー {url}: {e}")
                    continue
            
            logger.info(f"競合分析完了: {len(competitor_results)}サイト")
            return competitor_results
            
        except Exception as e:
            logger.error(f"競合分析エラー: {e}")
            return []
    
    def save_analysis_report(self, 
                            analysis: SEOAnalysis, 
                            filename: str = None):
        """
        SEO分析レポートを保存
        
        Args:
            analysis: SEO分析結果
            filename: 保存ファイル名
        """
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"output/seo_analysis_{timestamp}.json"
            
            report_data = {
                'analysis_date': datetime.now().isoformat(),
                'scores': {
                    'title_score': analysis.title_score,
                    'meta_description_score': analysis.meta_description_score,
                    'heading_structure_score': analysis.heading_structure_score,
                    'keyword_density_score': analysis.keyword_density_score,
                    'readability_score': analysis.readability_score,
                    'internal_links_score': analysis.internal_links_score,
                    'image_optimization_score': analysis.image_optimization_score,
                    'overall_seo_score': analysis.overall_seo_score
                },
                'recommendations': analysis.recommendations,
                'warnings': analysis.warnings
            }
            
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"SEO分析レポート保存完了: {filename}")
            
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")

def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO)
    
    # SEO最適化器の初期化
    optimizer = SEOOptimizer()
    
    # サンプル記事でテスト
    sample_title = "Python プログラミングの基礎"
    sample_content = """
# Python プログラミングの基礎

## はじめに
Pythonは初心者にも学びやすいプログラミング言語です。

## Pythonの特徴
- 簡潔な文法
- 豊富なライブラリ
- オープンソース

## 基本的な文法
変数の定義やループ文について説明します。

## まとめ
Pythonは強力で学びやすい言語です。
"""
    sample_meta = "Python プログラミングの基礎について、初心者向けに解説します。"
    target_keyword = "Python プログラミング"
    
    # SEO分析実行
    analysis = optimizer.analyze_article(
        sample_title, 
        sample_content, 
        sample_meta,
        target_keyword
    )
    
    print(f"総合SEOスコア: {analysis.overall_seo_score:.1f}/100")
    print(f"タイトルスコア: {analysis.title_score:.1f}/100") 
    print(f"見出し構造スコア: {analysis.heading_structure_score:.1f}/100")
    
    print("\n推奨事項:")
    for rec in analysis.recommendations[:3]:
        print(f"- {rec}")
    
    print("\n警告:")
    for warn in analysis.warnings[:3]:
        print(f"- {warn}")
    
    # 最適化実行
    optimized = optimizer.optimize_article(
        sample_title,
        sample_content, 
        sample_meta,
        target_keyword
    )
    
    print(f"\n最適化されたタイトル: {optimized['title']}")
    
    # レポート保存
    optimizer.save_analysis_report(analysis)

if __name__ == "__main__":
    main()