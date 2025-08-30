#!/usr/bin/env python3
"""
AI記事生成モジュール
OpenAI APIやAnthropic APIを使用して、SEOに最適化された記事を生成する
"""

import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import openai
import anthropic
from keyword_research import KeywordData

logger = logging.getLogger(__name__)

@dataclass
class ArticleConfig:
    """記事生成設定"""
    min_length: int = 1500
    max_length: int = 2500
    target_keyword_density: float = 0.025  # 2.5%
    temperature: float = 0.7
    model: str = "gpt-4"  # gpt-4, gpt-3.5-turbo, claude-3-sonnet
    max_tokens: int = 3000
    language: str = "ja"
    tone: str = "friendly"  # friendly, professional, casual
    include_faq: bool = True
    include_summary: bool = True

@dataclass
class SEOSettings:
    """SEO最適化設定"""
    title_max_length: int = 60
    meta_description_max_length: int = 160
    min_headings: int = 3
    max_headings: int = 6
    heading_keyword_density: float = 0.5  # 見出しにキーワードを含める割合
    internal_links_count: int = 2
    external_links_count: int = 1

@dataclass
class GeneratedArticle:
    """生成された記事データ"""
    title: str
    content: str
    meta_description: str
    keywords: List[str]
    headings: List[str]
    word_count: int
    keyword_density: float
    readability_score: float
    seo_score: float
    generated_at: str
    model_used: str
    generation_time: float

