#!/usr/bin/env python3
"""
Ollama（オーラマ）を使った完全無料AI記事生成システム
ローカルLLMで高品質な記事を生成
"""

import json
import os
import sys
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import subprocess

# srcディレクトリをパスに追加
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class OllamaArticleGenerator:
    """Ollamaを使用した記事生成クラス"""
    
    def __init__(self, model: str = "llama3.2"):
        """
        初期化
        
        Args:
            model: 使用するモデル（llama3.2, mistral, gemma2等）
        """
        self.model = model
        self.base_url = "http://localhost:11434"
        self.check_ollama_status()
    
    def check_ollama_status(self):
        """Ollamaの状態を確認"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"✅ Ollama起動中 - 利用可能モデル: {len(models)}個")
                if not any(m['name'].startswith(self.model) for m in models):
                    print(f"⚠️  {self.model}モデルが見つかりません")
                    print(f"   実行: ollama pull {self.model}")
            else:
                print("❌ Ollamaが起動していません")
                print("   実行: ollama serve")
        except:
            print("❌ Ollamaに接続できません")
            print("   インストール: https://ollama.ai/download")
    
    def generate_article(self, keyword: str, 
                        length: int = 1500,
                        include_affiliate: bool = True) -> Dict:
        """
        記事を生成
        
        Args:
            keyword: キーワード
            length: 文字数目安
            include_affiliate: アフィリエイトリンクを含めるか
            
        Returns:
            生成された記事データ
        """
        print(f"🤖 Ollamaで記事生成中: {keyword}")
        
        # プロンプト作成
        prompt = self._create_prompt(keyword, length, include_affiliate)
        
        try:
            # Ollama APIを呼び出し
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 4000
                    }
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')
                
                # タイトルとコンテンツを分離
                title = self._extract_title(content, keyword)
                
                # アフィリエイトリンク追加
                if include_affiliate:
                    content = self._add_affiliate_links(content, keyword)
                
                return {
                    'success': True,
                    'title': title,
                    'content': content,
                    'word_count': len(content),
                    'model': self.model,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'API Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_prompt(self, keyword: str, length: int, include_affiliate: bool) -> str:
        """プロンプトを作成"""
        affiliate_instruction = """
記事の適切な箇所に以下のサービスを自然に紹介してください：
- エックスサーバー（レンタルサーバー）
- ConoHa WING（レンタルサーバー）
- ラッコキーワード（SEOツール）
""" if include_affiliate else ""
        
        prompt = f"""あなたはSEOに精通したプロのブログライターです。
以下の条件で「{keyword}」についての記事を日本語で作成してください：

【記事要件】
- 文字数: {length}文字程度
- 読者層: 初心者〜中級者
- トーン: 親しみやすく分かりやすい
- 構成: 導入→本文（3-5セクション）→まとめ

【SEO要件】
- タイトルは32文字以内で魅力的に
- 見出しは階層構造（##, ###）で整理
- キーワード「{keyword}」を自然に含める
- 読者の検索意図に答える内容

【必須要素】
1. 魅力的なタイトル（#で始める）
2. 導入文で記事の概要を説明
3. 具体例や数値を含める
4. よくある質問（FAQ）セクション
5. まとめセクション

{affiliate_instruction}

【出力形式】
マークダウン形式で出力してください。

