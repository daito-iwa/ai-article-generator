#!/usr/bin/env python3
"""
AI記事生成システム - Web UI (FastAPI)
収益化対応版
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import json
import os
import sys
import logging
from datetime import datetime, timedelta
import hashlib
import secrets
from dataclasses import asdict

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from article_generator import ArticleGenerator, ArticleConfig
from keyword_research import KeywordResearcher
from seo_optimizer import SEOOptimizer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI記事生成システム", version="1.0.0")

# 静的ファイルとテンプレート設定
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# データベース（簡易版 - JSON）
USERS_DB = "data/users.json"
USAGE_DB = "data/usage.json"
ARTICLES_DB = "data/articles.json"

# プラン設定
PLANS = {
    "free": {"name": "無料プラン", "articles_per_month": 3, "price": 0},
    "basic": {"name": "ベーシック", "articles_per_month": 10, "price": 2900},
    "pro": {"name": "プロ", "articles_per_month": 50, "price": 9900},
    "enterprise": {"name": "エンタープライズ", "articles_per_month": 999, "price": 29900}
}

class User:
    """ユーザー管理クラス"""
    
    @staticmethod
    def load_users():
        if os.path.exists(USERS_DB):
            with open(USERS_DB, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def save_users(users):
        with open(USERS_DB, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def create_user(email: str, password: str, plan: str = "free"):
        users = User.load_users()
        
        if email in users:
            return False
        
        user_id = hashlib.md5(email.encode()).hexdigest()[:8]
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        users[email] = {
            "user_id": user_id,
            "password_hash": password_hash,
            "plan": plan,
            "created_at": datetime.now().isoformat(),
            "api_key": secrets.token_urlsafe(32),
            "articles_used": 0,
            "last_reset": datetime.now().replace(day=1).isoformat()
        }
        
        User.save_users(users)
        return True
    
    @staticmethod
    def authenticate(email: str, password: str):
        users = User.load_users()
        if email not in users:
            return None
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if users[email]["password_hash"] == password_hash:
            return users[email]
        return None
    
    @staticmethod
    def get_user_by_api_key(api_key: str):
        users = User.load_users()
        for email, user_data in users.items():
            if user_data.get("api_key") == api_key:
                return {**user_data, "email": email}
        return None
    
    @staticmethod
    def can_generate_article(email: str):
        users = User.load_users()
        if email not in users:
            return False
        
        user = users[email]
        plan_limit = PLANS[user["plan"]]["articles_per_month"]
        
        # 月次リセット確認
        last_reset = datetime.fromisoformat(user["last_reset"])
        now = datetime.now()
        if now.month != last_reset.month or now.year != last_reset.year:
            user["articles_used"] = 0
            user["last_reset"] = now.replace(day=1).isoformat()
            User.save_users(users)
        
        return user["articles_used"] < plan_limit
    
    @staticmethod
    def increment_usage(email: str):
        users = User.load_users()
        if email in users:
            users[email]["articles_used"] += 1
            User.save_users(users)

class ArticleRequest(BaseModel):
    keyword: str
    length: int = 1500
    tone: str = "friendly"
    include_faq: bool = True

class APIKeyRequest(BaseModel):
    api_key: str

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

# 認証依存関数
def get_current_user(api_key: str = Form(...)):
    user = User.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="無効なAPIキーです")
    return user

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {
        "request": request,
        "plans": PLANS
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "plans": PLANS
    })

@app.post("/register")
async def register(
    email: str = Form(...),
    password: str = Form(...),
    plan: str = Form("free")
):
    if plan not in PLANS:
        raise HTTPException(status_code=400, detail="無効なプランです")
    
    if User.create_user(email, password, plan):
        return {"success": True, "message": "登録完了"}
    else:
        raise HTTPException(status_code=400, detail="既に登録されているメールアドレスです")

@app.post("/login")
async def login(
    email: str = Form(...),
    password: str = Form(...)
):
    user = User.authenticate(email, password)
    if user:
        return {
            "success": True,
            "api_key": user["api_key"],
            "plan": user["plan"],
            "articles_used": user["articles_used"],
            "articles_limit": PLANS[user["plan"]]["articles_per_month"]
        }
    else:
        raise HTTPException(status_code=401, detail="認証に失敗しました")

@app.post("/api/generate-article")
async def generate_article_api(
    request: ArticleRequest,
    current_user: dict = Depends(get_current_user)
):
    # 利用制限チェック
    if not User.can_generate_article(current_user["email"]):
        raise HTTPException(
            status_code=403, 
            detail=f"月間利用制限に達しました。プランを{PLANS[current_user['plan']]['name']}でご利用ください。"
        )
    
    if not generator:
        raise HTTPException(status_code=500, detail="システムが初期化されていません")
    
    try:
        # 記事生成設定
        article_config = ArticleConfig(
            min_length=request.length,
            max_length=request.length + 500,
            tone=request.tone,
            include_faq=request.include_faq,
            temperature=0.7,
            model="gpt-4"
        )
        
        generator.config = article_config
        
        # 記事生成
        article = generator.generate_article(request.keyword)
        
        if not article:
            raise HTTPException(status_code=500, detail="記事生成に失敗しました")
        
        # 使用量増加
        User.increment_usage(current_user["email"])
        
        # 記事保存
        generator.save_article(article)
        
        # レスポンス
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
                "articles_used": current_user["articles_used"] + 1,
                "articles_limit": PLANS[current_user["plan"]]["articles_per_month"]
            }
        }
        
    except Exception as e:
        logger.error(f"記事生成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/research-keywords")
async def research_keywords_api(
    limit: int = Form(10),
    category: str = Form(None),
    current_user: dict = Depends(get_current_user)
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

@app.get("/api/user/status")
async def user_status(current_user: dict = Depends(get_current_user)):
    plan_info = PLANS[current_user["plan"]]
    
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "plan": current_user["plan"],
        "plan_name": plan_info["name"],
        "articles_used": current_user["articles_used"],
        "articles_limit": plan_info["articles_per_month"],
        "price": plan_info["price"]
    }

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {
        "request": request,
        "plans": PLANS
    })

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": generator is not None
    }

if __name__ == "__main__":
    import uvicorn
    
    print("AI記事生成システム Web UI 起動中...")
    print("URL: http://localhost:8080")
    print("API仕様: http://localhost:8080/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)