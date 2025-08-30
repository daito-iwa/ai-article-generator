# AI記事自動生成システム

## プロジェクト概要
このプロジェクトは、SEOに最適化された記事を半自動で生成し、WordPressなどのCMSに自動投稿するシステムです。

## 主要機能
1. トレンドキーワードの自動収集
2. AIを使った記事生成
3. SEO最適化
4. 自動投稿

## 技術スタック
- Python 3.9+
- OpenAI API / Anthropic API
- WordPress REST API
- Google Trends API
- Schedule (定期実行)

## セットアップ手順

### 1. 環境構築
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. API設定
`config/api_keys.json`に以下を設定：
```json
{
  "openai_api_key": "your-key",
  "anthropic_api_key": "your-key",
  "google_api_key": "your-key",
  "wordpress": {
    "url": "https://your-site.com",
    "username": "your-username",
    "password": "application-password"
  }
}
```

## 使用方法

### 単発記事生成
```bash
python src/article_generator.py --keyword "キーワード" --length 1500
```

### 定期実行設定
```bash
python scheduler.py --interval daily --time 09:00
```

## ディレクトリ構造の説明

- `src/keyword_research.py`: トレンドキーワード収集
- `src/article_generator.py`: AI記事生成メイン処理
- `src/seo_optimizer.py`: SEO最適化処理
- `src/publisher.py`: CMS投稿処理
- `templates/`: 記事テンプレート
- `output/`: 生成された記事の保存先

## カスタマイズポイント

### 記事テンプレート
`templates/article_template.md`を編集して記事の構造をカスタマイズ

### SEO設定
`config/settings.json`で以下を調整：
- メタディスクリプション長
- キーワード密度
- 見出し構造

## トラブルシューティング

### APIレート制限
- リトライ機能実装済み
- `config/settings.json`で待機時間調整可能

### 記事品質
- `temperature`パラメータで創造性を調整
- 複数回生成して最良のものを選択するオプション

## 注意事項
- 生成された記事は必ず人間がレビューすること
- 著作権・事実確認は人間が責任を持つ
- API利用料金に注意

# Claude Code 実装プロンプト集

## 初期セットアップ用プロンプト

```
AI記事自動生成システムを作成してください。

要件：
1. Pythonで実装
2. Google Trendsからトレンドキーワードを取得
3. OpenAI APIを使って記事を生成
4. SEO最適化（メタタグ、キーワード密度調整）
5. WordPress REST APIで自動投稿
6. エラーハンドリングとログ機能

プロジェクト構造を作成し、必要なファイルをすべて生成してください。
```

## 機能別プロンプト

### 1. キーワードリサーチ機能
```
pytrends を使用して、指定カテゴリのトレンドキーワードを取得する機能を実装してください。
- 日本のトレンドを取得
- 関連キーワードも収集
- 競合性の低いロングテールキーワードを優先
- CSVファイルに保存
```

### 2. 記事生成機能
```
OpenAI APIを使用した記事生成機能を実装してください。

要件：
- 1500-2000文字の記事生成
- SEOを意識した構造（H2, H3タグ使用）
- キーワードを自然に含める（2-3%の密度）
- 導入、本文、まとめの構成
- メタディスクリプション自動生成
- 記事の独自性チェック機能
```

### 3. SEO最適化
```
生成された記事をSEO最適化する機能を追加してください：
- タイトルタグ最適化（60文字以内）
- メタディスクリプション（120-160文字）
- 見出し構造の最適化
- 内部リンク提案
- 画像のalt属性生成
- 構造化データ（JSON-LD）の追加
```

### 4. 自動投稿機能
```
WordPress REST APIを使った自動投稿機能を実装してください：
- 下書き/公開の選択
- カテゴリー/タグの自動設定
- アイキャッチ画像の設定（Unsplash API連携）
- 投稿スケジュール機能
- 投稿結果のログ保存
```

### 5. モニタリング機能
```
システムの監視・分析機能を追加してください：
- 生成記事数の統計
- API使用量の追跡
- エラー率の監視
- 記事パフォーマンス追跡（Google Analytics連携）
- コスト計算機能
```

## 高度な機能の実装

### リライト機能
```
既存記事を改善するリライト機能を実装してください：
- 古い記事の自動検出
- 最新情報への更新
- SEOスコアの改善
- A/Bテスト用バリエーション生成
```

### 多言語対応
```
記事を複数言語で生成する機能を追加してください：
- 日本語→英語/中国語/韓国語
- 各言語でのSEO最適化
- hreflangタグの自動生成
```

## デバッグ・改善用プロンプト

### パフォーマンス改善
```
現在のコードのパフォーマンスを改善してください：
- 非同期処理の実装
- キャッシュ機能の追加
- バッチ処理の最適化
- メモリ使用量の削減
```

### エラーハンドリング強化
```
エラーハンドリングを強化してください：
- API制限への対応
- ネットワークエラーのリトライ
- 不正なレスポンスの処理
- ユーザーフレンドリーなエラーメッセージ
```