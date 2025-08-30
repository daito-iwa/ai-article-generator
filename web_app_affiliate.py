#!/usr/bin/env python3
"""
AI記事生成システム - アフィリエイト収益モデル版
完全無料で利用可能 + アフィリエイト収益
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import sys
import logging
from datetime import datetime
import hashlib
import secrets

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from article_generator import ArticleGenerator, ArticleConfig
from keyword_research import KeywordResearcher
from seo_optimizer import SEOOptimizer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI記事生成システム - 完全無料版", version="2.0.0")

# 静的ファイルとテンプレート設定
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# アフィリエイトリンク設定
AFFILIATE_LINKS = {
    "hosting": [
        {
            "name": "エックスサーバー",
            "description": "国内シェアNo.1の高速レンタルサーバー",
            "url": "https://px.a8.net/svt/ejp?a8mat=YOUR_A8_ID",
            "commission": "1件3,000円〜",
            "banner": "https://www.xserver.ne.jp/banner.jpg"
        },
        {
            "name": "ConoHa WING",
            "description": "表示速度国内No.1のレンタルサーバー",
            "url": "https://px.a8.net/svt/ejp?a8mat=YOUR_CONOHA_ID",
            "commission": "1件2,500円〜",
            "banner": "https://www.conoha.jp/wing/banner.jpg"
        }
    ],
    "wordpress_themes": [
        {
            "name": "SWELL",
            "description": "SEOに強い人気WordPressテーマ",
            "url": "https://swell-theme.com/?ref=YOUR_REF",
            "commission": "1件2,000円",
            "banner": "/static/swell_banner.jpg"
        },
        {
            "name": "JIN:R",
            "description": "アフィリエイトに特化したWordPressテーマ",
            "url": "https://jin-theme.com/?ref=YOUR_REF",
            "commission": "1件1,800円",
            "banner": "/static/jin_banner.jpg"
        }
    ],
    "seo_tools": [
        {
            "name": "Rank Tracker",
            "description": "プロが使う検索順位チェックツール",
            "url": "https://www.seopowersuite.com/rank-tracker/?ref=YOUR_REF",
            "commission": "売上の30%",
            "banner": "/static/ranktracker_banner.jpg"
        },
        {
            "name": "GRC",
            "description": "国産の検索順位チェックツール",
            "url": "https://seopro.jp/grc/?ref=YOUR_REF",
            "commission": "1件1,500円",
            "banner": "/static/grc_banner.jpg"
        }
    ],
    "ai_tools": [
        {
            "name": "ChatGPT Plus",
            "description": "最新のGPT-4が使える有料版",
            "url": "https://openai.com/chatgpt?ref=YOUR_REF",
            "commission": "月額の20%継続",
            "banner": "/static/chatgpt_banner.jpg"
        },
        {
            "name": "Claude Pro",
            "description": "Anthropic社の高性能AI",
            "url": "https://claude.ai/pro?ref=YOUR_REF",
            "commission": "月額の25%継続",
            "banner": "/static/claude_banner.jpg"
        }
    ]
}

# 日次利用制限（無料版）
DAILY_LIMIT = 10  # 1日10記事まで無料

class UsageTracker:
    """利用状況追跡クラス"""
    
    @staticmethod
    def get_usage(identifier: str) -> int:
        """本日の利用回数を取得"""
        usage_file = f"data/usage_{datetime.now().strftime('%Y%m%d')}.json"
        
        if os.path.exists(usage_file):
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage = json.load(f)
                return usage.get(identifier, 0)
        return 0
    
    @staticmethod
    def increment_usage(identifier: str):
        """利用回数をインクリメント"""
        usage_file = f"data/usage_{datetime.now().strftime('%Y%m%d')}.json"
        
        if os.path.exists(usage_file):
            with open(usage_file, 'r', encoding='utf-8') as f:
                usage = json.load(f)
        else:
            usage = {}
        
        usage[identifier] = usage.get(identifier, 0) + 1
        
        with open(usage_file, 'w', encoding='utf-8') as f:
            json.dump(usage, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def can_use(identifier: str) -> bool:
        """利用可能かチェック"""
        return UsageTracker.get_usage(identifier) < DAILY_LIMIT

class ArticleRequest(BaseModel):
    keyword: str
    length: int = 1500
    tone: str = "friendly"
    include_faq: bool = True
    include_affiliate: bool = True  # アフィリエイトリンクを含めるか

# システム初期化
def init_system():
    try:
        with open('config/api_keys.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        article_generator = ArticleGenerator(
            openai_api_key=config.get('openai_api_key'),
            anthropic_api_key=config.get('anthropic_api_key')
        )
        
        keyword_researcher = KeywordResearcher()
        seo_optimizer = SEOOptimizer()
        
        return article_generator, keyword_researcher, seo_optimizer, config
    except Exception as e:
        logger.error(f"システム初期化エラー: {e}")
        return None, None, None, None

generator, researcher, optimizer, config = init_system()

def get_client_identifier(request: Request) -> str:
    """クライアント識別子を取得（IPアドレス）"""
    return request.client.host

def insert_affiliate_links(content: str, keyword: str) -> str:
    """記事にアフィリエイトリンクを自然に挿入"""
    # キーワードに基づいて関連するアフィリエイトを選択
    relevant_affiliates = []
    
    if any(word in keyword.lower() for word in ["wordpress", "ブログ", "サイト"]):
        relevant_affiliates.extend(AFFILIATE_LINKS["hosting"])
        relevant_affiliates.extend(AFFILIATE_LINKS["wordpress_themes"])
    
    if any(word in keyword.lower() for word in ["seo", "検索", "順位"]):
        relevant_affiliates.extend(AFFILIATE_LINKS["seo_tools"])
    
    if any(word in keyword.lower() for word in ["ai", "自動", "生成"]):
        relevant_affiliates.extend(AFFILIATE_LINKS["ai_tools"])
    
    # デフォルトでホスティングを推奨
    if not relevant_affiliates:
        relevant_affiliates = AFFILIATE_LINKS["hosting"][:2]
    
    # アフィリエイトセクションを作成
    affiliate_section = "\n\n## おすすめのツール・サービス\n\n"
    affiliate_section += f"{keyword}を実践する上で、以下のツールやサービスがおすすめです：\n\n"
    
    for aff in relevant_affiliates[:3]:  # 最大3つまで
        affiliate_section += f"### [{aff['name']}]({aff['url']})\n"
        affiliate_section += f"{aff['description']}\n\n"
        affiliate_section += f"[→ {aff['name']}の詳細を見る]({aff['url']})\n\n"
    
    # 記事の適切な位置に挿入
    if "## まとめ" in content:
        content = content.replace("## まとめ", affiliate_section + "## まとめ")
    else:
        content += affiliate_section
    
    return content

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing_affiliate.html", {
        "request": request,
        "daily_limit": DAILY_LIMIT,
        "affiliate_links": AFFILIATE_LINKS
    })

@app.get("/generator", response_class=HTMLResponse)
async def generator_page(request: Request):
    client_id = get_client_identifier(request)
    usage = UsageTracker.get_usage(client_id)
    remaining = DAILY_LIMIT - usage
    
    return templates.TemplateResponse("generator_affiliate.html", {
        "request": request,
        "daily_limit": DAILY_LIMIT,
        "usage": usage,
        "remaining": remaining,
        "can_use": remaining > 0
    })

@app.post("/api/generate-article")
async def generate_article_api(
    request: Request,
    keyword: str = Form(...),
    length: int = Form(1500),
    tone: str = Form("friendly"),
    include_faq: bool = Form(True),
    include_affiliate: bool = Form(True)
):
    client_id = get_client_identifier(request)
    
    # 利用制限チェック
    if not UsageTracker.can_use(client_id):
        raise HTTPException(
            status_code=403,
            detail=f"本日の無料利用枠（{DAILY_LIMIT}記事）に達しました。明日またご利用ください。"
        )
    
    if not generator:
        raise HTTPException(status_code=500, detail="システムが初期化されていません")
    
    try:
        # 記事生成設定
        article_config = ArticleConfig(
            min_length=length,
            max_length=length + 500,
            tone=tone,
            include_faq=include_faq,
            temperature=0.7,
            model="gpt-4"
        )
        
        generator.config = article_config
        
        # 記事生成
        article = generator.generate_article(keyword)
        
        if not article:
            raise HTTPException(status_code=500, detail="記事生成に失敗しました")
        
        # アフィリエイトリンクを挿入
        if include_affiliate:
            article.content = insert_affiliate_links(article.content, keyword)
        
        # 利用回数増加
        UsageTracker.increment_usage(client_id)
        
        # 記事保存
        generator.save_article(article)
        
        # 残り利用可能数
        remaining = DAILY_LIMIT - UsageTracker.get_usage(client_id)
        
        return {
            "success": True,
            "article": {
                "title": article.title,
                "content": article.content,
                "meta_description": article.meta_description,
                "word_count": article.word_count,
                "keyword_density": article.keyword_density,
                "seo_score": article.seo_score,
                "generated_at": article.generated_at
            },
            "usage": {
                "used_today": UsageTracker.get_usage(client_id),
                "remaining": remaining,
                "daily_limit": DAILY_LIMIT
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"記事生成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research-keywords")
async def research_keywords_api(
    request: Request,
    limit: int = Form(10),
    category: str = Form(None)
):
    if not researcher:
        raise HTTPException(status_code=500, detail="システムが初期化されていません")
    
    try:
        keywords = researcher.get_trending_keywords(limit=limit, category=category)
        
        if not keywords:
            return {"success": False, "message": "キーワードが取得できませんでした"}
        
        return {
            "success": True,
            "keywords": [
                {
                    "keyword": kw.main_keyword,
                    "trend_score": kw.trend_score,
                    "related_keywords": kw.related_keywords[:3],
                    "search_volume": kw.search_volume
                }
                for kw in keywords[:10]
            ]
        }
        
    except Exception as e:
        logger.error(f"キーワードリサーチエラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/affiliate-dashboard", response_class=HTMLResponse)
async def affiliate_dashboard(request: Request):
    """アフィリエイト管理画面"""
    return templates.TemplateResponse("affiliate_dashboard.html", {
        "request": request,
        "affiliate_links": AFFILIATE_LINKS
    })

@app.get("/api/usage-stats")
async def usage_stats(request: Request):
    """利用統計API"""
    client_id = get_client_identifier(request)
    usage = UsageTracker.get_usage(client_id)
    
    return {
        "client_id": client_id,
        "usage_today": usage,
        "remaining": DAILY_LIMIT - usage,
        "daily_limit": DAILY_LIMIT
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": generator is not None,
        "model": "affiliate"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 AI記事生成システム（アフィリエイト収益モデル版）起動中...")
    print("📍 URL: http://localhost:8888")
    print("📊 API仕様: http://localhost:8888/docs")
    print("💰 収益モデル: アフィリエイト（完全無料で利用可能）")
    
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)