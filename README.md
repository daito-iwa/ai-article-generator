# AI記事自動生成システム

SEOに最適化された記事を自動生成し、WordPressなどのCMSに投稿するPythonシステムです。

## 主要機能

- **キーワードリサーチ**: Google Trendsから最新のトレンドキーワードを自動取得
- **AI記事生成**: OpenAI GPT-4やAnthropic Claudeを使った高品質な記事生成
- **SEO最適化**: タイトル、メタディスクリプション、見出し構造の自動最適化
- **自動投稿**: WordPress REST APIを使った自動投稿機能
- **品質分析**: 記事のSEOスコア、読みやすさスコアの自動評価

## システム要件

- Python 3.9以上
- 必要なAPIキー:
  - OpenAI API キー（記事生成用）
  - Anthropic API キー（オプション）
  - Unsplash Access Key（画像取得用、オプション）
  - WordPress サイトの管理者アカウント

## インストール

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd ai-article-generator
```

### 2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 設定ファイルの編集
`config/api_keys.json`を編集して、各APIキーを設定してください：

```json
{
  "openai_api_key": "sk-your-openai-key",
  "anthropic_api_key": "your-anthropic-key",
  "unsplash_access_key": "your-unsplash-key",
  "wordpress": {
    "url": "https://your-wordpress-site.com",
    "username": "your-username",
    "password": "your-application-password"
  }
}
```

## 使用方法

### コマンドライン使用例

#### 1. キーワードリサーチ
```bash
python main.py research --limit 10
```

#### 2. 記事生成（ローカル保存のみ）
```bash
python main.py generate "Python プログラミング" --length 2000
```

#### 3. 記事生成 + WordPress投稿
```bash
python main.py publish "AI 機械学習" --status draft
```

#### 4. 複数記事の一括生成
```bash
python main.py batch "Python基礎" "Web開発" "データ分析" --status draft
```

#### 5. SEO分析
```bash
python main.py analyze "記事タイトル" content.md "ターゲットキーワード"
```

#### 6. システムテスト実行
```bash
python main.py test
```

### Python スクリプトからの使用

```python
from src.keyword_research import KeywordResearcher
from src.article_generator import ArticleGenerator, ArticleConfig
from src.seo_optimizer import SEOOptimizer

# キーワードリサーチ
researcher = KeywordResearcher()
keywords = researcher.get_trending_keywords(limit=5)

# 記事生成
config = ArticleConfig(min_length=1500, max_length=2000)
generator = ArticleGenerator(openai_api_key="your-key", config=config)
article = generator.generate_article("Python プログラミング")

# SEO最適化
optimizer = SEOOptimizer()
analysis = optimizer.analyze_article(
    article.title, 
    article.content, 
    article.meta_description, 
    "Python プログラミング"
)
```

## ディレクトリ構造

```
ai-article-generator/
├── src/                    # メインソースコード
│   ├── keyword_research.py # キーワードリサーチ
│   ├── article_generator.py# AI記事生成
│   ├── seo_optimizer.py    # SEO最適化
│   └── publisher.py        # 自動投稿
├── config/                 # 設定ファイル
│   ├── api_keys.json      # APIキー設定
│   └── settings.json      # システム設定
├── templates/             # テンプレート
│   ├── article_template.md# 記事テンプレート
│   └── seo_template.json  # SEOテンプレート
├── output/                # 出力ファイル
│   └── articles/         # 生成された記事
├── logs/                  # ログファイル
├── main.py               # メインエントリーポイント
├── test_system.py        # システムテスト
├── claude.md             # Claude Code用指示書
└── README.md            # このファイル
```

## 設定カスタマイズ

### 記事生成設定（config/settings.json）

```json
{
  "article_generation": {
    "default_min_length": 1500,
    "default_max_length": 2500,
    "target_keyword_density": 2.5,
    "default_model": "gpt-4",
    "temperature": 0.7,
    "language": "ja",
    "tone": "friendly"
  }
}
```

### SEO最適化設定

```json
{
  "seo_optimization": {
    "title_max_length": 60,
    "meta_description_max_length": 160,
    "optimal_keyword_density_min": 1.0,
    "optimal_keyword_density_max": 3.0,
    "min_headings": 3,
    "max_headings": 6
  }
}
```

## 機能詳細

### キーワードリサーチ機能

- Google Trendsから日本のトレンドキーワードを取得
- 関連キーワードと急上昇キーワードを収集
- 検索ボリュームと競合性の推定
- CSV/JSON形式での結果出力

### 記事生成機能

- OpenAI GPT-4またはAnthropic Claudeを使用
- SEOを意識した記事構造（導入→本文→まとめ）
- 自然なキーワード配置（1-3%の密度）
- メタディスクリプション自動生成
- 品質メトリクスの計算

### SEO最適化機能

- タイトルの長さと構造の最適化
- メタディスクリプションの最適化
- 見出し構造の分析と改善
- キーワード密度の調整
- 読みやすさスコアの計算
- 構造化データ（JSON-LD）の生成

### 自動投稿機能

- WordPress REST APIを使った投稿
- 下書き/公開の選択
- カテゴリーとタグの自動設定
- アイキャッチ画像の自動取得（Unsplash連携）
- 投稿結果のログ記録

## トラブルシューティング

### よくある問題

#### 1. API接続エラー
```
ConnectionError: WordPress APIへの接続に失敗しました
```
**解決方法**: 
- WordPressサイトのURLが正しいことを確認
- アプリケーションパスワードが有効であることを確認
- REST APIが有効になっていることを確認

#### 2. キーワード取得エラー
```
キーワード取得エラー: HTTPSConnectionPool
```
**解決方法**: 
- ネットワーク接続を確認
- VPNを使用している場合は無効にして試行
- API制限に達していないか確認

#### 3. 記事生成エラー
```
OpenAI API エラー: Rate limit exceeded
```
**解決方法**: 
- APIキーの使用量制限を確認
- `settings.json`の`rate_limiting`設定を調整
- 時間をおいて再実行

### ログの確認

システムのログは`logs/`ディレクトリに保存されます：
- `main.log`: メイン処理のログ
- `test_system.log`: テスト実行のログ
- `generator.log`: 記事生成のログ

## 開発・貢献

### テストの実行
```bash
python main.py test
```

### 新機能の追加
1. `src/`ディレクトリに新しいモジュールを追加
2. `main.py`にコマンドを追加
3. テストを`test_system.py`に追加

### コード品質の確保
- PEP 8に準拠したコーディング
- 適切なエラーハンドリング
- ログ出力の実装
- ドキュメント文字列の記述

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

1. **コンテンツの品質管理**: 生成された記事は必ず人間がレビューしてから公開してください
2. **著作権の遵守**: 生成されたコンテンツの著作権と事実確認は利用者の責任です
3. **API利用料金**: OpenAI APIなどの利用料金にご注意ください
4. **レート制限**: 各APIのレート制限を遵守してください

## サポート

問題や質問がある場合は、以下の方法でサポートを受けられます：
- GitHubのIssueを作成
- ドキュメントの確認
- ログファイルの内容を確認

---

**最終更新**: 2024年
**バージョン**: 1.0.0