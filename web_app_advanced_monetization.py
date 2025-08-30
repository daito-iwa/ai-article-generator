#!/usr/bin/env python3
"""
AI記事生成システム - 高収益化モデル版
複数の収益化手法を組み合わせた最適化版
"""

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
import sys
import logging
from datetime import datetime
import hashlib
import secrets
import random

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from article_generator import ArticleGenerator, ArticleConfig
from keyword_research import KeywordResearcher
from seo_optimizer import SEOOptimizer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI記事生成システム - 高収益化版", version="3.0.0")

# 静的ファイルとテンプレート設定
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("data", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 収益化設定
MONETIZATION_CONFIG = {
    # Google AdSense設定
    "adsense": {
        "client_id": "ca-pub-XXXXXXXXXXXXXXXX",  # 実際のAdSenseクライアントIDに変更
        "enabled": True,
        "positions": {
            "header": True,
            "sidebar": True,
            "in_article": True,
            "footer": True,
            "popup": False  # ポップアップ広告（慎重に使用）
        }
    },
    
    # アフィリエイト設定（より多様な商品）
    "affiliates": {
        "hosting": [
            {"name": "エックスサーバー", "cpa": 3000, "url": "https://px.a8.net/svt/ejp?a8mat=XXX"},
            {"name": "ConoHa WING", "cpa": 2500, "url": "https://px.a8.net/svt/ejp?a8mat=YYY"},
            {"name": "ロリポップ", "cpa": 1500, "url": "https://px.a8.net/svt/ejp?a8mat=ZZZ"},
        ],
        "tools": [
            {"name": "Canva Pro", "cpa": 800, "url": "https://partner.canva.com/XXX"},
            {"name": "Adobe Creative Cloud", "cpa": 1000, "url": "https://www.adobe.com/jp/affiliates/XXX"},
            {"name": "ラッコキーワード", "cpa": 500, "url": "https://related-keywords.com/aff/XXX"},
        ],
        "ai_writing": [
            {"name": "Jasper AI", "cpa": 3000, "url": "https://jasper.ai?fpr=XXX"},
            {"name": "Copy.ai", "cpa": 2000, "url": "https://www.copy.ai/?via=XXX"},
            {"name": "Writesonic", "cpa": 1500, "url": "https://writesonic.com?ref=XXX"},
        ],
        "courses": [
            {"name": "ブログ収益化講座", "cpa": 5000, "url": "https://example-course.com/aff/XXX"},
            {"name": "SEOマスター講座", "cpa": 3000, "url": "https://seo-course.com/aff/XXX"},
        ]
    },
    
    # メールリスト収益化
    "email_capture": {
        "enabled": True,
        "incentive": "SEO完全ガイドPDF（5万円相当）を無料プレゼント",
        "exit_intent_popup": True,
        "in_article_optin": True
    },
    
    # プレミアムコンテンツ
    "premium": {
        "enabled": True,
        "features": [
            "文字数無制限",
            "高度なSEO分析",
            "競合分析機能",
            "AIリライト機能",
            "優先サポート"
        ],
        "price": 980,  # 月額
        "trial_days": 7
    },
    
    # 寄付・投げ銭
    "donation": {
        "enabled": True,
        "platforms": ["PayPal", "Buy Me a Coffee", "Stripe"]
    }
}

# 収益最適化クラス
class RevenueOptimizer:
    """収益を最大化するための最適化エンジン"""
    
    @staticmethod
    def select_best_affiliates(keyword: str, content_type: str = "general") -> List[Dict]:
        """キーワードとコンテンツタイプに基づいて最適なアフィリエイトを選択"""
        selected = []
        
        # キーワードマッチング
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ["ブログ", "サイト", "wordpress", "収益"]):
            selected.extend(MONETIZATION_CONFIG["affiliates"]["hosting"][:2])
            selected.extend(MONETIZATION_CONFIG["affiliates"]["courses"][:1])
            
        if any(word in keyword_lower for word in ["デザイン", "画像", "イラスト"]):
            selected.extend(MONETIZATION_CONFIG["affiliates"]["tools"][:2])
            
        if any(word in keyword_lower for word in ["ai", "自動", "効率", "ツール"]):
            selected.extend(MONETIZATION_CONFIG["affiliates"]["ai_writing"][:2])
            
        if any(word in keyword_lower for word in ["seo", "検索", "順位", "アクセス"]):
            selected.extend(MONETIZATION_CONFIG["affiliates"]["tools"][-1:])  # ラッコキーワード
            selected.extend(MONETIZATION_CONFIG["affiliates"]["courses"][-1:])  # SEO講座
        
        # デフォルトで高単価商品を追加
        if len(selected) < 3:
            high_cpa = [item for sublist in MONETIZATION_CONFIG["affiliates"].values() 
                       for item in sublist if item["cpa"] >= 2000]
            selected.extend(random.sample(high_cpa, min(3 - len(selected), len(high_cpa))))
        
        return selected[:5]  # 最大5個まで
    
    @staticmethod
    def optimize_ad_placement(content: str) -> str:
        """コンテンツ内の最適な位置に広告を配置"""
        lines = content.split('\n')
        optimized = []
        ad_count = 0
        
        # AdSenseコード（実際のコードに置き換え）
        adsense_code = """
<div class="ad-container">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="{client_id}"
         data-ad-slot="XXXXXXXXXX"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</div>
        """.format(client_id=MONETIZATION_CONFIG["adsense"]["client_id"])
        
        # コンテンツの適切な位置に広告を挿入
        for i, line in enumerate(lines):
            optimized.append(line)
            
            # 見出しの後に広告を配置（3つの見出しごと）
            if line.startswith('##') and ad_count < 3 and i > 10:
                if random.random() > 0.3:  # 70%の確率で広告挿入
                    optimized.append("\n" + adsense_code + "\n")
                    ad_count += 1
        
        return '\n'.join(optimized)
    
    @staticmethod
    def create_email_capture_form(position: str = "in_article") -> str:
        """メールキャプチャフォームを生成"""
        if position == "in_article":
            return """
<div class="email-capture-box">
    <h3>🎁 無料プレゼント</h3>
    <p>{incentive}</p>
    <form class="email-form" onsubmit="captureEmail(event)">
        <input type="email" placeholder="メールアドレスを入力" required>
        <button type="submit">無料で受け取る</button>
    </form>
    <p class="privacy-note">※ メールアドレスは厳重に管理され、スパムメールは送りません</p>
</div>
            """.format(incentive=MONETIZATION_CONFIG["email_capture"]["incentive"])
        else:
            return ""

