# 自動投稿システムのセットアップガイド

## 🚀 概要
このシステムは、AIが毎日自動的にトレンド記事を生成し、GitHub Pagesのnote風サイトに投稿します。

## 📋 必要な準備

### 1. GitHub Personal Access Tokenの取得
1. GitHubにログイン
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. 「Generate new token」をクリック
4. 以下の権限を選択：
   - `repo` (Full control of private repositories)
5. トークンをコピーして保存

### 2. OpenAI APIキーの取得
1. [OpenAI](https://platform.openai.com/)にログイン
2. API keys ページでキーを生成
3. キーをコピーして保存

### 3. 設定ファイルの編集
`config/auto_post_config.json`を編集：
```json
{
  "github": {
    "repository": "daito-iwa/ai-article-generator",
    "token": "YOUR_GITHUB_TOKEN_HERE",
    "branch": "main"
  },
  "openai": {
    "api_key": "YOUR_OPENAI_API_KEY_HERE",
    "model": "gpt-4o-mini",
    "temperature": 0.8
  }
}
```

## 🎯 使い方

### 必要なパッケージのインストール
```bash
pip install pytrends openai requests schedule
```

### 自動投稿システムの起動
```bash
python auto_post_to_github.py
```

### メニューオプション
1. **今すぐ記事を投稿** - テスト投稿を実行
2. **デモ記事を生成（5件）** - デモ用の記事を一括生成
3. **自動投稿スケジューラーを開始** - 毎日定時に自動投稿
4. **設定を確認** - 現在の設定を表示
5. **終了** - プログラムを終了

## ⏰ 投稿スケジュール
デフォルトでは以下の時間に自動投稿されます：
- 09:00 - 朝の投稿
- 14:00 - 昼の投稿
- 19:00 - 夜の投稿

## 🤖 AIペルソナ
システムは5つの異なるペルソナを使い分けます：
- **T.K** - AIエンジニア（技術記事）
- **M.Y** - ライフスタイルブロガー（生活・副業）
- **S.J** - ビジネスコンサルタント（ビジネス戦略）
- **A.M** - クリエイティブデザイナー（デザイン）
- **K.H** - 金融アナリスト（投資・経済）

## 📊 記事データの管理
- 記事データは`data/articles.json`に保存されます
- GitHub Actionsまたは手動でコミット＆プッシュが必要です
- 最大100記事まで保持（古い記事は自動削除）

## 🔧 トラブルシューティング

### APIキーエラー
- 設定ファイルのAPIキーが正しいか確認
- OpenAIの残高があるか確認

### GitHub更新エラー
- Personal Access Tokenの権限を確認
- リポジトリ名が正しいか確認

### トレンド取得エラー
- インターネット接続を確認
- フォールバックトピックが使用されます

## 💡 カスタマイズ

### 投稿時間の変更
`config/auto_post_config.json`の`post_times`を編集：
```json
"post_times": ["08:00", "12:00", "18:00", "22:00"]
```

### カテゴリの追加
`categories`配列に新しいカテゴリを追加可能

### ペルソナの追加
`auto_post_to_github.py`の`personas`辞書に新しいペルソナを追加