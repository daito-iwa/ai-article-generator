#!/usr/bin/env python3
"""
キーワードリサーチモジュール
Google Trendsからトレンドキーワードを収集し、関連キーワードも取得する
"""

import time
import json
import csv
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from pytrends.request import TrendReq
import requests

logger = logging.getLogger(__name__)

@dataclass
class KeywordData:
    """キーワードデータクラス"""
    main_keyword: str
    search_volume: str  # high, medium, low, unknown
    competition: str    # high, medium, low, unknown  
    related_keywords: List[str]
    rising_keywords: List[str]
    trend_score: float
    category: str
    collected_at: str

class KeywordResearcher:
    """トレンドキーワード収集クラス"""
    
    def __init__(self, geo: str = 'JP', hl: str = 'ja-JP', tz: int = 540):
        """
        初期化
        
        Args:
            geo: 地理的な場所 (JP=日本)
            hl: 言語設定
            tz: タイムゾーン (540=JST)
        """
        self.geo = geo
        self.hl = hl
        self.tz = tz
        self.pytrends = TrendReq(hl=hl, tz=tz)
        
    def get_trending_keywords(self, 
                            category: Optional[str] = None, 
                            limit: int = 10,
                            timeframe: str = 'now 7-d') -> List[KeywordData]:
        """
        トレンドキーワードを取得
        
        Args:
            category: カテゴリ指定 (None=全カテゴリ)
            limit: 取得するキーワード数
            timeframe: 期間指定
            
        Returns:
            KeywordDataのリスト
        """
        try:
            logger.info(f"トレンドキーワード取得開始: limit={limit}, category={category}")
            
            # 日本のトレンド検索を取得
            trending_searches = self.pytrends.trending_searches(pn=self.geo.lower())
            base_keywords = trending_searches[0].tolist()[:limit]
            
            keyword_data_list = []
            
            for keyword in base_keywords:
                try:
                    # 関連情報を取得
                    keyword_data = self._analyze_keyword(keyword, timeframe)
                    if keyword_data:
                        keyword_data_list.append(keyword_data)
                        
                    # API制限対策
                    time.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"キーワード分析エラー {keyword}: {e}")
                    continue
                    
            logger.info(f"取得完了: {len(keyword_data_list)}個のキーワード")
            return keyword_data_list
            
        except Exception as e:
            logger.error(f"トレンドキーワード取得エラー: {e}")
            return []
    
    def _analyze_keyword(self, keyword: str, timeframe: str = 'now 7-d') -> Optional[KeywordData]:
        """
        個別キーワードを分析
        
        Args:
            keyword: 分析するキーワード
            timeframe: 分析期間
            
        Returns:
            KeywordData or None
        """
        try:
            # Google Trendsでキーワード分析
            self.pytrends.build_payload([keyword], 
                                      cat=0, 
                                      timeframe=timeframe, 
                                      geo=self.geo)
            
            # 関連キーワード取得
            related_queries = self.pytrends.related_queries()
            related_keywords = []
            rising_keywords = []
            
            if keyword in related_queries:
                # トップ関連キーワード
                if related_queries[keyword]['top'] is not None:
                    related_keywords = related_queries[keyword]['top']['query'].tolist()[:5]
                
                # 急上昇関連キーワード
                if related_queries[keyword]['rising'] is not None:
                    rising_keywords = related_queries[keyword]['rising']['query'].tolist()[:5]
            
            # 検索ボリューム推定
            search_volume = self._estimate_search_volume(keyword)
            
            # 競合性推定
            competition = self._estimate_competition(keyword, related_keywords)
            
            # トレンドスコア計算
            trend_score = self._calculate_trend_score(keyword)
            
            return KeywordData(
                main_keyword=keyword,
                search_volume=search_volume,
                competition=competition,
                related_keywords=related_keywords,
                rising_keywords=rising_keywords,
                trend_score=trend_score,
                category="general",
                collected_at=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"キーワード分析エラー {keyword}: {e}")
            return None
    
    def _estimate_search_volume(self, keyword: str) -> str:
        """
        検索ボリュームを推定
        
        Args:
            keyword: キーワード
            
        Returns:
            'high', 'medium', 'low', 'unknown'
        """
        try:
            # 過去3ヶ月の検索トレンド取得
            self.pytrends.build_payload([keyword], 
                                      timeframe='today 3-m', 
                                      geo=self.geo)
            
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                avg_interest = interest_over_time[keyword].mean()
                max_interest = interest_over_time[keyword].max()
                
                # 判定基準
                if avg_interest > 60 or max_interest > 80:
                    return "high"
                elif avg_interest > 25 or max_interest > 50:
                    return "medium"
                else:
                    return "low"
            
            return "unknown"
            
        except Exception as e:
            logger.warning(f"検索ボリューム推定エラー {keyword}: {e}")
            return "unknown"
    
    def _estimate_competition(self, keyword: str, related_keywords: List[str]) -> str:
        """
        競合性を推定
        
        Args:
            keyword: メインキーワード
            related_keywords: 関連キーワードリスト
            
        Returns:
            'high', 'medium', 'low', 'unknown'
        """
        try:
            # 関連キーワード数による簡易判定
            related_count = len(related_keywords)
            
            # キーワードの長さ（ロングテール指標）
            word_count = len(keyword.split())
            
            # 判定ロジック
            if related_count > 15 and word_count <= 2:
                return "high"
            elif related_count > 8 or word_count <= 2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.warning(f"競合性推定エラー {keyword}: {e}")
            return "unknown"
    
    def _calculate_trend_score(self, keyword: str) -> float:
        """
        トレンドスコアを計算
        
        Args:
            keyword: キーワード
            
        Returns:
            0-100のトレンドスコア
        """
        try:
            # 過去1週間の検索トレンド
            self.pytrends.build_payload([keyword], 
                                      timeframe='now 7-d', 
                                      geo=self.geo)
            
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                values = interest_over_time[keyword].values
                if len(values) > 1:
                    # 直近の上昇傾向を評価
                    recent_trend = (values[-1] - values[0]) / max(values[0], 1)
                    base_score = interest_over_time[keyword].mean()
                    
                    # トレンドスコア = ベーススコア + 上昇傾向ボーナス
                    trend_score = min(100, base_score + (recent_trend * 50))
                    return max(0, trend_score)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"トレンドスコア計算エラー {keyword}: {e}")
            return 0.0
    
    def get_category_trends(self, category_id: int, limit: int = 20) -> List[KeywordData]:
        """
        特定カテゴリのトレンドキーワードを取得
        
        Args:
            category_id: Google TrendsカテゴリID
            limit: 取得数
            
        Returns:
            KeywordDataのリスト
        """
        try:
            logger.info(f"カテゴリトレンド取得: category={category_id}")
            
            # カテゴリ別トレンド取得（実装は簡略化）
            # 実際はGoogle Trends APIの制限により、
            # カテゴリ指定でのトレンド取得は限定的
            
            return self.get_trending_keywords(limit=limit)
            
        except Exception as e:
            logger.error(f"カテゴリトレンド取得エラー: {e}")
            return []
    
    def export_to_csv(self, keyword_data_list: List[KeywordData], filename: str):
        """
        キーワードデータをCSVに出力
        
        Args:
            keyword_data_list: キーワードデータリスト
            filename: 出力ファイル名
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'main_keyword', 'search_volume', 'competition',
                    'related_keywords', 'rising_keywords', 'trend_score',
                    'category', 'collected_at'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for data in keyword_data_list:
                    writer.writerow({
                        'main_keyword': data.main_keyword,
                        'search_volume': data.search_volume,
                        'competition': data.competition,
                        'related_keywords': ', '.join(data.related_keywords),
                        'rising_keywords': ', '.join(data.rising_keywords),
                        'trend_score': data.trend_score,
                        'category': data.category,
                        'collected_at': data.collected_at
                    })
                    
            logger.info(f"CSV出力完了: {filename}")
            
        except Exception as e:
            logger.error(f"CSV出力エラー: {e}")
    
    def save_keyword_data(self, keyword_data_list: List[KeywordData], filepath: str):
        """
        キーワードデータをJSONファイルに保存
        
        Args:
            keyword_data_list: キーワードデータリスト  
            filepath: 保存先ファイルパス
        """
        try:
            data_dict_list = []
            for data in keyword_data_list:
                data_dict_list.append({
                    'main_keyword': data.main_keyword,
                    'search_volume': data.search_volume,
                    'competition': data.competition,
                    'related_keywords': data.related_keywords,
                    'rising_keywords': data.rising_keywords,
                    'trend_score': data.trend_score,
                    'category': data.category,
                    'collected_at': data.collected_at
                })
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_dict_list, f, ensure_ascii=False, indent=2)
                
            logger.info(f"キーワードデータ保存完了: {filepath}")
            
        except Exception as e:
            logger.error(f"キーワードデータ保存エラー: {e}")

def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO)
    
    researcher = KeywordResearcher()
    
    # トレンドキーワード取得
    keywords = researcher.get_trending_keywords(limit=10)
    
    # 結果表示
    for keyword_data in keywords:
        print(f"キーワード: {keyword_data.main_keyword}")
        print(f"検索ボリューム: {keyword_data.search_volume}")
        print(f"競合性: {keyword_data.competition}")
        print(f"トレンドスコア: {keyword_data.trend_score:.2f}")
        print(f"関連キーワード: {', '.join(keyword_data.related_keywords[:3])}")
        print("-" * 50)
    
    # CSV出力
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    researcher.export_to_csv(keywords, f"output/keywords_{timestamp}.csv")
    researcher.save_keyword_data(keywords, f"output/keywords_{timestamp}.json")

if __name__ == "__main__":
    main()