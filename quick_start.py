#!/usr/bin/env python3
"""
最速で記事を生成するスクリプト
APIキー設定不要でテスト可能
"""

import os
import json
from datetime import datetime

def quick_generate_article(keyword):
    """簡易記事生成（デモ用）"""
    
    title = f"{keyword}について知っておくべき10のポイント"
    
    content = f"""# {title}

## はじめに

{keyword}について、初心者の方にも分かりやすく解説します。この記事を読むことで、{keyword}の基本から応用まで幅広く理解できるようになります。

## {keyword}とは？

{keyword}は、現代において非常に重要な概念です。多くの人が関心を持っており、正しい知識を身につけることが大切です。

## {keyword}の3つのメリット

### 1. 効率性の向上
{keyword}を活用することで、作業効率が大幅に向上します。従来の方法と比較して、時間を50%以上短縮できるケースもあります。

### 2. コスト削減
適切な{keyword}の導入により、長期的なコスト削減が可能です。初期投資は必要ですが、ROIは非常に高いと言えるでしょう。

### 3. 品質向上
{keyword}を取り入れることで、成果物の品質が向上します。これにより、顧客満足度も高まります。

## {keyword}の実践方法

### ステップ1: 計画立案
まずは明確な目標を設定しましょう。{keyword}を導入する目的を明確にすることが重要です。

### ステップ2: 実行
計画に基づいて実行します。小さく始めて、徐々に規模を拡大していくことをおすすめします。

### ステップ3: 評価と改善
結果を評価し、改善点を見つけます。PDCAサイクルを回すことで、継続的な改善が可能です。

## よくある質問（FAQ）

### Q1: {keyword}を始めるのに必要な費用は？
A: 初期費用は規模によりますが、小規模から始めることも可能です。

### Q2: {keyword}の学習期間はどのくらい？
A: 基本的な内容であれば1-2週間、応用まで含めると1-3ヶ月程度が目安です。

### Q3: {keyword}に失敗するリスクは？
A: 適切な計画と実行により、リスクは最小限に抑えられます。

## おすすめのツール・サービス

### 1. エックスサーバー
{keyword}を活用したウェブサイト運営には、高速で安定したサーバーが必要です。エックスサーバーは国内シェアNo.1の信頼性があります。
[→ エックスサーバーの詳細はこちら](https://example.com/xserver)

### 2. ConoHa WING
表示速度を重視する方には、ConoHa WINGがおすすめです。初心者にも使いやすい管理画面が特徴です。
[→ ConoHa WINGの詳細はこちら](https://example.com/conoha)

### 3. ラッコキーワード
{keyword}に関連するキーワードリサーチには、ラッコキーワードが便利です。
[→ ラッコキーワードの詳細はこちら](https://example.com/rakko)

## 成功事例

### 事例1: A社の場合
A社は{keyword}を導入することで、売上を前年比150%増加させました。

### 事例2: B氏の場合
個人ブロガーのB氏は、{keyword}を活用して月間10万PVを達成しました。

## まとめ

{keyword}について、基本から実践方法まで解説しました。重要なポイントは以下の通りです：

1. 明確な目標設定
2. 段階的な実行
3. 継続的な改善

{keyword}を正しく理解し、実践することで、大きな成果を得ることができるでしょう。

---

**関連記事:**
- {keyword}の最新トレンド2024
- {keyword}で成功するための5つのコツ
- {keyword}の失敗例から学ぶ教訓

**メタ情報:**
- 文字数: 約1,500文字
- 読了時間: 約5分
- 最終更新: {datetime.now().strftime('%Y年%m月%d日')}
"""
    
    return title, content

def save_article(title, content, keyword):
    """記事を保存"""
    # 出力ディレクトリ作成
    os.makedirs('output/quick_generated', exist_ok=True)
    
    # ファイル名作成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_keyword = keyword.replace(' ', '_')[:20]
    filename = f'output/quick_generated/{timestamp}_{safe_keyword}.md'
    
    # 保存
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 記事を保存しました: {filename}")
    return filename

def main():
    """メイン処理"""
    print("🚀 AI記事生成システム - クイックスタート")
    print("=" * 50)
    
    # APIキー確認（警告のみ）
    if not os.path.exists('config/api_keys.json'):
        print("⚠️  注意: APIキーが設定されていません")
        print("   実際のAI生成にはconfig/api_keys.jsonの設定が必要です")
        print("   今回はデモ版の記事を生成します")
        print()
    
    # キーワード入力
    print("記事を生成したいキーワードを入力してください")
    print("例: AI ブログ 収益化")
    keyword = input("キーワード: ").strip()
    
    if not keyword:
        keyword = "AI 記事 自動生成"
        print(f"→ デフォルトキーワード「{keyword}」で生成します")
    
    print()
    print("記事を生成中...")
    
    # 記事生成
    title, content = quick_generate_article(keyword)
    
    # 保存
    filename = save_article(title, content, keyword)
    
    # 結果表示
    print()
    print("=" * 50)
    print(f"タイトル: {title}")
    print(f"文字数: {len(content)}文字")
    print()
    print("記事の冒頭:")
    print("-" * 30)
    print(content[:300] + "...")
    print("-" * 30)
    print()
    
    # 次のアクション
    print("📝 次のステップ:")
    print("1. 生成された記事を確認: " + filename)
    print("2. APIキーを設定: config/api_keys.json")
    print("3. 本格的な自動生成: python3 auto_article_generator.py")
    
    # ブラウザで開くか確認
    if input("\nブラウザで記事を開きますか？ (y/n): ").lower() == 'y':
        import webbrowser
        file_url = f'file://{os.path.abspath(filename)}'
        webbrowser.open(file_url)

if __name__ == "__main__":
    main()