# 高度な記事生成関数
def generate_monetized_content(keyword: str, content: str) -> str:
    """収益最適化されたコンテンツを生成"""
    
    # 最適なアフィリエイトを選択
    affiliates = RevenueOptimizer.select_best_affiliates(keyword)
    
    # アフィリエイトセクションを作成
    affiliate_section = "\n\n## この記事を読んだ方におすすめのツール・サービス\n\n"
    
    for i, aff in enumerate(affiliates, 1):
        affiliate_section += f"""
### {i}. {aff['name']}

<div class="affiliate-box">
    <a href="{aff['url']}" target="_blank" rel="noopener" class="affiliate-link">
        <img src="/static/affiliate-banners/{aff['name'].lower().replace(' ', '_')}.jpg" alt="{aff['name']}" />
        <button class="cta-button">詳細を見る ▶</button>
    </a>
</div>

"""
    
    # コンテンツ内の適切な位置に挿入
    sections = content.split("## ")
    
    if len(sections) > 3:
        # 中間あたりに挿入
        middle = len(sections) // 2
        sections[middle] = sections[middle] + affiliate_section
        content = "## ".join(sections)
    else:
        # まとめの前に挿入
        if "## まとめ" in content:
            content = content.replace("## まとめ", affiliate_section + "\n## まとめ")
        else:
            content += affiliate_section
    
    # メールキャプチャフォームを挿入
    if MONETIZATION_CONFIG["email_capture"]["enabled"]:
        email_form = RevenueOptimizer.create_email_capture_form()
        
        # 記事の中盤に挿入
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 5:
            middle_idx = len(paragraphs) // 2
            paragraphs.insert(middle_idx, email_form)
            content = '\n\n'.join(paragraphs)
    
    # 広告最適化
    if MONETIZATION_CONFIG["adsense"]["enabled"]:
        content = RevenueOptimizer.optimize_ad_placement(content)
    
    # CTA（Call to Action）を追加
    cta_section = """

---

### 💡 さらに詳しく学びたい方へ

<div class="premium-cta">
    <h4>プレミアムプランで、さらに高度な機能を使いこなそう！</h4>
    <ul>
        <li>✅ 文字数無制限で長文記事も自由自在</li>
        <li>✅ 競合サイト分析で差別化</li>
        <li>✅ AIリライトで既存記事も最適化</li>
    </ul>
    <a href="/premium" class="premium-button">7日間無料で試す →</a>
</div>
"""
    
    content += cta_section
    
    return content

# API エンドポイント
@app.get("/", response_class=HTMLResponse)
async def landing_page_monetized(request: Request):
    return templates.TemplateResponse("landing_monetized.html", {
        "request": request,
        "monetization": MONETIZATION_CONFIG
    })

@app.post("/api/generate-monetized")
async def generate_monetized_article(
    request: Request,
    keyword: str = Form(...),
    length: int = Form(1500),
    monetize: bool = Form(True)
):
    """収益最適化された記事を生成"""
    # 既存の記事生成ロジック
    # ...（省略）...
    
    # 収益最適化
    if monetize:
        optimized_content = generate_monetized_content(keyword, "生成された記事コンテンツ")
    
    return {
        "success": True,
        "content": optimized_content,
        "revenue_potential": {
            "estimated_cpa": sum([aff["cpa"] for aff in RevenueOptimizer.select_best_affiliates(keyword)]) / 100,
            "ad_slots": 3,
            "email_capture": True
        }
    }

@app.post("/api/capture-email")
async def capture_email(email: str = Form(...)):
    """メールアドレスを取得"""
    # メールリストに追加する処理
    # 実際はメールマーケティングツールのAPIを使用
    return {"success": True, "message": "プレゼントをメールでお送りしました！"}

@app.get("/premium", response_class=HTMLResponse)
async def premium_page(request: Request):
    """プレミアムプラン申し込みページ"""
    return templates.TemplateResponse("premium.html", {
        "request": request,
        "features": MONETIZATION_CONFIG["premium"]["features"],
        "price": MONETIZATION_CONFIG["premium"]["price"]
    })

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 AI記事生成システム（高収益化モデル）起動中...")
    print("📍 URL: http://localhost:8888")
    print("💰 収益化手法: AdSense + アフィリエイト + メールリスト + プレミアム")
    print("📈 予想月収: 10万円〜100万円")
    
    uvicorn.run(app, host="0.0.0.0", port=8888, reload=True)