では、記事を作成してください：
"""
        return prompt
    
    def _extract_title(self, content: str, keyword: str) -> str:
        """タイトルを抽出"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return f"{keyword}について詳しく解説"
    
    def _add_affiliate_links(self, content: str, keyword: str) -> str:
        """アフィリエイトリンクを追加"""
        if "エックスサーバー" not in content:
            affiliate_section = """

## おすすめのツール・サービス

記事作成やブログ運営に役立つサービスを紹介します。

### 🖥️ エックスサーバー
国内シェアNo.1の高速レンタルサーバー。安定性が高く、初心者にも使いやすい管理画面が特徴です。
- 月額990円〜
- 無料SSL対応
- 自動バックアップ機能
[→ エックスサーバーの詳細を見る](https://px.a8.net/svt/ejp?a8mat=YOUR_ID)

### 🚀 ConoHa WING
表示速度国内No.1のレンタルサーバー。WordPressの高速化に特化しています。
- 月額643円〜
- WordPressかんたんセットアップ
- 独自ドメイン永久無料
[→ ConoHa WINGの詳細を見る](https://px.a8.net/svt/ejp?a8mat=YOUR_ID)

### 🔍 ラッコキーワード
無料で使えるキーワードリサーチツール。SEO対策に必須です。
- 関連キーワード取得
- 検索ボリューム確認
- 競合分析機能
[→ ラッコキーワードを使ってみる](https://related-keywords.com/)
"""
            if "## まとめ" in content:
                content = content.replace("## まとめ", affiliate_section + "\n## まとめ")
            else:
                content += affiliate_section
        
        return content
    
    def save_article(self, article_data: Dict, keyword: str) -> str:
        """記事を保存"""
        if not article_data['success']:
            return None
        
        # 出力ディレクトリ作成
        os.makedirs('output/ollama_generated', exist_ok=True)
        
        # ファイル名作成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_keyword = keyword.replace(' ', '_')[:30]
        filename = f'output/ollama_generated/{timestamp}_{safe_keyword}.md'
        
        # 保存
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(article_data['content'])
        
        # メタデータも保存
        meta_filename = filename.replace('.md', '_meta.json')
        with open(meta_filename, 'w', encoding='utf-8') as f:
            json.dump({
                'title': article_data['title'],
                'keyword': keyword,
                'word_count': article_data['word_count'],
                'model': article_data['model'],
                'generated_at': article_data['generated_at']
            }, f, ensure_ascii=False, indent=2)
        
        return filename

def install_ollama():
    """Ollamaのインストール方法を表示"""
    print("""
🚀 Ollamaのインストール方法

1. macOSの場合:
   brew install ollama
   または
   https://ollama.ai/download からダウンロード

2. Ollamaを起動:
   ollama serve

3. モデルをダウンロード（別ターミナルで）:
   ollama pull llama3.2      # 最新の小型モデル（推奨）
   ollama pull mistral       # 高速で高品質
   ollama pull gemma2        # Google製の高性能モデル

4. このスクリプトを再実行:
   python3 ollama_article_generator.py
""")

def main():
    """メイン処理"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ollamaで記事を自動生成')
    parser.add_argument('--keyword', type=str, help='記事のキーワード')
    parser.add_argument('--model', type=str, default='llama3.2', help='使用するモデル')
    parser.add_argument('--length', type=int, default=1500, help='文字数目安')
    parser.add_argument('--count', type=int, default=1, help='生成する記事数')
    parser.add_argument('--no-affiliate', action='store_true', help='アフィリエイトリンクを含めない')
    
    args = parser.parse_args()
    
    print("🤖 Ollama AI記事生成システム")
    print("=" * 50)
    
    # Ollama状態確認
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            raise Exception("Ollama not running")
    except:
        print("❌ Ollamaが起動していません")
        install_ollama()
        return
    
    # 生成器初期化
    generator = OllamaArticleGenerator(model=args.model)
    
    # キーワード取得
    if args.keyword:
        keywords = [args.keyword]
    else:
        # デフォルトキーワード
        keywords = [
            "AI ブログ 自動生成",
            "ChatGPT 活用法",
            "プログラミング 独学",
            "副業 在宅 稼ぎ方",
            "投資 初心者 始め方"
        ][:args.count]
    
    # 記事生成
    for i, keyword in enumerate(keywords, 1):
        print(f"\n[{i}/{len(keywords)}] 記事生成: {keyword}")
        
        article = generator.generate_article(
            keyword=keyword,
            length=args.length,
            include_affiliate=not args.no_affiliate
        )
        
        if article['success']:
            filename = generator.save_article(article, keyword)
            print(f"✅ 保存完了: {filename}")
            print(f"   文字数: {article['word_count']}文字")
        else:
            print(f"❌ 生成失敗: {article['error']}")
        
        # API負荷軽減
        if i < len(keywords):
            time.sleep(5)
    
    print("\n✨ 処理完了！")
    print(f"📁 生成記事: output/ollama_generated/")

if __name__ == "__main__":
    main()