class ArticleGenerator:
    """AI記事生成クラス"""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 anthropic_api_key: Optional[str] = None,
                 config: ArticleConfig = ArticleConfig(),
                 seo_settings: SEOSettings = SEOSettings()):
        """
        初期化
        
        Args:
            openai_api_key: OpenAI APIキー
            anthropic_api_key: Anthropic APIキー  
            config: 記事生成設定
            seo_settings: SEO設定
        """
        self.config = config
        self.seo_settings = seo_settings
        
        # API設定
        if openai_api_key:
            openai.api_key = openai_api_key
            
        if anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
        else:
            self.anthropic_client = None
    
    def generate_article(self, 
                        keyword_data: Union[KeywordData, str], 
                        additional_context: str = "",
                        custom_outline: Optional[List[str]] = None) -> Optional[GeneratedArticle]:
        """
        記事を生成
        
        Args:
            keyword_data: キーワードデータ または キーワード文字列
            additional_context: 追加のコンテキスト情報
            custom_outline: カスタム見出し構成
            
        Returns:
            GeneratedArticle or None
        """
        start_time = time.time()
        
        try:
            # キーワード情報の準備
            if isinstance(keyword_data, str):
                main_keyword = keyword_data
                related_keywords = []
            else:
                main_keyword = keyword_data.main_keyword
                related_keywords = keyword_data.related_keywords + keyword_data.rising_keywords
                
            logger.info(f"記事生成開始: {main_keyword}")
            
            # プロンプト生成
            prompt = self._create_article_prompt(
                main_keyword, 
                related_keywords, 
                additional_context,
                custom_outline
            )
            
            # AI APIで記事生成
            raw_content = self._call_ai_api(prompt)
            if not raw_content:
                return None
            
            # 記事構造解析
            structured_content = self._parse_article_structure(raw_content)
            
            # SEO最適化
            optimized_article = self._optimize_for_seo(
                structured_content, 
                main_keyword, 
                related_keywords
            )
            
            # 品質評価
            quality_metrics = self._evaluate_article_quality(
                optimized_article, 
                main_keyword
            )
            
            generation_time = time.time() - start_time
            
            # GeneratedArticleオブジェクト作成
            article = GeneratedArticle(
                title=optimized_article.get('title', ''),
                content=optimized_article.get('content', ''),
                meta_description=optimized_article.get('meta_description', ''),
                keywords=[main_keyword] + related_keywords[:4],
                headings=optimized_article.get('headings', []),
                word_count=quality_metrics['word_count'],
                keyword_density=quality_metrics['keyword_density'],
                readability_score=quality_metrics['readability_score'],
                seo_score=quality_metrics['seo_score'],
                generated_at=datetime.now().isoformat(),
                model_used=self.config.model,
                generation_time=generation_time
            )
            
            logger.info(f"記事生成完了: {main_keyword} ({generation_time:.2f}s)")
            return article
            
        except Exception as e:
            logger.error(f"記事生成エラー: {e}")
            return None
    
    def _create_article_prompt(self, 
                              main_keyword: str, 
                              related_keywords: List[str],
                              additional_context: str = "",
                              custom_outline: Optional[List[str]] = None) -> str:
        """
        記事生成用プロンプトを作成
        
        Args:
            main_keyword: メインキーワード
            related_keywords: 関連キーワード
            additional_context: 追加コンテキスト
            custom_outline: カスタム見出し
            
        Returns:
            プロンプト文字列
        """
        related_str = ", ".join(related_keywords[:5]) if related_keywords else ""
        
        # 基本プロンプト
        base_prompt = f"""
あなたはSEOに精通したプロのライターです。以下の条件で「{main_keyword}」についての記事を作成してください：

## 記事要件
1. **文字数**: {self.config.min_length}〜{self.config.max_length}文字
2. **言語**: 日本語
3. **トーン**: {self._get_tone_description(self.config.tone)}
4. **対象読者**: 初心者から中級者

## SEO要件
1. **メインキーワード**: 「{main_keyword}」を自然に含める（密度約{self.config.target_keyword_density*100:.1f}%）
2. **関連キーワード**: {related_str}
3. **見出し**: H2, H3タグを{self.seo_settings.min_headings}〜{self.seo_settings.max_headings}個使用
4. **構造**: 導入→本文→まとめの流れ

## 記事構成
"""
        
        # カスタム見出し構成がある場合
        if custom_outline:
            base_prompt += "\n以下の見出し構成に従って記事を作成してください：\n"
            for i, heading in enumerate(custom_outline, 1):
                base_prompt += f"{i}. {heading}\n"
        else:
            base_prompt += """
1. **導入部** (200-300文字)
   - 読者の関心を引く
   - 記事で学べることを明示

2. **本文** (複数のH2見出しで構成)
   - 実用的な情報と具体例
   - 読者の疑問に答える内容
   - データや事例を含める

3. **まとめ** (150-200文字)
   - 重要ポイントの整理
   - 読者へのアクションアイテム
"""
        
        # 追加コンテキスト
        if additional_context:
            base_prompt += f"\n## 追加情報\n{additional_context}\n"
        
        # FAQセクション
        if self.config.include_faq:
            base_prompt += "\n4. **FAQ**: よくある質問3-5個を含めてください\n"
        
        base_prompt += """
## 出力形式
以下の形式で出力してください：

# [記事タイトル]

[導入文]

## [見出し1]
[内容]

## [見出し2]  
[内容]

## まとめ
[まとめ文]

---
META_DESCRIPTION: [120-160文字のメタディスクリプション]
"""
        
        return base_prompt
    
    def _get_tone_description(self, tone: str) -> str:
        """トーン説明を取得"""
        tone_map = {
            "friendly": "親しみやすく、読みやすい文体",
            "professional": "専門的で信頼性のある文体", 
            "casual": "カジュアルで親近感のある文体"
        }
        return tone_map.get(tone, "親しみやすい文体")
    
    def _call_ai_api(self, prompt: str) -> Optional[str]:
        """
        AI APIを呼び出して記事を生成
        
        Args:
            prompt: 生成プロンプト
            
        Returns:
            生成された記事 or None
        """
        try:
            if self.config.model.startswith("gpt"):
                return self._call_openai_api(prompt)
            elif self.config.model.startswith("claude"):
                return self._call_anthropic_api(prompt)
            else:
                logger.error(f"サポートされていないモデル: {self.config.model}")
                return None
                
        except Exception as e:
            logger.error(f"AI API呼び出しエラー: {e}")
            return None
    
    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """OpenAI API呼び出し"""
        try:
            response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "あなたはSEOに精通したプロのライターです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API エラー: {e}")
            return None
    
    def _call_anthropic_api(self, prompt: str) -> Optional[str]:
        """Anthropic API呼び出し"""
        if not self.anthropic_client:
            logger.error("Anthropic APIキーが設定されていません")
            return None
            
        try:
            message = self.anthropic_client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API エラー: {e}")
            return None
    
    def _parse_article_structure(self, raw_content: str) -> Dict:
        """
        生成された記事の構造を解析
        
        Args:
            raw_content: 生成された記事
            
        Returns:
            構造化された記事データ
        """
        # メタディスクリプション抽出
        meta_description = ""
        meta_match = re.search(r'META_DESCRIPTION:\s*(.+)', raw_content)
        if meta_match:
            meta_description = meta_match.group(1).strip()
            raw_content = re.sub(r'---\s*META_DESCRIPTION:.*', '', raw_content, flags=re.DOTALL)
        
        # タイトル抽出
        title_match = re.search(r'^#\s+(.+)', raw_content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else ""
        
        # 見出し抽出
        headings = re.findall(r'^##\s+(.+)', raw_content, re.MULTILINE)
        
        # 本文抽出（メタ情報を除去）
        content = re.sub(r'^#\s+.+', '', raw_content, flags=re.MULTILINE).strip()
        content = re.sub(r'---.*$', '', content, flags=re.DOTALL).strip()
        
        return {
            'title': title,
            'content': content,
            'meta_description': meta_description,
            'headings': headings
        }
    
    def _optimize_for_seo(self, 
                         structured_content: Dict, 
                         main_keyword: str,
                         related_keywords: List[str]) -> Dict:
        """
        SEO最適化処理
        
        Args:
            structured_content: 構造化された記事
            main_keyword: メインキーワード
            related_keywords: 関連キーワード
            
        Returns:
            最適化された記事
        """
        try:
            optimized = structured_content.copy()
            
            # タイトル最適化
            optimized['title'] = self._optimize_title(
                structured_content['title'], 
                main_keyword
            )
            
            # メタディスクリプション最適化
            if not optimized['meta_description']:
                optimized['meta_description'] = self._generate_meta_description(
                    structured_content['content'], 
                    main_keyword
                )
            
            # 本文のキーワード密度調整
            optimized['content'] = self._adjust_keyword_density(
                structured_content['content'],
                main_keyword,
                related_keywords
            )
            
            return optimized
            
        except Exception as e:
            logger.error(f"SEO最適化エラー: {e}")
            return structured_content
    
    def _optimize_title(self, title: str, main_keyword: str) -> str:
        """タイトル最適化"""
        if not title:
            title = f"{main_keyword}について知っておくべき重要なポイント"
        
        # キーワードがタイトルに含まれていない場合は追加
        if main_keyword.lower() not in title.lower():
            title = f"{main_keyword} | {title}"
        
        # 文字数調整
        if len(title) > self.seo_settings.title_max_length:
            title = title[:self.seo_settings.title_max_length-3] + "..."
            
        return title
    
    def _generate_meta_description(self, content: str, main_keyword: str) -> str:
        """メタディスクリプション生成"""
        # 最初の段落から抽出
        paragraphs = content.split('\n\n')
        first_paragraph = next((p for p in paragraphs if len(p.strip()) > 50), '')
        
        if first_paragraph:
            meta_desc = first_paragraph.strip()
        else:
            meta_desc = f"{main_keyword}について詳しく解説します。初心者にもわかりやすく説明していますので、ぜひご参考ください。"
        
        # 文字数調整
        if len(meta_desc) > self.seo_settings.meta_description_max_length:
            meta_desc = meta_desc[:self.seo_settings.meta_description_max_length-3] + "..."
            
        return meta_desc
    
    def _adjust_keyword_density(self, 
                               content: str, 
                               main_keyword: str,
                               related_keywords: List[str]) -> str:
        """キーワード密度調整"""
        # 実装は簡略化
        # 実際はより高度な自然言語処理が必要
        return content
    
    def _evaluate_article_quality(self, article: Dict, main_keyword: str) -> Dict:
        """
        記事品質評価
        
        Args:
            article: 記事データ
            main_keyword: メインキーワード
            
        Returns:
            品質メトリクス
        """
        content = article.get('content', '')
        
        # 文字数カウント
        word_count = len(content.replace(' ', ''))
        
        # キーワード密度計算
        keyword_count = content.lower().count(main_keyword.lower())
        keyword_density = (keyword_count / max(word_count, 1)) * 100
        
        # 読みやすさスコア（簡易版）
        readability_score = self._calculate_readability_score(content)
        
        # SEOスコア（簡易版）
        seo_score = self._calculate_seo_score(article, main_keyword)
        
        return {
            'word_count': word_count,
            'keyword_density': keyword_density,
            'readability_score': readability_score,
            'seo_score': seo_score
        }
    
    def _calculate_readability_score(self, content: str) -> float:
        """読みやすさスコア計算（簡易版）"""
        try:
            sentences = re.split(r'[。！？]', content)
            sentence_count = len([s for s in sentences if s.strip()])
            
            if sentence_count == 0:
                return 0.0
                
            words_per_sentence = len(content) / sentence_count
            
            # 簡易スコア（100点満点）
            if words_per_sentence < 20:
                return 90.0
            elif words_per_sentence < 30:
                return 80.0
            elif words_per_sentence < 40:
                return 70.0
            else:
                return 60.0
                
        except Exception:
            return 70.0
    
    def _calculate_seo_score(self, article: Dict, main_keyword: str) -> float:
        """SEOスコア計算（簡易版）"""
        score = 0.0
        
        # タイトルにキーワード
        if main_keyword.lower() in article.get('title', '').lower():
            score += 20
        
        # メタディスクリプションにキーワード
        if main_keyword.lower() in article.get('meta_description', '').lower():
            score += 15
        
        # 見出し数
        heading_count = len(article.get('headings', []))
        if self.seo_settings.min_headings <= heading_count <= self.seo_settings.max_headings:
            score += 20
        
        # 文字数
        word_count = len(article.get('content', ''))
        if self.config.min_length <= word_count <= self.config.max_length:
            score += 25
        
        # キーワード密度
        keyword_count = article.get('content', '').lower().count(main_keyword.lower())
        if word_count > 0:
            density = (keyword_count / word_count) * 100
            if 1.0 <= density <= 4.0:
                score += 20
        
        return min(100.0, score)
    
    def save_article(self, article: GeneratedArticle, output_dir: str = "output/articles"):
        """
        記事をファイルに保存
        
        Args:
            article: 生成された記事
            output_dir: 出力ディレクトリ
        """
        try:
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            keyword_safe = re.sub(r'[^\w\-_.]', '_', article.keywords[0])
            
            # JSON形式で保存
            json_filename = f"{output_dir}/{timestamp}_{keyword_safe}.json"
            article_dict = {
                'title': article.title,
                'content': article.content,
                'meta_description': article.meta_description,
                'keywords': article.keywords,
                'headings': article.headings,
                'word_count': article.word_count,
                'keyword_density': article.keyword_density,
                'readability_score': article.readability_score,
                'seo_score': article.seo_score,
                'generated_at': article.generated_at,
                'model_used': article.model_used,
                'generation_time': article.generation_time
            }
            
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(article_dict, f, ensure_ascii=False, indent=2)
            
            # Markdown形式でも保存
            md_filename = f"{output_dir}/{timestamp}_{keyword_safe}.md"
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(f"# {article.title}\n\n")
                f.write(article.content)
                f.write(f"\n\n---\n")
                f.write(f"**メタディスクリプション**: {article.meta_description}\n")
                f.write(f"**キーワード**: {', '.join(article.keywords)}\n")
                f.write(f"**文字数**: {article.word_count}\n")
                f.write(f"**SEOスコア**: {article.seo_score:.1f}/100\n")
            
            logger.info(f"記事保存完了: {json_filename}")
            
        except Exception as e:
            logger.error(f"記事保存エラー: {e}")

def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO)
    
    # 設定（実際の使用時はconfig.jsonから読み込み）
    config = ArticleConfig(
        min_length=1500,
        max_length=2000,
        model="gpt-4",
        temperature=0.7
    )
    
    # 記事生成器初期化（APIキーは環境変数から取得することを推奨）
    generator = ArticleGenerator(
        openai_api_key="your-openai-key",  # 実際はos.getenv()を使用
        config=config
    )
    
    # テスト記事生成
    test_keyword = "AI 記事 生成"
    article = generator.generate_article(test_keyword)
    
    if article:
        print(f"タイトル: {article.title}")
        print(f"文字数: {article.word_count}")
        print(f"SEOスコア: {article.seo_score:.1f}")
        print(f"生成時間: {article.generation_time:.2f}秒")
        
        # 保存
        generator.save_article(article)
    else:
        print("記事生成に失敗しました")

if __name__ == "__main__":
    main()